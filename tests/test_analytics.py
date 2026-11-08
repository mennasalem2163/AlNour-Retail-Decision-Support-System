"""
tests/test_analytics.py
Unit tests for the DSS analytics engine.
Run: pytest tests/ -v
"""

import os, sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.analytics import DSSAnalytics

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


@pytest.fixture(scope="module")
def engine():
    return DSSAnalytics(data_dir=DATA_DIR)


def test_data_loaded(engine):
    assert len(engine.pos) > 0, "POS data should not be empty"
    assert len(engine.traffic) > 0, "Foot traffic data should not be empty"
    assert len(engine.staffing) > 0, "Staffing data should not be empty"
    assert len(engine.competitors) > 0, "Competitor data should not be empty"


def test_kpis_2025(engine):
    kpis = engine.compute_kpis(2025)
    assert kpis.total_revenue > 0
    assert 10 <= kpis.peak_hour <= 23
    assert 0 < kpis.conversion_rate < 1
    assert kpis.transactions > 0


def test_kpis_2026(engine):
    kpis = engine.compute_kpis(2026)
    assert kpis.total_revenue > 0
    assert kpis.peak_hour < 21, "Post-regulation peak should be before 9 PM"


def test_hourly_comparison_shape(engine):
    df = engine.hourly_revenue_comparison()
    assert "hour" in df.columns
    assert "pre_reg_avg" in df.columns
    assert "post_reg_avg" in df.columns
    assert len(df) > 0


def test_power_hours_within_window(engine):
    for closing in [20, 21, 22]:
        ph = engine.identify_power_hours(closing_hour=closing)
        assert all(ph["hour"] < closing), f"Power hours must be < closing hour {closing}"
        assert "is_power_hour" in ph.columns
        assert ph["is_power_hour"].any(), "At least one power hour should be identified"


def test_forecast_length(engine):
    for days in [7, 14, 30]:
        fc = engine.forecast_daily_revenue(days_ahead=days)
        assert len(fc) == days, f"Forecast should have {days} rows"
        assert all(fc["forecasted_revenue"] > 0)
        assert all(fc["lower_bound"] < fc["forecasted_revenue"])
        assert all(fc["upper_bound"] > fc["forecasted_revenue"])


def test_whatif_baseline(engine):
    result = engine.run_whatif(
        closing_hour=21, discount_start=16, discount_end=18,
        discount_pct=0.0, extra_marketing_spend=0.0
    )
    assert result.projected_revenue > 0
    assert result.revenue_vs_baseline > 0
    assert isinstance(result.recommendation, str)
    assert result.closing_hour == 21


def test_whatif_extended_hours(engine):
    base = engine.run_whatif(closing_hour=21, discount_start=18, discount_end=20, discount_pct=0)
    extended = engine.run_whatif(closing_hour=23, discount_start=18, discount_end=20, discount_pct=0)
    assert extended.projected_revenue > base.projected_revenue, \
        "Extending hours should increase projected revenue"


def test_whatif_discount_uplift(engine):
    no_disc = engine.run_whatif(closing_hour=21, discount_start=16, discount_end=18, discount_pct=0)
    with_disc = engine.run_whatif(closing_hour=21, discount_start=16, discount_end=18, discount_pct=20)
    # Discount with volume uplift should change revenue
    assert no_disc.projected_revenue != with_disc.projected_revenue


def test_staffing_plan(engine):
    plans = engine.optimize_staffing(closing_hour=21)
    assert len(plans) > 0
    for p in plans:
        assert p.hour < 21
        assert p.recommended_sales >= 0
        assert p.recommended_cashiers >= 1
        assert 0 <= p.utilization_pct <= 100


def test_category_performance(engine):
    cats = engine.category_performance()
    assert "category" in cats.columns
    assert "total_revenue" in cats.columns
    assert len(cats) == 5  # 5 categories defined


def test_competitor_gap(engine):
    gaps = engine.competitor_gap_analysis()
    assert "gap_opportunity" in gaps.columns
    assert "gap_label" in gaps.columns
    assert all(gaps["gap_opportunity"] >= 0)


def test_weekly_heatmap(engine):
    hm = engine.weekly_heatmap()
    assert not hm.empty
    # Heatmap includes all years (pre + post), so hours up to 23 are valid
    assert all(10 <= col <= 23 for col in hm.columns), "Heatmap should only cover shop trading hours"


# ── Ramadan Calendar Tests ────────────────────────────────────────────────────

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ramadan_calendar import (
    get_event_for_date, upcoming_events, ramadan_impact_summary,
    tag_dataframe, ALL_EVENTS
)
from datetime import date


def test_ramadan_event_lookup():
    """Ramadan 2026 date should return the Ramadan event."""
    ev = get_event_for_date(date(2026, 3, 1))
    assert ev is not None
    assert "Ramadan" in ev.name
    assert ev.revenue_multiplier > 1.0


def test_eid_event_lookup():
    """Eid al-Fitr 2026 should return highest multiplier."""
    ev = get_event_for_date(date(2026, 3, 21))
    assert ev is not None
    assert "Eid" in ev.name
    assert ev.revenue_multiplier >= 1.40


def test_normal_day_returns_none():
    """A normal weekday with no event should return None."""
    ev = get_event_for_date(date(2025, 7, 15))
    assert ev is None


def test_ramadan_impact_summary():
    impact = ramadan_impact_summary()
    assert impact["ramadan_days"] == 30
    assert impact["total_ramadan_loss_egp"] > 0
    assert impact["pre_reg_daily_rev_egp"] > impact["post_reg_daily_rev_egp"]
    assert "notes" in impact


def test_upcoming_events():
    events = upcoming_events(from_date=date(2026, 1, 1), n=3)
    assert len(events) == 3
    # Should all be on or after Jan 1 2026
    for ev in events:
        assert ev.end >= date(2026, 1, 1)
    # Should be sorted chronologically
    assert events[0].start <= events[1].start


def test_all_events_have_valid_multipliers():
    for ev in ALL_EVENTS:
        assert 0.5 <= ev.revenue_multiplier <= 2.0
        assert 0.5 <= ev.traffic_multiplier <= 2.0
        assert ev.start <= ev.end


def test_tag_dataframe():
    import pandas as pd
    df = pd.DataFrame({
        "date": ["2026-03-01", "2025-07-15", "2026-03-20"],
        "revenue": [1000, 1000, 1000],
    })
    result = tag_dataframe(df)
    assert "season_event" in result.columns
    assert "revenue_multiplier" in result.columns
    assert result.loc[0, "season_event"] == "Ramadan 2026"
    assert result.loc[1, "season_event"] == "Normal"
    assert result.loc[2, "season_event"] == "Eid al-Fitr 2026"
