"""
views/app.py  ─  Streamlit Dashboard
Shop Operating Hours Compliance & Revenue Optimization DSS (B-01)
Run with:  streamlit run views/app.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from controllers.dashboard_controller import DashboardController
from utils.ramadan_calendar import (
    ALL_EVENTS, get_event_for_date, upcoming_events,
    ramadan_impact_summary, tag_dataframe
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DSS | Al-Nour Fashion Boutique",
    page_icon="🕘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Space+Mono&display=swap');

html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }

.main { background: #0f1117; }

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #1a1f2e 0%, #232940 100%);
    border: 1px solid #2d3554;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 4px 0;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #e8973a, #d4581a);
}
.kpi-value { font-size: 2rem; font-weight: 700; color: #e8973a; font-family: 'Space Mono', monospace; }
.kpi-label { font-size: 0.78rem; color: #8892b0; text-transform: uppercase; letter-spacing: 1.5px; }
.kpi-delta { font-size: 0.85rem; margin-top: 4px; }

.alert-box {
    background: #1f1115;
    border-left: 4px solid #e84444;
    border-radius: 8px;
    padding: 12px 16px;
    color: #f0a0a0;
    margin: 12px 0;
}
.power-badge {
    display: inline-block;
    background: #e8973a22;
    border: 1px solid #e8973a;
    color: #e8973a;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 600;
}
section[data-testid="stSidebar"] { background: #0d1117; border-right: 1px solid #1e2533; }
h1, h2, h3 { color: #e8e8f0; }
.stSelectbox label, .stSlider label { color: #8892b0; }
</style>
""", unsafe_allow_html=True)

# ── Controller ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_controller():
    base = os.path.dirname(os.path.dirname(__file__))
    return DashboardController(data_dir=os.path.join(base, "data"))

ctrl = load_controller()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏪 Al-Nour Fashion")
    st.markdown("**DSS · Cairo, Egypt**")
    st.divider()
    page = st.radio(
        "Navigation",
        ["📊 Overview", "⚡ Power Hours", "👥 Staffing", "🔮 What-If Simulator",
         "🏆 Competitor Intel", "📈 Forecast", "🌙 Ramadan & Calendar"],
        label_visibility="collapsed"
    )
    st.divider()
    year_sel = st.selectbox("Filter Year", [None, 2025, 2026], format_func=lambda x: "All Years" if x is None else str(x))
    st.caption("🔴 Regulation: Shops close at 21:00")

