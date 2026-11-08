"""
models/analytics.py
Core analytical engine for the DSS.
Handles: time-series KPIs, revenue optimization, staffing recommendations,
         what-if simulation, and competitor gap analysis.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
import warnings
warnings.filterwarnings("ignore")


# ── Data containers ───────────────────────────────────────────────────────────

@dataclass
class KPISnapshot:
    total_revenue: float
    avg_hourly_revenue: float
    peak_hour: int
    peak_revenue: float
    revenue_lost_post_9pm: float
    conversion_rate: float
    top_category: str
    transactions: int


@dataclass
class StaffingPlan:
    hour: int
    recommended_sales: int
    recommended_cashiers: int
    expected_visitors: int
    utilization_pct: float
    note: str


@dataclass
class WhatIfResult:
    scenario_name: str
    closing_hour: int
    discount_window: tuple
    discount_pct: float
    projected_revenue: float
    revenue_vs_baseline: float
    revenue_change_pct: float
    peak_hours: list
    recommendation: str


# ── Main Analytics Engine ─────────────────────────────────────────────────────

class DSSAnalytics:
    """Model layer: loads data, computes KPIs, runs optimization and simulation."""

    REGULATION_HOUR = 21  # 9 PM Egypt law
    HOURLY_CAPACITY = 25  # max customers comfortable in store simultaneously
    STAFF_CUSTOMER_RATIO = 5  # 1 staff per N customers

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._load_data()
        self._preprocess()

    # ── Loading ───────────────────────────────────────────────────────────────

    def _load_data(self):
        base = self.data_dir
        self.pos = pd.read_csv(f"{base}/pos_transactions.csv", parse_dates=["timestamp", "date"])
        self.traffic = pd.read_csv(f"{base}/foot_traffic.csv", parse_dates=["date"])
        self.staffing = pd.read_csv(f"{base}/staffing.csv", parse_dates=["date"])
        self.competitors = pd.read_csv(f"{base}/competitor_activity.csv", parse_dates=["date"])

    def _preprocess(self):
        self.pos["date"] = pd.to_datetime(self.pos["date"])
        self.pos["week"] = self.pos["date"].dt.isocalendar().week
        # Hourly revenue aggregation (pre / post regulation)
        self.hourly_pre = (
            self.pos[self.pos["is_post_regulation"] == False]
            .groupby("hour")["revenue_egp"].mean().reset_index()
        )
        self.hourly_post = (
            self.pos[self.pos["is_post_regulation"] == True]
            .groupby("hour")["revenue_egp"].mean().reset_index()
        )

    # ── KPIs ──────────────────────────────────────────────────────────────────

    def compute_kpis(self, year: Optional[int] = None) -> KPISnapshot:
        df = self.pos if year is None else self.pos[self.pos["year"] == year]
        tf = self.traffic if year is None else self.traffic[self.traffic["year"] == year]

        total_rev = df["revenue_egp"].sum()
        hourly_rev = df.groupby("hour")["revenue_egp"].mean()
        peak_hr = int(hourly_rev.idxmax())
        peak_rev = float(hourly_rev.max())

        # Revenue lost after 9 PM (using pre-regulation hours 21-23 as counterfactual)
        post9_pre = self.hourly_pre[self.hourly_pre["hour"] >= 21]["revenue_egp"].sum()
        avg_days = df["date"].nunique()
        rev_lost = post9_pre * avg_days  # projected annual loss

        conv = tf["conversion_rate"].mean()
        top_cat = df.groupby("category")["revenue_egp"].sum().idxmax()
        txns = len(df)

        return KPISnapshot(
            total_revenue=round(total_rev, 2),
            avg_hourly_revenue=round(hourly_rev.mean(), 2),
            peak_hour=peak_hr,
            peak_revenue=round(peak_rev, 2),
            revenue_lost_post_9pm=round(rev_lost, 2),
            conversion_rate=round(float(conv), 4),
            top_category=top_cat,
            transactions=txns,
        )

    # ── Hourly Revenue Comparison ─────────────────────────────────────────────

    def hourly_revenue_comparison(self) -> pd.DataFrame:
        """Returns merged pre/post regulation hourly averages."""
        merged = self.hourly_pre.rename(columns={"revenue_egp": "pre_reg_avg"}).merge(
            self.hourly_post.rename(columns={"revenue_egp": "post_reg_avg"}),
            on="hour", how="outer"
        ).sort_values("hour")
        merged["delta"] = merged["post_reg_avg"] - merged["pre_reg_avg"]
        merged["delta_pct"] = (merged["delta"] / merged["pre_reg_avg"] * 100).round(2)
        return merged

    # ── Time-Series Forecast ──────────────────────────────────────────────────

    def forecast_daily_revenue(self, days_ahead: int = 30) -> pd.DataFrame:
        """Simple exponential smoothing forecast (no external libs needed)."""
        daily = (
            self.pos[self.pos["is_post_regulation"] == True]
            .groupby("date")["revenue_egp"].sum()
            .reset_index()
            .sort_values("date")
        )
        alpha = 0.25
        smoothed = [float(daily["revenue_egp"].iloc[0])]
        for v in daily["revenue_egp"].iloc[1:]:
            smoothed.append(alpha * v + (1 - alpha) * smoothed[-1])

        # Trend component (linear regression on last 30 days)
        recent = np.array(smoothed[-30:])
        x = np.arange(len(recent))
        slope = np.polyfit(x, recent, 1)[0]

        last_date = daily["date"].max()
        forecast_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=days_ahead)
        forecast_vals = [smoothed[-1] + slope * (i + 1) for i in range(days_ahead)]

        # Add noise ±3%
        noise = np.random.normal(0, 0.03, days_ahead)
        forecast_vals = [v * (1 + n) for v, n in zip(forecast_vals, noise)]

        return pd.DataFrame({
            "date": forecast_dates,
            "forecasted_revenue": [round(v, 2) for v in forecast_vals],
            "lower_bound": [round(v * 0.93, 2) for v in forecast_vals],
            "upper_bound": [round(v * 1.07, 2) for v in forecast_vals],
        })

    # ── Power Hours Optimizer ─────────────────────────────────────────────────

    def identify_power_hours(self, closing_hour: int = 21) -> pd.DataFrame:
        """Identify top revenue-generating hours within allowed window."""
        df = self.pos[
            (self.pos["is_post_regulation"] == True) &
            (self.pos["hour"] < closing_hour)
        ]
        hourly = df.groupby("hour").agg(
            avg_revenue=("revenue_egp", "mean"),
            total_revenue=("revenue_egp", "sum"),
            transactions=("transaction_id", "count"),
            avg_conversion=("revenue_egp", lambda x: len(x) / max(1, len(x)) * 0.42),
        ).reset_index()

        hourly["power_score"] = (
            hourly["avg_revenue"] / hourly["avg_revenue"].max() * 0.6 +
            hourly["transactions"] / hourly["transactions"].max() * 0.4
        ).round(4)

        hourly["is_power_hour"] = hourly["power_score"] >= hourly["power_score"].quantile(0.65)
        hourly["recommendation"] = hourly.apply(self._hour_recommendation, axis=1)
        return hourly.sort_values("hour")

    def _hour_recommendation(self, row) -> str:
        h = row["hour"]
        if row["is_power_hour"]:
            return f"⚡ POWER HOUR — Deploy max staff, run flash deals"
        elif h in [10, 11, 12]:
            return "📦 Morning — Ideal for restocking & window display refresh"
        elif h in [13, 14]:
            return "🧹 Midday — Staff breaks, inventory audit"
        else:
            return "📊 Moderate — Maintain standard operations"

    # ── Staffing Optimizer ────────────────────────────────────────────────────

    def optimize_staffing(self, closing_hour: int = 21) -> list[StaffingPlan]:
        plans = []
        tf = self.traffic[
            (self.traffic["is_post_regulation"] == True) &
            (self.traffic["hour"] < closing_hour)
        ].groupby("hour").agg(
            avg_visitors=("visitors", "mean"),
        ).reset_index()

        for _, row in tf.iterrows():
            visitors = int(row["avg_visitors"])
            needed = max(1, visitors // self.STAFF_CUSTOMER_RATIO)
            cashiers = max(1, needed // 3)
            sales = needed - cashiers
            util = min(100, round(visitors / self.HOURLY_CAPACITY * 100, 1))

            if row["hour"] >= 18:
                note = "🔴 Peak rush — all hands on deck"
            elif row["hour"] >= 15:
                note = "🟡 Moderate traffic — normal operations"
            else:
                note = "🟢 Low traffic — good for stocking/training"

            plans.append(StaffingPlan(
                hour=int(row["hour"]),
                recommended_sales=sales,
                recommended_cashiers=cashiers,
                expected_visitors=visitors,
                utilization_pct=util,
                note=note,
            ))
        return plans

    # ── What-If Simulator ─────────────────────────────────────────────────────

    def run_whatif(
        self,
        closing_hour: int = 21,
        discount_start: int = 16,
        discount_end: int = 18,
        discount_pct: float = 20.0,
        extra_marketing_spend: float = 0.0,
    ) -> WhatIfResult:
        """Simulate revenue under user-defined scenario."""
        df_post = self.pos[self.pos["is_post_regulation"] == True].copy()

        # Baseline: sum of revenue within allowed hours
        baseline = df_post[df_post["hour"] < self.REGULATION_HOUR]["revenue_egp"].sum()

        # Scenario revenue
        scenario_df = df_post[df_post["hour"] < closing_hour].copy()

        # Apply discount uplift: discounted hours see +35% visitor boost
        uplift_mask = (
            (scenario_df["hour"] >= discount_start) &
            (scenario_df["hour"] < discount_end)
        )
        discount_factor = 1 - discount_pct / 100
        volume_uplift = 1.35
        scenario_df.loc[uplift_mask, "revenue_egp"] = (
            scenario_df.loc[uplift_mask, "revenue_egp"] * discount_factor * volume_uplift
        )

        # Extended hours: add synthetic revenue for hours 21..closing_hour-1
        extra_rev = 0.0
        for h in range(self.REGULATION_HOUR, closing_hour):
            # Estimate based on pre-regulation pattern
            pre_h = self.hourly_pre[self.hourly_pre["hour"] == h]
            if not pre_h.empty:
                extra_rev += float(pre_h["revenue_egp"].iloc[0]) * df_post["date"].nunique()

        scenario_rev = scenario_df["revenue_egp"].sum() + extra_rev - extra_marketing_spend
        delta = scenario_rev - baseline
        delta_pct = delta / baseline * 100

        power = self.identify_power_hours(closing_hour)
        power_hours = power[power["is_power_hour"]]["hour"].tolist()

        if delta_pct > 10:
            rec = f"✅ Strong uplift projected (+{delta_pct:.1f}%). Recommend implementing this scenario."
        elif delta_pct > 0:
            rec = f"⚠️ Moderate gain (+{delta_pct:.1f}%). Consider piloting on weekends first."
        else:
            rec = f"❌ Scenario underperforms baseline ({delta_pct:.1f}%). Revise discount depth or hours."

        return WhatIfResult(
            scenario_name=f"Close@{closing_hour}:00 | Discount {discount_pct}% [{discount_start}-{discount_end}h]",
            closing_hour=closing_hour,
            discount_window=(discount_start, discount_end),
            discount_pct=discount_pct,
            projected_revenue=round(scenario_rev, 2),
            revenue_vs_baseline=round(baseline, 2),
            revenue_change_pct=round(delta_pct, 2),
            peak_hours=power_hours,
            recommendation=rec,
        )

    # ── Competitor Gap Analysis ───────────────────────────────────────────────

    def competitor_gap_analysis(self) -> pd.DataFrame:
        """Find hours where our shop can capture demand competitors miss."""
        comp_hourly = (
            self.competitors[self.competitors["year"] == 2026]
            .groupby("hour")["activity_index"]
            .mean()
            .reset_index()
            .rename(columns={"activity_index": "avg_competitor_activity"})
        )
        our = self.identify_power_hours()
        merged = our.merge(comp_hourly, on="hour", how="left")
        merged["gap_opportunity"] = (
            (1 - merged["avg_competitor_activity"]) * merged["power_score"]
        ).round(4)
        merged["gap_label"] = merged["gap_opportunity"].apply(
            lambda x: "🎯 High Opportunity" if x > 0.4 else (
                "⚡ Competitive" if x > 0.2 else "📉 Saturated"
            )
        )
        return merged.sort_values("gap_opportunity", ascending=False)

    # ── Category Performance ──────────────────────────────────────────────────

    def category_performance(self) -> pd.DataFrame:
        return (
            self.pos[self.pos["is_post_regulation"] == True]
            .groupby("category")
            .agg(
                total_revenue=("revenue_egp", "sum"),
                transactions=("transaction_id", "count"),
                avg_ticket=("revenue_egp", "mean"),
                avg_discount=("discount_pct", "mean"),
            )
            .round(2)
            .reset_index()
            .sort_values("total_revenue", ascending=False)
        )

    # ── Weekly Heatmap ────────────────────────────────────────────────────────

    def weekly_heatmap(self) -> pd.DataFrame:
        """Revenue pivot: day-of-week × hour."""
        df = self.pos[self.pos["is_post_regulation"] == True]
        pivot = df.pivot_table(
            values="revenue_egp", index="day_of_week", columns="hour",
            aggfunc="mean"
        )
        order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        existing = [d for d in order if d in pivot.index]
        return pivot.reindex(existing).round(2)
