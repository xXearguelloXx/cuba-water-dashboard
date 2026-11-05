# Cuba, NM Drinking Water Data, 2025–2026 (ENG220 Peace Engineering)

Water quality and compliance data for the **Cuba Water System** (Village of Cuba, Sandoval County, NM), the community system serving about **1,789 people through 660 connections** from **three groundwater wells**. Federal ID (PWSID): **NM3509023**. Data pulled **October 27, 2026**.

Every file in `data/` is a tidy CSV (one row per observation, ISO dates `YYYY-MM-DD`), so it loads directly with `pandas.read_csv` or MATLAB `readtable`.

## Quick start

```bash
pip install pandas matplotlib
python plot_cuba_water.py        # writes 7 PNGs to figures/
```
MATLAB (R2020a+): open `plot_cuba_water.m` with this folder as the current folder and press Run (writes to `figures_matlab/`).

### Streamlit dashboard (added Nov 5, 2026)

```bash
pip install -r requirements.txt
streamlit run app.py             # opens http://localhost:8501
```
`app.py` is the public dashboard page (7 tabs: violations, water quality, lead & copper, penalty & fixes, rainfall, conservation, about the data). Deploy it free on Streamlit Community Cloud (share.streamlit.io) from a GitHub repo; see the setup tutorial doc.

### Video assets (added Nov 5, 2026)

```bash
python make_video_figures.py     # writes figures/08_gantt_chart.png and figures/09_method_pipeline.png (1920x1080)
```
- `milestones.csv` drives the Gantt chart. Its dates are **proposed**: replace them with your team's real dates and re-run. Rows starting with `MILESTONE:` are drawn as diamonds. `status` must be `Done`, `In progress` or `Planned`.
- `data/raw_2026-10-27/` holds the raw JSON pulls from EPA and NMED, saved on the pull date. Personal contact details and sampling-site street addresses have been removed.

## Files

| File | Rows | What it is | Good plot |
|---|---|---|---|
| `violations_2025_2026.csv` | 28 | Every violation NMED determined Jan 2025 – Oct 2026 | Timeline / bar by category / open vs. resolved |
| `violations_all_years.csv` | 149 | Same columns, full history 1994–2026 | Stacked bar by year |
| `chemical_results_2025_2026_long.csv` | 243 | Every lab result (detects and non-detects) | Filter by analyte |
| `chemical_detections_2025_2026.csv` | 19 | Only the results that were detected (excl. lead/copper) | % of limit bar chart |
| `lead_copper_tap_samples_2025_2026.csv` | 106 | Individual household tap samples for lead & copper | Strip/scatter vs. action level |
| `lead_copper_90th_percentile_history.csv` | 22 | Official 90th-percentile results by monitoring period, 2005–2026 | Line vs. action level |
| `chlorine_residual_monthly_2025_2026.csv` | 21 | Monthly disinfectant residual (Jan 2025 – Sep 2026) | Line chart |
| `coliform_bacteria_samples_2025_2026.csv` | 44 | Total coliform / E. coli tests (A = absent, P = present) | Count / calendar |
| `nmed_2026_penalty_breakdown.csv` | 7 | Penalty line items from NMED's July 14, 2026 compliance order | Bar chart |
| `significant_deficiencies_2026_order.csv` | 14 | Infrastructure problems NMED ordered fixed | Table / count by component |
| `system_info.csv` | 1 | Population, connections, source | Title slide facts |

## Key columns

**Violations:** `determination_date` (when the state recorded it) · `violation_code` / `violation_name` (EPA SDWIS code) · `plain_english` · `category` · `health_based` (Y = MCL or treatment-technique violation) · `rule` · `compl_per_begin_date` (the compliance period the violation is about, can be years earlier) · `status` · `rtc_date` (returned to compliance) · `days_open` (to RTC date, or to Oct 27, 2026 if still open) · `data_note`.

