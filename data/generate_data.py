"""
HOUR 1 - Data Generation Script
Warner Bros. Singapore — Marketing Analytics Agent
Creates 50K+ rows of realistic marketing data in DuckDB
Market: Singapore | Currency: SGD | Platforms: Meta, Google, TikTok, YouTube
"""

import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

DB_PATH = os.path.join(os.path.dirname(__file__), "marketing_analytics.duckdb")

print("=" * 65)
print("Warner Bros. Singapore — Marketing Analytics Data Generation")
print("=" * 65)

# ─────────────────────────────────────────────
# STEP 1: Connect to DuckDB
# ─────────────────────────────────────────────
con = duckdb.connect(DB_PATH)
print(f"\n✓ Connected to DuckDB at: {DB_PATH}")

# ─────────────────────────────────────────────
# STEP 2: Dimension Tables
# ─────────────────────────────────────────────

# dim_platform (YouTube replaces DV360 — more relevant for WB content)
platforms = pd.DataFrame([
    {"platform_id": 1, "platform_name": "Meta",    "platform_type": "Social",  "avg_cpm_baseline": 10.5},
    {"platform_id": 2, "platform_name": "Google",  "platform_type": "Search",  "avg_cpm_baseline": 15.0},
    {"platform_id": 3, "platform_name": "TikTok",  "platform_type": "Social",  "avg_cpm_baseline": 7.0},
    {"platform_id": 4, "platform_name": "YouTube", "platform_type": "Video",   "avg_cpm_baseline": 9.5},
])
con.execute("DROP TABLE IF EXISTS dim_platform")
con.execute("CREATE TABLE dim_platform AS SELECT * FROM platforms")
print(f"✓ dim_platform: {len(platforms)} rows")

# dim_campaign
# Warner Bros. Singapore business lines
business_lines = [
    "Theatrical",        # Movie releases (Dune, Aquaman, Wonka etc.)
    "Max Streaming",     # HBO Max / Warner Bros. Max subscriptions
    "Home Entertainment",# Digital downloads & Blu-ray
    "WB Games",          # Gaming titles (Mortal Kombat, Hogwarts Legacy)
    "Licensing & Merch", # Brand licensing, merchandise
]

objectives = ["Awareness", "Consideration", "Conversion", "Retention"]

# SGD ROAS targets per business line
roas_targets = {
    "Theatrical":         3.5,
    "Max Streaming":      4.0,
    "Home Entertainment": 3.0,
    "WB Games":           3.5,
    "Licensing & Merch":  2.5,
}

# Singapore-relevant movie/campaign titles for realism
campaign_themes = {
    "Theatrical": [
        "Dune Part Two SG Launch", "Superman 2025 Release",
        "Joker Folie à Deux", "Aquaman SG Premiere", "Wonka Re-Release"
    ],
    "Max Streaming": [
        "Max Subscription Drive Q1", "House of the Dragon S2",
        "The Last of Us S2 Promo", "Max Bundle Offer SG", "HBO Originals Awareness"
    ],
    "Home Entertainment": [
        "4K Ultra HD Catalogue", "Digital Download Promo",
        "Blu-ray New Releases", "Bundle Deal Campaign"
    ],
    "WB Games": [
        "Hogwarts Legacy SG", "Mortal Kombat 1 Launch",
        "MultiVersus Free-to-Play", "WB Games Sale"
    ],
    "Licensing & Merch": [
        "DC Merchandise SG", "Harry Potter Merch Collab",
        "WB Studio Store Launch", "Licensed Apparel Drive"
    ],
}

campaigns = []
campaign_id = 1
for biz in business_lines:
    themes = campaign_themes[biz]
    for theme in themes:
        for platform_id in random.sample([1, 2, 3, 4], k=random.randint(2, 4)):
            obj = random.choice(objectives)
            campaigns.append({
                "campaign_id":   campaign_id,
                "campaign_name": f"{theme} — {['Meta','Google','TikTok','YouTube'][platform_id-1]}",
                "business_line": biz,
                "objective":     obj,
                "platform_id":   platform_id,
                "roas_target":   roas_targets[biz],
                "daily_budget":  random.choice([800, 1200, 1500, 2000, 2500, 3000]),  # SGD
                "status":        random.choices(["Active","Active","Active","Paused"], k=1)[0],
            })
            campaign_id += 1

