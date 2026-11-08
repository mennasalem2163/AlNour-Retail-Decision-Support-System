#!/usr/bin/env python3
"""
utils/cli_summary.py
Command-line Daily Management Briefing for Al-Nour Fashion Boutique.
Prints a colour-coded summary to the terminal without needing Streamlit.

Usage:  python utils/cli_summary.py
        python utils/cli_summary.py --date 2026-03-15
"""

import os, sys, argparse
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.analytics import DSSAnalytics
from utils.ramadan_calendar import get_event_for_date, upcoming_events, ramadan_impact_summary

# ANSI colours
R  = "\033[91m"   # red
G  = "\033[92m"   # green
Y  = "\033[93m"   # yellow
B  = "\033[94m"   # blue
M  = "\033[95m"   # magenta
C  = "\033[96m"   # cyan
W  = "\033[97m"   # white bold
DIM= "\033[2m"
RST= "\033[0m"

LINE  = f"{DIM}{'─'*62}{RST}"
DLINE = f"{W}{'═'*62}{RST}"


def hdr(text): print(f"\n{W}{text}{RST}")
def sub(label, val, colour=W): print(f"  {DIM}{label:<30}{RST}{colour}{val}{RST}")
def ok(text):  print(f"  {G}✔  {text}{RST}")
def warn(text):print(f"  {Y}⚠  {text}{RST}")
def crit(text):print(f"  {R}✖  {text}{RST}")
def info(text):print(f"  {C}ℹ  {text}{RST}")


