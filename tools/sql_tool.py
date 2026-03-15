"""
SQL Tool — Natural Language → SQL → DuckDB Results
Warner Bros. Singapore Marketing Analytics Agent

How it works:
  1. User asks a plain English question
  2. Claude converts it to SQL (knows the full schema)
  3. SQL runs against DuckDB
  4. Clean results returned
"""

import os
import re
import duckdb
import anthropic
from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(_env_path, override=True)

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/marketing_analytics.duckdb")

# ─────────────────────────────────────────────
# Full schema context — Claude needs this to write correct SQL
# ─────────────────────────────────────────────
SCHEMA_CONTEXT = """
You are a SQL expert for Warner Bros. Singapore's marketing analytics database.
Currency is SGD. Today's date is 2026-03-15.

DATABASE SCHEMA:

TABLE: dim_platform
  platform_id      INTEGER  (1=Meta, 2=Google, 3=TikTok, 4=YouTube)
  platform_name    VARCHAR
  platform_type    VARCHAR  (Social, Search, Video)
  avg_cpm_baseline DOUBLE

TABLE: dim_campaign
  campaign_id   INTEGER
  campaign_name VARCHAR
  business_line VARCHAR  (Theatrical, Max Streaming, Home Entertainment, WB Games, Licensing & Merch)
  objective     VARCHAR  (Awareness, Consideration, Conversion, Retention)
  platform_id   INTEGER
  roas_target   DOUBLE
  daily_budget  DOUBLE   (SGD)
  status        VARCHAR  (Active, Paused)

TABLE: dim_ad_set
  ad_set_id    INTEGER
  campaign_id  INTEGER
  ad_set_name  VARCHAR
  audience_type VARCHAR
  age_range    VARCHAR
  gender       VARCHAR
  daily_budget DOUBLE   (SGD)

TABLE: dim_creative
  creative_id   INTEGER
  campaign_id   INTEGER
  creative_name VARCHAR
  format        VARCHAR  (Video 15s, Video 30s, Static Image, Carousel, Story, Reel, YouTube Pre-roll)
  style         VARCHAR
  business_line VARCHAR
  is_video      INTEGER  (1=yes, 0=no)

TABLE: fact_daily_performance  [main fact table — 112K rows]
  row_id        INTEGER
  date          VARCHAR  (format: 'YYYY-MM-DD') — ALWAYS cast as: CAST(date AS DATE)
  campaign_id   INTEGER
  ad_set_id     INTEGER
  creative_id   INTEGER
  platform_id   INTEGER
  business_line VARCHAR
  objective     VARCHAR
  impressions   INTEGER
  clicks        INTEGER
  conversions   INTEGER
  spend         DOUBLE   (SGD)
  revenue       DOUBLE   (SGD)
  roas          DOUBLE   (revenue / spend)
  cpm           DOUBLE   (cost per 1000 impressions, SGD)
  ctr           DOUBLE   (click-through rate as percentage, e.g. 2.1 = 2.1%)
  cvr           DOUBLE   (conversion rate as percentage)
  frequency     DOUBLE   (avg times an individual saw the ad)
  day_num       INTEGER  (0=oldest day, 89=most recent day)

KEY BUSINESS RULES:
- "This month" = March 2026 → use: date LIKE '2026-03-%'
- "Last 7 days" = 2026-03-08 to 2026-03-14 → use: date >= '2026-03-08'
- "Last 30 days" = 2026-02-13 to 2026-03-14 → use: date >= '2026-02-13'
- "MTD" = March 2026
- ROAS targets: Theatrical=3.5, Max Streaming=4.0, Home Entertainment=3.0, WB Games=3.5, Licensing & Merch=2.5
- Always use CAST(date AS DATE) when comparing dates
- Always ROUND monetary values to 2 decimal places
- Always format spend/revenue with SGD prefix in output

IMPORTANT SQL RULES:
- date column is VARCHAR, always cast: CAST(date AS DATE) >= CAST('2026-02-13' AS DATE)
  OR use string comparison: date >= '2026-02-13' (works for YYYY-MM-DD strings)
- Never use CURRENT_DATE — use literal dates based on today = 2026-03-15
- For platform joins: JOIN dim_platform p ON f.platform_id = p.platform_id
- NEVER put descriptive string labels in SELECT (e.g. SELECT 'Some label' AS ...) — just use real columns
- NEVER write multiple queries or UNION ALL blocks with string labels
- NEVER use ROLLUP or GROUPING SETS
- Write ONE simple SELECT query only — no CTEs unless absolutely required
- String literals in WHERE clauses must always have matching opening AND closing single quotes
- business_line values: 'Theatrical', 'Max Streaming', 'Home Entertainment', 'WB Games', 'Licensing & Merch'
"""