campaigns_df = pd.DataFrame(campaigns)
con.execute("DROP TABLE IF EXISTS dim_campaign")
con.execute("CREATE TABLE dim_campaign AS SELECT * FROM campaigns_df")
print(f"✓ dim_campaign: {len(campaigns_df)} rows")

# dim_ad_set
audiences = [
    "Lookalike 1% — SG Movie Fans",
    "Lookalike 2-5% — Entertainment",
    "Retargeting — Website Visitors",
    "Interest: Movies & TV Shows",
    "Interest: Gaming",
    "Interest: Streaming Services",
    "Age 18-24 — Gen Z SG",
    "Age 25-34 — Millennials SG",
    "CRM — Existing Subscribers",
    "Broad — Singapore All",
]

ad_sets = []
ad_set_id = 1
for _, camp in campaigns_df.iterrows():
    for _ in range(random.randint(2, 5)):
        ad_sets.append({
            "ad_set_id":    ad_set_id,
            "campaign_id":  int(camp["campaign_id"]),
            "ad_set_name":  f"{camp['business_line']} — {random.choice(audiences)}",
            "audience_type": random.choice(audiences),
            "age_range":    random.choice(["18-24", "25-34", "35-44", "18-34", "25-44"]),
            "gender":       random.choice(["All", "Male", "Female"]),
            "daily_budget": round(camp["daily_budget"] / random.uniform(2, 4), 2),
        })
        ad_set_id += 1

ad_sets_df = pd.DataFrame(ad_sets)
con.execute("DROP TABLE IF EXISTS dim_ad_set")
con.execute("CREATE TABLE dim_ad_set AS SELECT * FROM ad_sets_df")
print(f"✓ dim_ad_set: {len(ad_sets_df)} rows")

# dim_creative
formats = ["Video 15s", "Video 30s", "Static Image", "Carousel", "Story", "Reel", "YouTube Pre-roll"]
styles  = ["Trailer Clip", "Product Showcase", "Testimonial", "Promotional Offer", "Brand Story", "UGC Style"]

creatives = []
creative_id = 1
for _, camp in campaigns_df.iterrows():
    for _ in range(random.randint(3, 7)):
        fmt = random.choice(formats)
        creatives.append({
            "creative_id":   creative_id,
            "campaign_id":   int(camp["campaign_id"]),
            "creative_name": f"{camp['business_line']} | {fmt} — {random.choice(styles)}",
            "format":        fmt,
            "style":         random.choice(styles),
            "business_line": camp["business_line"],
            "is_video":      1 if "Video" in fmt or "Pre-roll" in fmt or "Reel" in fmt else 0,
        })
        creative_id += 1

creatives_df = pd.DataFrame(creatives)
con.execute("DROP TABLE IF EXISTS dim_creative")
con.execute("CREATE TABLE dim_creative AS SELECT * FROM creatives_df")
print(f"✓ dim_creative: {len(creatives_df)} rows")

# ─────────────────────────────────────────────
# STEP 3: Fact Table — 50K+ rows daily performance
# ─────────────────────────────────────────────
print("\n⏳ Generating 50K+ rows of daily performance data...")

END_DATE   = datetime(2026, 3, 14)
START_DATE = END_DATE - timedelta(days=89)  # 90 days
date_range = [START_DATE + timedelta(days=i) for i in range(90)]


def seasonality(date):
    """Singapore seasonality: CNY boost Jan/Feb, GSS in June, year-end Dec"""
    base = 1.0
    # Chinese New Year boost (late Jan - mid Feb)
    if date.month == 1 and date.day >= 20:
        base = 1.35
    elif date.month == 2 and date.day <= 15:
        base = 1.30
    # Valentine's Day bump
    elif date.month == 2 and 12 <= date.day <= 16:
        base *= 1.15
    # March — steady
    elif date.month == 3:
        base = 1.05
    # Weekend dip (Sun-Mon lower engagement for entertainment)
    if date.weekday() == 6:   # Sunday
        base *= 0.90
    elif date.weekday() == 0:  # Monday
        base *= 0.92
    return base