def run(target_date: date):
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    engine = DSSAnalytics(data_dir=DATA_DIR)

    kpi26 = engine.compute_kpis(2026)
    kpi25 = engine.compute_kpis(2025)

    ph     = engine.identify_power_hours(21)
    power  = ph[ph["is_power_hour"]]["hour"].tolist()
    staff  = engine.optimize_staffing(21)
    gaps   = engine.competitor_gap_analysis()
    top_gap= gaps.iloc[0]
    fc     = engine.forecast_daily_revenue(7)
    fc7    = fc["forecasted_revenue"].sum()

    event  = get_event_for_date(target_date)
    next3  = upcoming_events(from_date=target_date, n=3)
    ram    = ramadan_impact_summary()

    # ── Header ────────────────────────────────────────────────────────────────
    print(DLINE)
    print(f"{W}  🏪  AL-NOUR FASHION BOUTIQUE — DAILY BRIEFING{RST}")
    print(f"  {DIM}Cairo, Egypt  |  {target_date.strftime('%A, %d %B %Y')}  |  DSS B-01{RST}")
    print(DLINE)

    # ── Today's context ───────────────────────────────────────────────────────
    hdr("📅  TODAY'S CONTEXT")
    if event:
        print(f"  {M}🎉  ACTIVE EVENT: {event.name}{RST}")
        print(f"     Revenue multiplier: ×{event.revenue_multiplier}  |  "
              f"Traffic multiplier: ×{event.traffic_multiplier}")
        print(f"     {DIM}{event.notes}{RST}")
    else:
        print(f"  {DIM}  Normal trading day — no special event active.{RST}")

    print(f"\n  {DIM}Upcoming events:{RST}")
    for ev in next3:
        days_away = (ev.start - target_date).days
        print(f"    {C}→ {ev.name:<25}{RST}  {ev.start}  "
              f"({days_away}d away)  ×{ev.revenue_multiplier:.2f}")

    # ── KPI snapshot ─────────────────────────────────────────────────────────
    hdr("📊  KPI SNAPSHOT (2026 YTD vs 2025 Full Year)")
    print(LINE)
    sub("Total Revenue 2025 (pre-reg):",
        f"EGP {kpi25.total_revenue/1e6:.2f}M", G)
    sub("Total Revenue 2026 (post-reg YTD):",
        f"EGP {kpi26.total_revenue/1e6:.2f}M", Y)

    rev_delta_pct = (kpi26.total_revenue - kpi25.total_revenue) / kpi25.total_revenue * 100
    colour = G if rev_delta_pct >= 0 else R
    sub("YoY Revenue Δ:", f"{rev_delta_pct:+.1f}%", colour)

    sub("2025 Peak Hour:", f"{kpi25.peak_hour}:00", W)
    sub("2026 Peak Hour:", f"{kpi26.peak_hour}:00  ← shifted by regulation", Y)
    sub("Transactions (2026 YTD):", f"{kpi26.transactions:,}", W)
    sub("Top Revenue Category:", kpi26.top_category, C)
    sub("Avg Conversion Rate:", f"{kpi26.conversion_rate*100:.1f}%", W)
    sub("7-Day Revenue Forecast:", f"EGP {fc7:,.0f}", G)
    print(LINE)

    # ── Power hours ───────────────────────────────────────────────────────────
    hdr("⚡  TODAY'S POWER HOURS  (9 PM Closing)")
    if power:
        ok(f"Deploy maximum staff during: "
           + "  |  ".join(f"{h}:00–{h+1}:00" for h in power))
        for h in power:
            row = ph[ph["hour"] == h].iloc[0]
            print(f"     {Y}{h}:00{RST}  avg EGP {row['avg_revenue']:,.0f} "
                  f" score={row['power_score']:.3f}  txns={int(row['transactions'])}")
    else:
        warn("No power hours identified — check data.")

    # ── Regulation alert ──────────────────────────────────────────────────────
    hdr("🔴  REGULATION COMPLIANCE  (9 PM Closure)")
    crit(f"Shop MUST close by 21:00 — Egyptian Cabinet Decree 1276")
    warn(f"Estimated annual revenue at risk: "
         f"EGP {kpi26.revenue_lost_post_9pm:,.0f}")
    info(f"Ramadan 2026 additional loss: "
         f"EGP {ram['total_ramadan_loss_egp']:,.0f}  "
         f"({ram['ramadan_days']} days × EGP {ram['daily_loss_egp']:,.0f}/day)")

    # ── Staffing ──────────────────────────────────────────────────────────────
    hdr("👥  STAFFING RECOMMENDATION")
    print(f"  {'Hour':<8}{'Sales':>8}{'Cashiers':>10}{'Visitors':>10}  {'Note'}")
    print(LINE)
    for p in staff:
        util_col = R if p.utilization_pct > 80 else (Y if p.utilization_pct > 50 else G)
        print(f"  {p.hour}:00   "
              f"{p.recommended_sales:>5}   "
              f"{p.recommended_cashiers:>8}   "
              f"{p.expected_visitors:>8}   "
              f"{util_col}{p.note}{RST}")
    print(LINE)
    ok("Shift all restocking to before 14:00 — free staff for evening rush")

    # ── Competitor gap ────────────────────────────────────────────────────────
    hdr("🏆  TOP COMPETITOR OPPORTUNITY")
    ok(f"Best uncontested window: {int(top_gap['hour'])}:00–{int(top_gap['hour'])+1}:00")
    sub("Gap Opportunity Score:", f"{top_gap['gap_opportunity']:.3f}", G)
    sub("Competitor Activity:",   f"{top_gap['avg_competitor_activity']:.2f} (low = good)", G)
    sub("Our Avg Revenue there:", f"EGP {top_gap['avg_revenue']:,.0f}", W)

    # ── Recommendations ───────────────────────────────────────────────────────
    hdr("✅  TOP ACTIONS FOR TODAY")
    actions = [
        f"Activate flash promotions at {', '.join(f'{h}:00' for h in power[:2])} (Power Hours)",
        f"Station 2 cashiers + 3 sales staff from 18:00 onwards",
        f"Run a {int(top_gap['hour'])}:00 lunch-hour deal — competitors are quiet then",
        "Complete all restocking before 14:00 — zero stock tasks after 18:00",
        "Ensure shop is fully cleared of customers by 20:45",
    ]
    if event:
        actions.insert(0, f"🎉 {event.name} is active — push {event.name.split()[0]} promotions hard!")
    for i, a in enumerate(actions, 1):
        ok(f"[{i}] {a}")

    print(f"\n{DLINE}")
    print(f"  {DIM}Generated by DSS B-01 · Al-Nour Fashion Boutique · {datetime.now():%Y-%m-%d %H:%M}{RST}")
    print(DLINE + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DSS Daily Management Briefing")
    parser.add_argument("--date", default=str(date.today()),
                        help="Target date (YYYY-MM-DD), default: today")
    args = parser.parse_args()
    target = datetime.strptime(args.date, "%Y-%m-%d").date()
    run(target)