def ask_claude_for_sql(question: str) -> str:
    """Send question to Claude, get back a SQL query."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",   # Fast + cheap for SQL generation
        max_tokens=1024,
        system=SCHEMA_CONTEXT,
        messages=[{
            "role": "user",
            "content": f"""Convert this question to a single DuckDB SQL query.

Question: {question}

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no ```sql blocks
- End with exactly ONE semicolon
- Use table aliases for readability
- LIMIT to 20 rows unless the question asks for totals/aggregations
- Write ONE simple SELECT query — no UNION ALL blocks, no ROLLUP, no string labels in SELECT
- All string literals must have BOTH opening AND closing single quotes
- Never start SELECT with a string literal like SELECT 'some text' AS label
"""
        }]
    )
    return response.content[0].text.strip()


def clean_sql(raw: str) -> str:
    """Strip markdown, fix unterminated quotes, ensure single trailing semicolon."""
    raw = re.sub(r"```sql\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)
    raw = raw.strip()

    # Remove ALL trailing semicolons, then add exactly one
    raw = raw.rstrip(";").rstrip()

    # Fix unterminated string literals: if odd number of single quotes, add closing one
    # This catches cases like WHERE x = 'Max Streaming  (missing closing quote)
    lines = raw.split("\n")
    fixed = []
    for line in lines:
        # Count unescaped single quotes
        quote_count = line.count("'") - line.count("\\'")
        if quote_count % 2 != 0:
            line = line.rstrip() + "'"
        fixed.append(line)
    raw = "\n".join(fixed)

    return raw + ";"


def run_query(sql: str):
    """Execute SQL against DuckDB, return (dataframe, error)."""
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        df  = con.execute(sql).df()
        con.close()
        return df, None
    except Exception as e:
        return None, str(e)


def query(question: str, verbose: bool = True) -> dict:
    """
    Main entry point. Auto-retries once on SQL error with simpler prompt.
    Input : plain English question (str)
    Output: dict with keys: question, sql, data (DataFrame), error
    """
    if verbose:
        print(f"\n{'─'*60}")
        print(f"Question : {question}")

    # Step 1: Generate SQL (with one retry on failure)
    raw_sql = ask_claude_for_sql(question)
    sql     = clean_sql(raw_sql)

    if verbose:
        print(f"SQL      : {sql[:120]}{'...' if len(sql) > 120 else ''}")

    # Step 2: Run query (auto-retry once with simpler prompt on error)
    df, error = run_query(sql)

    if error:
        retry_q  = f"Simple version: {question}. Use only basic SELECT, SUM, AVG, GROUP BY. No ROLLUP, no COALESCE with subqueries."
        raw_sql2 = ask_claude_for_sql(retry_q)
        sql      = clean_sql(raw_sql2)
        df, error = run_query(sql)

    if error:
        if verbose:
            print(f"❌ Error : {error}")
        return {"question": question, "sql": sql, "data": None, "error": error}

    if verbose:
        print(f"Result   : {len(df)} rows returned")
        print(df.to_string(index=False) if len(df) <= 20 else df.head(20).to_string(index=False))

    return {"question": question, "sql": sql, "data": df, "error": None}


# ─────────────────────────────────────────────
# Run 4 sample tests when executed directly
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("SQL Tool Test — Warner Bros. Singapore")
    print("=" * 60)

    test_questions = [
        "What's my total spend across all platforms this month?",
        "Which business line has the highest ROAS in the last 30 days?",
        "Show me the top 5 campaigns by spend this month",
        "Which platform has the lowest CPM?",
    ]

    passed = 0
    for q in test_questions:
        result = query(q)
        if result["error"] is None:
            passed += 1

    print(f"\n{'='*60}")
    print(f"SQL Tool Test: {passed}/{len(test_questions)} passed ✅")
    print(f"{'='*60}")
