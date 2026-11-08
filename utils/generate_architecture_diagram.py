"""
utils/generate_architecture_diagram.py
Generates the system architecture diagram as SVG for the report.
"""

import os

SVG = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="900" height="560" xmlns="http://www.w3.org/2000/svg" font-family="Arial,sans-serif">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#e8973a"/>
    </marker>
    <filter id="shadow">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="900" height="560" fill="#0f1117" rx="16"/>
  <text x="450" y="38" text-anchor="middle" fill="#e8973a" font-size="20" font-weight="bold">
    DSS B-01 · System Architecture · Al-Nour Fashion Boutique
  </text>

  <!-- DATA LAYER -->
  <rect x="30" y="70" width="180" height="400" fill="#1a1f2e" rx="10" stroke="#2d3554" stroke-width="1.5"/>
  <text x="120" y="94" text-anchor="middle" fill="#e8973a" font-size="13" font-weight="bold">DATA LAYER</text>

  <rect x="50" y="105" width="140" height="42" fill="#232940" rx="8"/>
  <text x="120" y="121" text-anchor="middle" fill="#fff" font-size="11">POS Transactions</text>
  <text x="120" y="138" text-anchor="middle" fill="#8892b0" font-size="10">89K rows · CSV</text>

  <rect x="50" y="158" width="140" height="42" fill="#232940" rx="8"/>
  <text x="120" y="174" text-anchor="middle" fill="#fff" font-size="11">Foot Traffic</text>
  <text x="120" y="191" text-anchor="middle" fill="#8892b0" font-size="10">9K rows · hourly</text>

  <rect x="50" y="211" width="140" height="42" fill="#232940" rx="8"/>
  <text x="120" y="227" text-anchor="middle" fill="#fff" font-size="11">Competitor Activity</text>
  <text x="120" y="244" text-anchor="middle" fill="#8892b0" font-size="10">41K rows · hourly</text>

  <rect x="50" y="264" width="140" height="42" fill="#232940" rx="8"/>
  <text x="120" y="280" text-anchor="middle" fill="#fff" font-size="11">Staffing Records</text>
  <text x="120" y="297" text-anchor="middle" fill="#8892b0" font-size="10">2K rows · shifts</text>

  <rect x="50" y="317" width="140" height="42" fill="#1a2535" rx="8" stroke="#4a9eff" stroke-width="1"/>
  <text x="120" y="333" text-anchor="middle" fill="#4a9eff" font-size="11">Regulation Rules</text>
  <text x="120" y="350" text-anchor="middle" fill="#8892b0" font-size="10">9 PM closure law</text>

  <!-- MODEL LAYER -->
  <rect x="270" y="70" width="200" height="400" fill="#1a1f2e" rx="10" stroke="#2d3554" stroke-width="1.5"/>
  <text x="370" y="94" text-anchor="middle" fill="#e8973a" font-size="13" font-weight="bold">MODEL LAYER</text>

  <rect x="285" y="105" width="170" height="52" fill="#232940" rx="8"/>
  <text x="370" y="124" text-anchor="middle" fill="#fff" font-size="11">Time-Series Forecast</text>
  <text x="370" y="141" text-anchor="middle" fill="#8892b0" font-size="10">Exp. Smoothing α=0.25</text>
  <text x="370" y="152" text-anchor="middle" fill="#8892b0" font-size="10">30-day horizon</text>

  <rect x="285" y="168" width="170" height="52" fill="#232940" rx="8"/>
  <text x="370" y="187" text-anchor="middle" fill="#fff" font-size="11">Power Hours Optimizer</text>
  <text x="370" y="204" text-anchor="middle" fill="#8892b0" font-size="10">Composite score model</text>
  <text x="370" y="215" text-anchor="middle" fill="#8892b0" font-size="10">Revenue + Volume</text>

  <rect x="285" y="231" width="170" height="52" fill="#232940" rx="8"/>
  <text x="370" y="250" text-anchor="middle" fill="#fff" font-size="11">Staffing Optimizer</text>
  <text x="370" y="267" text-anchor="middle" fill="#8892b0" font-size="10">Visitor/staff ratio</text>
  <text x="370" y="278" text-anchor="middle" fill="#8892b0" font-size="10">Shift allocation</text>

  <rect x="285" y="294" width="170" height="52" fill="#232940" rx="8"/>
  <text x="370" y="313" text-anchor="middle" fill="#fff" font-size="11">What-If Simulator</text>
  <text x="370" y="330" text-anchor="middle" fill="#8892b0" font-size="10">Scenario planning</text>
  <text x="370" y="341" text-anchor="middle" fill="#8892b0" font-size="10">Revenue projection</text>

  <rect x="285" y="357" width="170" height="52" fill="#232940" rx="8"/>
  <text x="370" y="376" text-anchor="middle" fill="#fff" font-size="11">Competitor Gap</text>
  <text x="370" y="393" text-anchor="middle" fill="#8892b0" font-size="10">Market opportunity</text>
  <text x="370" y="404" text-anchor="middle" fill="#8892b0" font-size="10">analysis</text>

  <!-- CONTROLLER -->
  <rect x="530" y="160" width="160" height="120" fill="#1a2535" rx="10" stroke="#4a9eff" stroke-width="1.5"/>
  <text x="610" y="184" text-anchor="middle" fill="#4a9eff" font-size="13" font-weight="bold">CONTROLLER</text>
  <text x="610" y="206" text-anchor="middle" fill="#fff" font-size="11">DashboardController</text>
  <text x="610" y="224" text-anchor="middle" fill="#8892b0" font-size="10">Routes API calls</text>
  <text x="610" y="240" text-anchor="middle" fill="#8892b0" font-size="10">Formats output</text>
  <text x="610" y="256" text-anchor="middle" fill="#8892b0" font-size="10">Manages state</text>

  <!-- VIEW LAYER -->
  <rect x="730" y="70" width="148" height="400" fill="#1a1f2e" rx="10" stroke="#2d3554" stroke-width="1.5"/>
  <text x="804" y="94" text-anchor="middle" fill="#e8973a" font-size="13" font-weight="bold">VIEW LAYER</text>

  <rect x="745" y="105" width="118" height="38" fill="#232940" rx="8"/>
  <text x="804" y="121" text-anchor="middle" fill="#fff" font-size="11">📊 Overview</text>
  <text x="804" y="137" text-anchor="middle" fill="#8892b0" font-size="10">KPIs + charts</text>

  <rect x="745" y="153" width="118" height="38" fill="#232940" rx="8"/>
  <text x="804" y="169" text-anchor="middle" fill="#fff" font-size="11">⚡ Power Hours</text>
  <text x="804" y="185" text-anchor="middle" fill="#8892b0" font-size="10">Ranked windows</text>

  <rect x="745" y="201" width="118" height="38" fill="#232940" rx="8"/>
  <text x="804" y="217" text-anchor="middle" fill="#fff" font-size="11">👥 Staffing</text>
  <text x="804" y="233" text-anchor="middle" fill="#8892b0" font-size="10">Shift planner</text>

  <rect x="745" y="249" width="118" height="38" fill="#232940" rx="8"/>
  <text x="804" y="265" text-anchor="middle" fill="#fff" font-size="11">🔮 What-If</text>
  <text x="804" y="281" text-anchor="middle" fill="#8892b0" font-size="10">Scenario builder</text>

  <rect x="745" y="297" width="118" height="38" fill="#232940" rx="8"/>
  <text x="804" y="313" text-anchor="middle" fill="#fff" font-size="11">🏆 Competitors</text>
  <text x="804" y="329" text-anchor="middle" fill="#8892b0" font-size="10">Gap analysis</text>

  <rect x="745" y="345" width="118" height="38" fill="#232940" rx="8"/>
  <text x="804" y="361" text-anchor="middle" fill="#fff" font-size="11">📈 Forecast</text>
  <text x="804" y="377" text-anchor="middle" fill="#8892b0" font-size="10">30-day outlook</text>

  <!-- Arrows: Data → Model -->
  <line x1="190" y1="200" x2="268" y2="200" stroke="#e8973a" stroke-width="2" marker-end="url(#arrow)"/>
  <!-- Arrows: Model → Controller -->
  <line x1="470" y1="240" x2="528" y2="220" stroke="#e8973a" stroke-width="2" marker-end="url(#arrow)"/>
  <!-- Arrows: Controller → View -->
  <line x1="690" y1="220" x2="728" y2="220" stroke="#4a9eff" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Labels on arrows -->
  <text x="229" y="194" fill="#e8973a" font-size="9">pandas DataFrames</text>
  <text x="489" y="218" fill="#e8973a" font-size="9">KPI / Plan objects</text>
  <text x="694" y="212" fill="#4a9eff" font-size="9">Plotly charts</text>

  <!-- Footer -->
  <text x="450" y="500" text-anchor="middle" fill="#4a5568" font-size="11">
    Tech stack: Python 3.12 · Pandas · Streamlit · Plotly · pytest
  </text>
  <text x="450" y="518" text-anchor="middle" fill="#4a5568" font-size="11">
    Data: Synthetic (calibrated to CAPMAS 2023 + EFG Hermes Retail Survey 2023)
  </text>
  <text x="450" y="536" text-anchor="middle" fill="#4a5568" font-size="11">
    Regulation: Egyptian Cabinet Decree 1276 (2021) · 9 PM Mandatory Closure
  </text>
</svg>
'''

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "architecture_diagram.svg")
    with open(out, "w") as f:
        f.write(SVG)
    print(f"Architecture diagram saved to: {out}")
