# Al-Nour Retail Decision Support System

**Retail Revenue Analysis, Staffing Recommendations, and What-If Planning with Streamlit**

A Python decision support application for an illustrative Cairo clothing boutique. The dashboard uses synthetic transactions, foot traffic, staffing, and competitor activity to explore the effects of an earlier closing time and compare operational scenarios.

The 21:00 closing time is a project assumption. This repository does not verify current Egyptian operating-hour regulations.

## Features

- KPI overview and before/after scenario comparisons
- Hourly revenue and weekly activity visualizations
- Power-hour identification using weighted transaction and ticket-value scores
- Rule-based staffing recommendations
- What-if simulations for closing times, discounts, and marketing spend
- Synthetic competitor activity gap analysis
- Revenue forecasting using exponential smoothing and a recent linear trend
- Seasonal-event helpers and illustrative Ramadan/Eid scenarios
- HTML project report and SVG architecture diagram
- Command-line briefing and pytest suite

## Dashboard Pages

| Page | Purpose |
|---|---|
| Overview | Revenue, transaction, conversion, and category KPIs |
| Power Hours | Rank trading hours and display operational recommendations |
| Staffing | Estimate staffing needs using visitor-to-staff ratios |
| What-If Simulator | Compare closing-time and promotion assumptions |
| Competitor Intel | Compare synthetic competitor activity with shop scores |
| Forecast | Display a 30-day revenue projection |

## Architecture

The application follows a Model-View-Controller structure:

- `data/`: synthetic data and generation code
- `models/analytics.py`: data loading, KPIs, forecasting, staffing, and simulations
- `controllers/dashboard_controller.py`: interface between analytics and dashboard
- `views/app.py`: Streamlit interface
- `utils/`: CLI briefing, report generation, seasonal calendar, and diagram generation
- `tests/test_analytics.py`: analytics and seasonal-calendar tests
- `reports/`: bundled HTML report and architecture diagram
- `index.html`: bundled static project presentation
- `run.py`: data checks, tests, report generation, and dashboard launcher

## Data

All bundled datasets are synthetic demonstration data, not verified boutique transactions or independently collected competitor measurements.

| File | Bundled rows |
|---|---:|
| `data/pos_transactions.csv` | 60,335 |
| `data/foot_traffic.csv` | 6,720 |
| `data/staffing.csv` | 1,440 |
| `data/competitor_activity.csv` | 26,880 |

The generator covers January 2025 through April 2026. It uses predefined traffic patterns, prices, seasonal multipliers, and random variation. External reports named in legacy comments and generated presentations have not been independently verified as calibration sources.

## Setup

Use Python 3.12, matching the package configuration and the supplied dependency pins.

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

## Run the Dashboard

```bash
streamlit run views/app.py
```

Open `http://localhost:8501` in your browser. Run commands from the repository root so relative data paths resolve correctly.

Alternatively:

```bash
python run.py
```

The launcher checks for data, runs tests, regenerates reports, and launches Streamlit. It prints a warning and continues if tests fail; review the test output.

## Other Commands

Run the supplied tests:

```bash
python -m pytest tests/ -v
```

Regenerate synthetic datasets:

```bash
python data/generate_data.py
```

This overwrites the four CSVs. Review the generator inconsistencies below before regenerating.

Generate project documentation:

```bash
python utils/generate_report.py
python utils/generate_architecture_diagram.py
```

## Model Assumptions and Known Issues

- **Data generator mismatch:** `get_hourly_dist()` checks for 2024, while scenario labels mark 2026 as the post-change year. The bundled 2026 POS data includes 2,937 transactions at or after 21:00. Reconcile generation and filtering before interpreting the scenario as closed after 21:00.
- **Revenue aggregation:** several fields called hourly revenue use mean transaction values, rather than average hourly revenue totals. Revenue-loss and extended-hours estimates inherit this distinction.
- **Discount simulation:** the fixed 35% volume uplift is applied to the selected window even when the discount is zero. It is an assumption, not a fitted customer-response model.
- **Forecast bands:** the displayed bounds are fixed at plus/minus 7%, not statistically calibrated confidence intervals. No held-out forecast accuracy is supplied.
- **Staffing:** recommendations use fixed visitor-to-staff ratios rather than a constrained scheduling optimization model.
- **Seasonal effects:** event multipliers and dates are configured assumptions. Some older source comments associate Ramadan with April; these comments are not a reliable event calendar.
- **Legacy materials:** bundled reports and static pages preserve the submitted project and may contain older counts, dates, legal descriptions, or test claims. Use this README for the packaging validation status.

## Validation During Packaging

- All project Python files passed syntax parsing.
- Data loading, 2026 KPI computation, 30-day forecasting, power-hour identification, staffing recommendations, competitor gaps, and a what-if scenario completed successfully.
- Checks used the available pandas 2.2.3 / NumPy 2.3.5 environment, rather than a fresh installation of the pinned requirements.
- All 20 supplied pytest tests passed. Interactive browser validation was not completed. These tests do not resolve the modeling and data inconsistencies documented above.

## Technologies

Python, Streamlit, pandas, NumPy, Plotly, and pytest.

## Project Context

Decision Support Systems course project B-01, using Al-Nour Fashion Boutique as its demonstration business. The package preserves the supplied application source and data; the README was rewritten to describe the current implementation and its limits.