**Chemical results:** `sample_date` · `location` (Treatment Plant = water entering the system; Distribution System = household taps; Well # 3 = untreated source water) · `analyte` · `detected` · `result` + `unit_reported` (as the lab reported it) · `result_mg_L` (converted to mg/L where possible) · `reporting_limit` (for non-detects) · `limit`, `limit_type`, `limit_unit`, `pct_of_limit`.

**Limits used:** EPA primary MCLs (health-based), lead/copper action levels (0.015 / 1.3 mg/L, applied to the 90th percentile, not single taps), and EPA secondary standards (aesthetic: taste, odor, staining). Chlorine rows include EPA's maximum residual (4.0 mg/L) and the WHO minimum-residual guideline (0.2 mg/L) as reference lines.

## What the data shows

1. **28 violations in 2025–2026; 21 still open.** 12 are health-based treatment-technique violations under the Ground Water Rule: significant deficiencies from the Aug 21, 2024 sanitary survey not corrected within 120 days (recorded Feb 5, 2025). The rest are reporting and public-notice failures, plus operating without a certified operator (June 29, 2026).
2. **NMED penalty: $134,740** (order 2026-DW-ACOP-02, July 14, 2026). $129,080 of it (96%) is for uncorrected deficiencies dating back to the 2018, 2021 and 2024 surveys. The 14 listed deficiencies include a corroding storage tank, distribution pressure as low as 20 psi, an unsealed wellhead and cross-connections at a well and a booster station.
3. **No bacteria detected:** 44 coliform/E. coli samples, all absent.
4. **No health-based contaminant limit exceeded** in 2025–2026. Barium, fluoride, nitrate, radium and gross alpha were detected, all well under their MCLs. All tested organics (VOCs, pesticides) were non-detect.
5. **Lead:** the 90th percentile stayed under the 15 µg/L action level in every period. One tap sample reached **21 µg/L** (Dec 10, 2025). Because compliance is based on the 90th percentile, a single high tap is not a violation.
6. **Chlorine residual dropped** from 0.8–1.0 mg/L in early 2025 to **0.06–0.07 mg/L** in July and September 2026, below the WHO 0.2 mg/L guideline. This is not recorded as a violation, but low residual means less protection against bacterial regrowth in the pipes.
7. **Well #3 source water (July 2025):** manganese **0.90 mg/L**, 18× the EPA secondary standard (0.05 mg/L) and 3× EPA's lifetime health advisory (0.3 mg/L). Total dissolved solids were 566 mg/L (standard 500). This is untreated well water, not necessarily what reaches taps.
8. **No disinfection byproduct (TTHM/HAA5) samples** appear in the state database for 2025. The most recent result on record is from 2023.

## Caveats for your write-up

- **Two databases.** The NMED Drinking Water Watch is the live state record. EPA's federal SDWIS copy lags behind: the two newest violations (June and Sept 2026) and 33 older records (mostly 1994–2013) exist only in the state database. Those older ones have no resolution date.
- **Dates.** Some violations cite old compliance periods (e.g., lead notices for 2010–2021) but were only determined in 2025. Filter on `determination_date` for "what happened in 2025–26" and on `compl_per_begin_date` for "what period it covers."
- **Units.** The lab reported copper and lead in both µg/L and mg/L. Use `result_mg_L` for consistent plots.
- **Non-detects** have a blank `result` and a `reporting_limit`. The lead/copper file also provides `result_mg_L_nd_as_zero` for plotting.
- Radium and gross alpha show identical values across three 2025 quarters. This is as recorded by the state.

## Sources

- NMED Drinking Water Watch, Cuba Water System: https://dww.water.env.nm.gov/JSP/WaterSystemDetail.jsp?tinwsys_is_number=454&tinwsys_st_code=NM (violations, chemical results, coliform, chlorine, lead/copper summaries)
- EPA Envirofacts SDWIS API: https://data.epa.gov/efservice/VIOLATION/PWSID/NM3509023/JSON (also the `ENFORCEMENT_ACTION`, `VIOLATION_ENF_ASSOC`, `LCR_SAMPLE`, `LCR_SAMPLE_RESULT`, `WATER_SYSTEM`, `WATER_SYSTEM_FACILITY` tables). Replace `/JSON` with `/CSV` to download a table directly.
- NMED Administrative Compliance Order 2026-DW-ACOP-02 (July 14, 2026): https://cloud.env.nm.gov/resources/_translator.php/YTgzMDg5MjQ0YThjZTMwZDViNmU2M2ViN18yMzQ5OTY~.pdf
- Village of Cuba, 2025 Consumer Confidence Report (scanned): https://www.cubanm.gov/july-7-2026-water-quality-report-2025-consumer-confidence-report/