performance_rows = []
row_id = 1

for _, ad_set in ad_sets_df.iterrows():
    camp     = campaigns_df[campaigns_df["campaign_id"] == ad_set["campaign_id"]].iloc[0]
    platform = platforms[platforms["platform_id"] == camp["platform_id"]].iloc[0]

    camp_creatives = creatives_df[creatives_df["campaign_id"] == camp["campaign_id"]]
    if len(camp_creatives) == 0:
        continue

    for _, creative in camp_creatives.iterrows():
        base_cpm    = platform["avg_cpm_baseline"] * random.uniform(0.8, 1.3)
        base_ctr    = random.uniform(0.008, 0.040)
        base_cvr    = random.uniform(0.02, 0.14)
        base_spend  = ad_set["daily_budget"] * random.uniform(0.7, 1.0)
        fatigue_day = random.randint(20, 55)

        for day_num, date in enumerate(date_range):
            if random.random() < 0.08:
                continue

            season  = seasonality(date)
            fatigue = max(0.5, 1.0 - max(0, day_num - fatigue_day) * 0.015)
            cpm     = base_cpm * season * random.uniform(0.92, 1.08)
            ctr     = base_ctr * fatigue * season * random.uniform(0.9, 1.1)
            cvr     = base_cvr * random.uniform(0.85, 1.15)
            spend   = base_spend * season * random.uniform(0.85, 1.15)

            impressions = int((spend / cpm) * 1000)
            clicks      = int(impressions * ctr)
            conversions = int(clicks * cvr)
            # SGD revenue per conversion (ticket ~SGD 15-25, subscription ~SGD 12-20, game ~SGD 40-80)
            revenue_per_conv = {
                "Theatrical":         random.uniform(15, 28),
                "Max Streaming":      random.uniform(10, 22),
                "Home Entertainment": random.uniform(18, 45),
                "WB Games":           random.uniform(30, 85),
                "Licensing & Merch":  random.uniform(25, 120),
            }
            revenue = conversions * revenue_per_conv.get(camp["business_line"], 20)
            roas    = revenue / spend if spend > 0 else 0

            performance_rows.append({
                "row_id":        row_id,
                "date":          date.strftime("%Y-%m-%d"),
                "campaign_id":   int(camp["campaign_id"]),
                "ad_set_id":     int(ad_set["ad_set_id"]),
                "creative_id":   int(creative["creative_id"]),
                "platform_id":   int(camp["platform_id"]),
                "business_line": camp["business_line"],
                "objective":     camp["objective"],
                "impressions":   impressions,
                "clicks":        clicks,
                "conversions":   conversions,
                "spend":         round(spend, 2),
                "revenue":       round(revenue, 2),
                "roas":          round(roas, 2),
                "cpm":           round(cpm, 2),
                "ctr":           round(ctr * 100, 4),
                "cvr":           round(cvr * 100, 4),
                "frequency":     round(random.uniform(1.2, 6.5), 2),
                "day_num":       day_num,
            })
            row_id += 1

fact_df = pd.DataFrame(performance_rows)
con.execute("DROP TABLE IF EXISTS fact_daily_performance")
con.execute("CREATE TABLE fact_daily_performance AS SELECT * FROM fact_df")
print(f"✓ fact_daily_performance: {len(fact_df):,} rows")

# ─────────────────────────────────────────────
# STEP 4: Summary
# ─────────────────────────────────────────────
print("\n" + "=" * 65)
print("DATABASE SUMMARY — Warner Bros. Singapore")
print("=" * 65)
for table in ["dim_platform", "dim_campaign", "dim_ad_set", "dim_creative", "fact_daily_performance"]:
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<30} {count:>8,} rows")

total_spend = con.execute("SELECT ROUND(SUM(spend),2) FROM fact_daily_performance").fetchone()[0]
dates       = con.execute("SELECT MIN(date), MAX(date) FROM fact_daily_performance").fetchone()
print(f"\n  Currency:               SGD")
print(f"  Total simulated spend:  SGD {total_spend:>12,.2f}")
print(f"  Date range:             {dates[0]}  →  {dates[1]}")
print(f"\n✅ Database saved to: {DB_PATH}")
print("=" * 65)

con.close()
