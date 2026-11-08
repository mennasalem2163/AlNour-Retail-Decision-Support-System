"""
controllers/dashboard_controller.py
MVC Controller — orchestrates data flow between model (analytics) and view (Streamlit).
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.analytics import DSSAnalytics, WhatIfResult


class DashboardController:
    """
    Single entry-point for the Streamlit view.
    All business logic lives in DSSAnalytics; controller only routes calls.
    """

    def __init__(self, data_dir: str = "data"):
        self.engine = DSSAnalytics(data_dir=data_dir)

    # ── KPI panel ─────────────────────────────────────────────────────────────

    def get_kpis(self, year: int = None):
        return self.engine.compute_kpis(year)

    # ── Charts / tables ───────────────────────────────────────────────────────

    def get_hourly_comparison(self) -> pd.DataFrame:
        return self.engine.hourly_revenue_comparison()

    def get_power_hours(self, closing_hour: int = 21) -> pd.DataFrame:
        return self.engine.identify_power_hours(closing_hour)

    def get_forecast(self, days: int = 30) -> pd.DataFrame:
        return self.engine.forecast_daily_revenue(days)

    def get_staffing_plan(self, closing_hour: int = 21):
        return self.engine.optimize_staffing(closing_hour)

    def get_category_performance(self) -> pd.DataFrame:
        return self.engine.category_performance()

    def get_weekly_heatmap(self) -> pd.DataFrame:
        return self.engine.weekly_heatmap()

    def get_competitor_gaps(self) -> pd.DataFrame:
        return self.engine.competitor_gap_analysis()

    # ── What-If ───────────────────────────────────────────────────────────────

    def run_scenario(
        self,
        closing_hour: int,
        discount_start: int,
        discount_end: int,
        discount_pct: float,
        marketing_spend: float = 0.0,
    ) -> WhatIfResult:
        return self.engine.run_whatif(
            closing_hour=closing_hour,
            discount_start=discount_start,
            discount_end=discount_end,
            discount_pct=discount_pct,
            extra_marketing_spend=marketing_spend,
        )

    # ── Formatting helpers ────────────────────────────────────────────────────

    @staticmethod
    def fmt_egp(value: float) -> str:
        return f"EGP {value:,.0f}"

    @staticmethod
    def fmt_pct(value: float) -> str:
        return f"{value:.1f}%"
