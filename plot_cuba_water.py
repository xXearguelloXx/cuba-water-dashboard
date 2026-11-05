"""
Cuba, NM drinking water (PWSID NM3509023) -- starter plots for ENG220.

Run from this folder:   python plot_cuba_water.py
Needs:                  pandas, matplotlib   (pip install pandas matplotlib)
Writes PNGs to:         figures/
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATA = Path(__file__).parent / "data"
FIGS = Path(__file__).parent / "figures"
FIGS.mkdir(exist_ok=True)

# Palette: fixed categorical order + one reserved "limit" red for regulatory lines
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"]
LIMIT = "#d03b3b"
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"
plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 200, "font.size": 10, "axes.edgecolor": "#c3c2b7",
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titleweight": "bold", "axes.titlesize": 12, "legend.frameon": False,
})

def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIGS / name, bbox_inches="tight")
    plt.close(fig)
    print("wrote", FIGS / name)

# ---------------------------------------------------------------- 1. violations per year, by category
v = pd.read_csv(DATA / "violations_all_years.csv", parse_dates=["determination_date"])
order = ["Contaminant limit exceeded (health-based)", "Treatment technique (health-based)", "Monitoring & reporting",
         "Reporting (CCR)", "Public notice / communication", "Operations / staffing", "Other"]
counts = (v.groupby(["year", "category"]).size().unstack(fill_value=0)
            .reindex(columns=[c for c in order if c in v["category"].unique()])
            .reindex(range(v["year"].min(), v["year"].max() + 1), fill_value=0))
fig, ax = plt.subplots(figsize=(11, 4.8))
bottom = pd.Series(0, index=counts.index)
for col in counts.columns:
    ax.bar(counts.index, counts[col], bottom=bottom, color=C[order.index(col)], label=col, width=0.8,
           edgecolor="white", linewidth=1.5)
    bottom += counts[col]
for yr in (2025, 2026):
    ax.text(yr, bottom[yr] + 0.3, str(int(bottom[yr])), ha="center", va="bottom", color=INK, fontsize=9)
ax.set_title("Cuba Water System: violations by year determined (2026 = Jan-Oct)")
ax.set_ylabel("Number of violations")
ax.set_xticks(counts.index[::2])
ax.legend(loc="upper left", fontsize=8.5)
save(fig, "01_violations_by_year.png")

# ---------------------------------------------------------------- 2. 2025-26 violation timeline
v2 = pd.read_csv(DATA / "violations_2025_2026.csv", parse_dates=["determination_date"])
cats = [c for c in order if c in v2["category"].unique()]
fig, ax = plt.subplots(figsize=(10, 4))
for i, cat in enumerate(cats):
    sub = v2[v2["category"] == cat]
    per_day = sub.groupby("determination_date")
    for d, g in per_day:
        n_open = g["status"].str.startswith("Open").sum()
        n_res = len(g) - n_open
        y = len(cats) - 1 - i
        if n_open:
            ax.scatter(d, y, s=60 + 25 * n_open, color=C[order.index(cat)], zorder=3,
                       edgecolor="white", linewidth=1.5)
            ax.annotate(f"{n_open}", (d, y), xytext=(0, 9), textcoords="offset points", ha="center",
                        fontsize=8, color=INK)
        if n_res:
            ax.scatter(d, y - 0.25, s=50, facecolor="white", edgecolor=C[order.index(cat)], linewidth=2, zorder=3)
ax.set_yticks(range(len(cats)))
ax.set_yticklabels(cats[::-1])
ax.set_ylim(-0.7, len(cats) - 0.4)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.set_title("2025-2026 violations by date determined (filled = still open, hollow = resolved; number = open count)")
save(fig, "02_violation_timeline_2025_2026.png")

# ---------------------------------------------------------------- 3. chlorine residual
cl = pd.read_csv(DATA / "chlorine_residual_monthly_2025_2026.csv", parse_dates=["month_start"])
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(cl["month_start"], cl["monthly_avg_mg_L"], color=C[0], lw=2, marker="o", ms=6, label="Monthly average")
ax.plot(cl["month_start"], cl["running_annual_avg_mg_L"], color=C[1], lw=2, label="Running annual average")
ax.axhline(0.2, color=LIMIT, lw=1.2, ls="--")
ax.text(cl["month_start"].iloc[0], 0.215, "0.2 mg/L - WHO minimum residual guideline", color=LIMIT, fontsize=8.5)
ax.set_ylim(0, 1.15)
ax.set_ylabel("Chlorine residual (mg/L)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.set_title("Disinfectant (chlorine) residual in the distribution system, 2025-2026")
ax.legend(loc="upper right")
ax.text(0.99, 0.02, "EPA maximum (MRDL) = 4.0 mg/L, off scale", transform=ax.transAxes, ha="right", fontsize=8, color=MUTED)
save(fig, "03_chlorine_residual.png")

# ---------------------------------------------------------------- 4. lead & copper 90th percentile history
pb = pd.read_csv(DATA / "lead_copper_90th_percentile_history.csv", parse_dates=["last_sample_date"])
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, an, col, al in [(axes[0], "LEAD", C[0], 0.015), (axes[1], "COPPER", C[2], 1.3)]:
    s = pb[pb["analyte"] == an]
    ax.plot(s["last_sample_date"], s["90th_percentile"], color=col, lw=2, marker="o", ms=6)
    ax.axhline(al, color=LIMIT, lw=1.2, ls="--")
    ax.text(s["last_sample_date"].iloc[0], al * 1.03, f"Action level {al} mg/L", color=LIMIT, fontsize=8.5, va="bottom")
    ax.set_ylim(0, al * 1.25)
    ax.set_title(f"{an.title()} - 90th percentile of tap samples")
    ax.set_ylabel("mg/L")
    ax.set_xlabel("Date of last sample in monitoring period")
save(fig, "04_lead_copper_90th_percentile.png")

# ---------------------------------------------------------------- 5. individual lead tap samples 2025-26
lc = pd.read_csv(DATA / "lead_copper_tap_samples_2025_2026.csv", parse_dates=["sample_date"])
lead = lc[lc["analyte"] == "LEAD"]
fig, ax = plt.subplots(figsize=(10, 4))
det = lead[lead["detected"]]
nd = lead[~lead["detected"]]
ax.scatter(det["sample_date"], det["result_mg_L"] * 1000, s=55, color=C[0], edgecolor="white", lw=1.5,
           zorder=3, label="Detected")
ax.scatter(nd["sample_date"], [0] * len(nd), s=55, marker="v", facecolor="white", edgecolor=MUTED, lw=1.5,
           zorder=3, label="Not detected (below reporting limit)")
ax.axhline(15, color=LIMIT, lw=1.2, ls="--")
ax.text(lead["sample_date"].min(), 15.4, "Lead action level 15 ug/L (applies to the 90th percentile)", color=LIMIT, fontsize=8.5)
top = det.loc[det["result_mg_L"].idxmax()]
ax.annotate(f"{top['result_mg_L']*1000:.0f} ug/L  ({top['sample_date']:%b %d, %Y})",
            (top["sample_date"], top["result_mg_L"] * 1000), xytext=(10, -4), textcoords="offset points", fontsize=8.5)
ax.set_ylabel("Lead (ug/L)")
ax.set_ylim(-1.5, 24)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.set_title("Lead in individual household tap samples, 2025-2026")
ax.legend(loc="upper right")
save(fig, "05_lead_tap_samples.png")

# ---------------------------------------------------------------- 6. detected contaminants vs. their limit
d = pd.read_csv(DATA / "chemical_detections_2025_2026.csv", parse_dates=["sample_date"])
d = d.dropna(subset=["pct_of_limit"]).sort_values("sample_date").drop_duplicates("analyte", keep="last")
d = d.sort_values("pct_of_limit")
NICE = {"TDS": "Total dissolved solids", "PH": "pH", "GROSS ALPHA, EXCL. RADON & U": "Gross alpha",
        "COMBINED RADIUM (-226 & -228)": "Radium-226 + 228", "NITRATE-NITRITE": "Nitrate + nitrite"}
labels = [f"{NICE.get(a, a.title())} ({loc}, {dt:%b %Y})" for a, loc, dt in zip(d["analyte"], d["location"], d["sample_date"])]
colors = [C[0] if t.startswith("MCL") else C[1] for t in d["limit_type"]]
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(labels, d["pct_of_limit"], color=colors, height=0.6, edgecolor="white", linewidth=1.5)
ax.set_xscale("log")
ax.axvline(100, color=LIMIT, lw=1.2, ls="--")
ax.text(105, len(d) - 0.6, "100% = at the limit", color=LIMIT, fontsize=8.5)
for y, val in enumerate(d["pct_of_limit"]):
    ax.text(val * 1.08, y, f"{val:g}%", va="center", fontsize=8, color=INK)
ax.set_xlabel("Result as % of its limit (log scale).  Well #3 = untreated source water; Treatment Plant = entry point")
ax.set_title("Detected contaminants, latest 2025-2026 result vs. its standard")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=C[0], label="Health-based MCL"),
                   Patch(color=C[1], label="Secondary (taste/odor/staining) standard")], loc="lower right")
save(fig, "06_detections_vs_limits.png")

# ---------------------------------------------------------------- 7. NMED 2026 penalty breakdown
pen = pd.read_csv(DATA / "nmed_2026_penalty_breakdown.csv").sort_values("penalty_usd")
fig, ax = plt.subplots(figsize=(10, 4))
ax.barh(pen["violation"], pen["penalty_usd"], color=C[0], height=0.6, edgecolor="white", linewidth=1.5)
ax.set_xscale("log")
for y, val in enumerate(pen["penalty_usd"]):
    ax.text(val * 1.1, y, f"${val:,.0f}", va="center", fontsize=8.5, color=INK)
ax.set_xlabel("Penalty (USD, log scale)")
ax.set_title(f"NMED civil penalty, July 2026 order: ${pen['penalty_usd'].sum():,.0f} total")
ax.set_xlim(right=pen["penalty_usd"].max() * 6)
save(fig, "07_nmed_penalty_breakdown.png")

# ---------------------------------------------------------------- quick text summary
print("\nSummary")
print(" 2025-26 violations:", len(v2), "| open:", v2["status"].str.startswith("Open").sum(),
      "| health-based:", (v2["health_based"] == "Y").sum())
tcr = pd.read_csv(DATA / "coliform_bacteria_samples_2025_2026.csv")
print(" Coliform samples:", len(tcr), "| positives:", int(tcr["total_coliform_present"].sum()))