# ── Shared data ───────────────────────────────────────────────────────────────
kpis = ctrl.get_kpis(year_sel)
COLORS = {"pre": "#4a9eff", "post": "#e8973a", "accent": "#e84444", "green": "#4ade80"}

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown("# 📊 Operations Overview")
    st.markdown(f"**Shop: Al-Nour Fashion Boutique · Cairo · Egypt**  |  Regulation: 9 PM Closure Active")

    # Alert
    st.markdown(f"""
    <div class="alert-box">
    ⚠️ <strong>Regulation Impact Alert:</strong> Under the 9 PM closure rule, an estimated
    <strong>EGP {kpis.revenue_lost_post_9pm:,.0f}</strong> in annual revenue is at risk from lost
    late-night trading (21:00–23:00). This DSS helps you recover it.
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (c1, "Total Revenue", f"EGP {kpis.total_revenue/1e6:.2f}M", ""),
        (c2, "Transactions",  f"{kpis.transactions:,}", ""),
        (c3, "Peak Hour",     f"{kpis.peak_hour}:00", "Best trading window"),
        (c4, "Conversion",    f"{kpis.conversion_rate*100:.1f}%", ""),
        (c5, "Top Category",  kpis.top_category.split("'")[0], ""),
    ]
    for col, label, val, delta in metrics:
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-delta" style="color:#8892b0">{delta}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Hourly revenue comparison
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.subheader("Hourly Revenue: Pre vs Post Regulation")
        hrly = ctrl.get_hourly_comparison()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hrly["hour"], y=hrly.get("pre_reg_avg", [0]*len(hrly)),
            name="Pre-Regulation (2025)", marker_color=COLORS["pre"], opacity=0.7
        ))
        fig.add_trace(go.Bar(
            x=hrly["hour"], y=hrly.get("post_reg_avg", [0]*len(hrly)),
            name="Post-Regulation (2026)", marker_color=COLORS["post"]
        ))
        fig.add_vline(x=20.5, line_dash="dash", line_color=COLORS["accent"],
                      annotation_text="9 PM Cutoff", annotation_position="top left")
        fig.update_layout(
            barmode="group", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=360,
            legend=dict(orientation="h", y=-0.2),
            xaxis_title="Hour of Day", yaxis_title="Avg Revenue (EGP)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Revenue by Category")
        cats = ctrl.get_category_performance()
        fig2 = px.pie(cats, values="total_revenue", names="category",
                      color_discrete_sequence=px.colors.sequential.Oranges_r,
                      hole=0.45)
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            height=360, showlegend=True,
            legend=dict(orientation="v", font_size=11)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Weekly heatmap
    st.subheader("Weekly Revenue Heatmap (EGP avg · 2026)")
    hm = ctrl.get_weekly_heatmap()
    fig3 = px.imshow(
        hm.values,
        x=[f"{h}:00" for h in hm.columns],
        y=list(hm.index),
        color_continuous_scale="Oranges",
        aspect="auto",
        labels=dict(color="Revenue (EGP)"),
    )
    fig3.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=280,
        xaxis_title="Hour", yaxis_title=""
    )
    st.plotly_chart(fig3, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: POWER HOURS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "⚡ Power Hours":
    st.markdown("# ⚡ Power Hours Optimizer")
    st.caption("Identifies the highest-revenue windows within the legally allowed trading hours.")

    closing_h = st.slider("Assumed Closing Hour", 18, 23, 21, key="ph_close")
    ph = ctrl.get_power_hours(closing_h)

    # Highlight power hours
    power_list = ph[ph["is_power_hour"]]["hour"].tolist()
    ph_str = ", ".join(f"**{h}:00–{h+1}:00**" for h in power_list)
    st.success(f"🏆 Recommended POWER HOURS today: {ph_str}")

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = go.Figure()
        colors = [COLORS["post"] if r else "#2d3554" for r in ph["is_power_hour"]]
        fig.add_trace(go.Bar(
            x=ph["hour"].apply(lambda h: f"{h}:00"),
            y=ph["avg_revenue"],
            marker_color=colors,
            text=ph["power_score"].apply(lambda x: f"Score: {x:.2f}"),
            textposition="outside",
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=380,
            xaxis_title="Hour", yaxis_title="Avg Revenue (EGP)",
            title="Revenue Score by Hour (orange = Power Hour)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Action Recommendations")
        for _, row in ph.iterrows():
            badge = '<span class="power-badge">POWER</span>' if row["is_power_hour"] else ""
            st.markdown(f"""
            **{int(row['hour'])}:00** {badge}<br>
            {row['recommendation']}<br>
            <small style='color:#8892b0'>Avg: EGP {row['avg_revenue']:,.0f} | Txns: {int(row['transactions'])}</small>
            """, unsafe_allow_html=True)
            st.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: STAFFING
# ═════════════════════════════════════════════════════════════════════════════
elif page == "👥 Staffing":
    st.markdown("# 👥 Smart Staffing Planner")
    st.caption("Optimal staff allocation per hour to maximize service speed during the 9 PM crunch.")

    closing_h = st.slider("Closing Hour", 18, 23, 21, key="staff_close")
    plans = ctrl.get_staffing_plan(closing_h)

    rows = []
    for p in plans:
        rows.append({
            "Hour": f"{p.hour}:00",
            "Sales Associates": p.recommended_sales,
            "Cashiers": p.recommended_cashiers,
            "Expected Visitors": p.expected_visitors,
            "Utilization %": p.utilization_pct,
            "Note": p.note,
        })
    df_plans = pd.DataFrame(rows)

    # Stacked bar
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Sales Associates", x=df_plans["Hour"],
                         y=df_plans["Sales Associates"], marker_color=COLORS["post"]))
    fig.add_trace(go.Bar(name="Cashiers", x=df_plans["Hour"],
                         y=df_plans["Cashiers"], marker_color=COLORS["pre"]))
    fig.add_trace(go.Scatter(name="Store Utilization %", x=df_plans["Hour"],
                             y=df_plans["Utilization %"], yaxis="y2",
                             line=dict(color=COLORS["green"], width=2.5), mode="lines+markers"))
    fig.update_layout(
        barmode="stack", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=400,
        yaxis=dict(title="Staff Count"),
        yaxis2=dict(title="Utilization %", overlaying="y", side="right", range=[0, 120]),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Hourly Staffing Plan")
    st.dataframe(
        df_plans.style.background_gradient(subset=["Utilization %"], cmap="YlOrRd"),
        use_container_width=True, hide_index=True
    )

    st.info("💡 **Key Insight:** Shift all inventory restocking to before 14:00. "
            "This frees 100% of stock handlers to assist sales during the 18:00–21:00 rush.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: WHAT-IF SIMULATOR
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🔮 What-If Simulator":
    st.markdown("# 🔮 What-If Scenario Simulator")
    st.caption("Model the impact of regulatory changes or promotional strategies on your revenue.")

    with st.form("scenario_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            close_h = st.slider("Closing Hour Scenario", 18, 23, 21)
            marketing = st.number_input("Extra Marketing Spend (EGP)", 0, 50000, 0, 1000)
        with col2:
            disc_start = st.slider("Discount Window Start", 10, 19, 16)
            disc_end = st.slider("Discount Window End", 11, 20, 18)
        with col3:
            disc_pct = st.slider("Discount %", 0, 40, 20)

        submitted = st.form_submit_button("▶ Run Scenario", use_container_width=True)

    if submitted:
        result = ctrl.run_scenario(close_h, disc_start, disc_end, disc_pct, marketing)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Baseline Revenue (2026)", f"EGP {result.revenue_vs_baseline/1e6:.2f}M")
        col_b.metric("Projected Revenue", f"EGP {result.projected_revenue/1e6:.2f}M",
                     delta=f"{result.revenue_change_pct:+.1f}%")
        col_c.metric("Revenue Δ", f"EGP {(result.projected_revenue-result.revenue_vs_baseline)/1e3:+,.0f}K")

        st.markdown(f"### {result.recommendation}")

        # Waterfall
        categories = ["Baseline", f"Close@{close_h}", f"Discount {disc_pct}%", "Marketing Cost", "Total"]
        base = result.revenue_vs_baseline
        ext = max(0, (result.projected_revenue - base) * 0.6)
        disc_gain = max(0, (result.projected_revenue - base) * 0.4)
        fig = go.Figure(go.Waterfall(
            name="Revenue", orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=categories,
            y=[base/1e6, ext/1e6, disc_gain/1e6, -marketing/1e6, 0],
            connector={"line": {"color": "#2d3554"}},
            decreasing={"marker": {"color": COLORS["accent"]}},
            increasing={"marker": {"color": COLORS["green"]}},
            totals={"marker": {"color": COLORS["post"]}},
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=380,
            yaxis_title="Revenue (Million EGP)",
            title=result.scenario_name
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"**Recommended Power Hours in this scenario:** "
                    + ", ".join(f"`{h}:00`" for h in result.peak_hours))

    else:
        st.markdown("""
        ### Try these pre-set scenarios:
        | Scenario | Closing | Discount | Expected Impact |
        |---|---|---|---|
        | Status Quo | 21:00 | None | Baseline |
        | Regulation Eased | 22:00 | None | +8–12% |
        | Early-Bird Promo | 21:00 | 20% @ 16–18h | +5–9% |
        | Double Strike | 22:00 | 15% @ 15–17h | +14–18% |
        """)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: COMPETITOR INTEL
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🏆 Competitor Intel":
    st.markdown("# 🏆 Competitor Gap Analysis")
    st.caption("Identify hours where competitors are quiet — your window to capture uncontested demand.")

    gaps = ctrl.get_competitor_gaps()

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = px.scatter(
            gaps, x="hour", y="gap_opportunity",
            size="avg_revenue", color="gap_label",
            color_discrete_map={
                "🎯 High Opportunity": COLORS["green"],
                "⚡ Competitive": COLORS["post"],
                "📉 Saturated": "#555"
            },
            hover_data=["avg_revenue", "avg_competitor_activity"],
            title="Gap Opportunity Score by Hour",
            labels={"hour": "Hour of Day", "gap_opportunity": "Opportunity Score"}
        )
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Top Opportunities")
        top = gaps[gaps["gap_label"] == "🎯 High Opportunity"].head(5)
        for _, row in top.iterrows():
            st.markdown(f"""
            **{int(row['hour'])}:00–{int(row['hour'])+1}:00**
            Opportunity: `{row['gap_opportunity']:.3f}`
            Competitor Activity: `{row['avg_competitor_activity']:.2f}`
            Our Revenue: `EGP {row['avg_revenue']:,.0f}`
            """)
            st.progress(float(row["gap_opportunity"]))

    st.markdown("### Competitor Activity Table")
    st.dataframe(
        gaps[["hour", "avg_revenue", "avg_competitor_activity", "gap_opportunity", "gap_label"]]
        .rename(columns={"hour": "Hour", "avg_revenue": "Our Avg Rev (EGP)",
                         "avg_competitor_activity": "Competitor Activity",
                         "gap_opportunity": "Gap Score", "gap_label": "Status"})
        .style.background_gradient(subset=["Gap Score"], cmap="Greens"),
        use_container_width=True, hide_index=True
    )

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: FORECAST
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📈 Forecast":
    st.markdown("# 📈 Revenue Forecast")
    st.caption("30-day ahead forecast using exponential smoothing on 2026 post-regulation trading data.")

    days = st.slider("Forecast Horizon (days)", 7, 90, 30)
    fc = ctrl.get_forecast(days)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fc["date"], y=fc["upper_bound"],
        fill=None, mode="lines", line_color="rgba(232,151,58,0)", showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=fc["date"], y=fc["lower_bound"],
        fill="tonexty", mode="lines", line_color="rgba(232,151,58,0)",
        fillcolor="rgba(232,151,58,0.15)", name="Confidence Band"
    ))
    fig.add_trace(go.Scatter(
        x=fc["date"], y=fc["forecasted_revenue"],
        mode="lines+markers", name="Forecast",
        line=dict(color=COLORS["post"], width=2.5)
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=420,
        xaxis_title="Date", yaxis_title="Daily Revenue (EGP)",
        legend=dict(orientation="h", y=-0.2)
    )
    st.plotly_chart(fig, use_container_width=True)

    total_proj = fc["forecasted_revenue"].sum()
    avg_daily = fc["forecasted_revenue"].mean()
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Projected {days}-Day Revenue", f"EGP {total_proj:,.0f}")
    col2.metric("Avg Daily Revenue", f"EGP {avg_daily:,.0f}")
    col3.metric("Trend", "📈 Positive" if fc["forecasted_revenue"].iloc[-1] > fc["forecasted_revenue"].iloc[0] else "📉 Declining")

    st.markdown("### Forecast Data Table")
    st.dataframe(fc.rename(columns={
        "date": "Date", "forecasted_revenue": "Forecast (EGP)",
        "lower_bound": "Lower (EGP)", "upper_bound": "Upper (EGP)"
    }), use_container_width=True, hide_index=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: RAMADAN & CALENDAR
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🌙 Ramadan & Calendar":
    from datetime import date as dt_date
    st.markdown("# 🌙 Ramadan & Egyptian Holiday Calendar")
    st.caption("Seasonality-aware planning for Egypt's major retail events — "
               "with 9 PM regulation impact quantified for Ramadan 2026.")

    # Ramadan 2026 impact box
    ram = ramadan_impact_summary()
    st.markdown(f"""
    <div class="alert-box">
    🌙 <strong>Ramadan 2026 Regulation Impact</strong><br>
    Dates: <strong>{ram['ramadan_start']} → {ram['ramadan_end']}</strong>
    ({ram['ramadan_days']} days)<br>
    The 9 PM closure eliminates the traditional 21:00–01:00 Ramadan shopping window.<br>
    Estimated loss vs pre-regulation Ramadan:
    <strong>EGP {ram['total_ramadan_loss_egp']:,.0f}</strong>
    (EGP {ram['daily_loss_egp']:,.0f}/day × {ram['ramadan_days']} days)<br>
    <small>{ram['notes']}</small>
    </div>
    """, unsafe_allow_html=True)

    # Events table
    st.subheader("📅 Full Event Calendar 2025–2026")
    rows = []
    for ev in ALL_EVENTS:
        days = (ev.end - ev.start).days + 1
        today = dt_date.today()
        status = "✅ Past" if ev.end < today else ("🔴 Active" if ev.start <= today <= ev.end else "🔵 Upcoming")
        rows.append({
            "Event": ev.name,
            "Start": str(ev.start),
            "End": str(ev.end),
            "Days": days,
            "Rev Multiplier": f"×{ev.revenue_multiplier:.2f}",
            "Traffic Multiplier": f"×{ev.traffic_multiplier:.2f}",
            "Status": status,
            "Notes": ev.notes[:60] + "…" if len(ev.notes) > 60 else ev.notes,
        })
    df_events = pd.DataFrame(rows)
    st.dataframe(df_events, use_container_width=True, hide_index=True)

    # Revenue multiplier timeline chart
    st.subheader("Revenue Multiplier by Season")
    fig = go.Figure()
    colours = {"✅ Past": "#4a5568", "🔴 Active": "#e84444", "🔵 Upcoming": "#4a9eff"}
    for _, r in df_events.iterrows():
        mult = float(r["Rev Multiplier"].replace("×", ""))
        colour = "#4ade80" if mult >= 1.30 else ("#e8973a" if mult >= 1.10 else "#e84444")
        fig.add_trace(go.Bar(
            name=r["Event"],
            x=[r["Event"]],
            y=[mult],
            marker_color=colour,
            text=r["Rev Multiplier"],
            textposition="outside",
            showlegend=False,
        ))
    fig.add_hline(y=1.0, line_dash="dash", line_color="#8892b0",
                  annotation_text="Baseline (×1.00)")
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=380,
        xaxis_tickangle=-35,
        yaxis_title="Revenue Multiplier",
        title="Seasonal Revenue Impact vs Normal Day"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Upcoming events
    st.subheader("📌 Upcoming Events (from today)")
    upcoming = upcoming_events(from_date=dt_date.today(), n=5)
    for ev in upcoming:
        days_away = (ev.start - dt_date.today()).days
        col1, col2, col3 = st.columns([3, 1, 2])
        col1.markdown(f"**{ev.name}**  \n{ev.start} → {ev.end}")
        col2.markdown(f"**{days_away}d away**")
        col3.markdown(f"Revenue: **×{ev.revenue_multiplier:.2f}**  \n"
                      f"Traffic: **×{ev.traffic_multiplier:.2f}**")
        st.caption(ev.notes)
        st.divider()

    st.info("💡 **Planning tip:** Pre-order Eid al-Adha inventory now (32 days away). "
            "Women's Clothing and Accessories see the sharpest spike during Eid.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small style='color:#4a5568'>DSS B-01 · Al-Nour Fashion Boutique · Cairo, Egypt "
    "· Built with Streamlit + Plotly · Data: Synthetic (CAPMAS/EFG Hermes Reference)</small></center>",
    unsafe_allow_html=True
)
