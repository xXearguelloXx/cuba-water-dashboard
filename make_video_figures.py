"""
Two extra figures for the video: a Gantt chart (rubric: timeline and milestones) and a
methodology pipeline graphic. Both are 1920x1080 so they fill a 16:9 frame.

Edit milestones.csv with your team's real dates, then run:   python make_video_figures.py
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch, Patch
from matplotlib.lines import Line2D

HERE = Path(__file__).parent
FIGS = HERE / "figures"
FIGS.mkdir(exist_ok=True)
TODAY = pd.Timestamp("today").normalize()


def md(ts):
    """Month and day without a leading zero, e.g. Oct 7 (works on Windows, Mac and Linux)."""
    ts = pd.Timestamp(ts)
    return f"{ts:%b} {ts.day}"


INK, MUTED, GRID, EDGE = "#0b0b0b", "#6b6a64", "#e1e0d9", "#c3c2b7"
STATUS = {"Done": "#2a78d6", "In progress": "#eb6834", "Planned": "#b9b8b1"}
plt.rcParams.update({"font.size": 15, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False, "axes.edgecolor": EDGE, "xtick.color": MUTED,
                     "ytick.color": INK, "legend.frameon": False})

# ---------------------------------------------------------------- Gantt chart
m = pd.read_csv(HERE / "milestones.csv", parse_dates=["start", "end"])
is_ms = m["task"].str.startswith("MILESTONE:")
tasks, ms = m[~is_ms].reset_index(drop=True), m[is_ms].copy()
ms["label"] = ms["task"].str.replace("MILESTONE:", "", regex=False).str.strip()

fig, ax = plt.subplots(figsize=(12, 6.75), dpi=160)
ms = ms.sort_values("start").reset_index(drop=True)
rows = [("ms", r) for _, r in ms.iterrows()] + [("task", r) for _, r in tasks.iterrows()]
n = len(rows)
labels = []
for i, (kind, r) in enumerate(rows):
    y = n - 1 - i
    if kind == "ms":
        ax.plot(r["start"], y, marker="D", ms=14, color=STATUS[r["status"]], mec="white", mew=2, zorder=4)
        ax.text(r["start"] + pd.Timedelta(days=2.5), y, md(r["start"]), va="center", fontsize=13,
                color=INK, fontweight="bold", zorder=5,
                bbox=dict(fc="white", ec="none", pad=1.5))
        labels.append(r["label"])
    else:
        width = max((r["end"] - r["start"]).days, 1)
        ax.barh(y, width, left=r["start"], height=0.56, color=STATUS[r["status"]], edgecolor="white", linewidth=2)
        if isinstance(r["owner"], str):
            ax.text(r["end"] + pd.Timedelta(days=1.5), y, r["owner"], va="center", fontsize=12, color=MUTED, zorder=5,
                    bbox=dict(fc="white", ec="none", pad=1.5))
        labels.append(r["task"])
ax.set_yticks(range(n))
ax.set_yticklabels(labels[::-1])
for t, (kind, _) in zip(ax.get_yticklabels(), rows[::-1]):
    if kind == "ms":
        t.set_fontweight("bold")
ax.axhline(n - len(ms) - 0.5, color=EDGE, lw=1)
ax.tick_params(axis="y", length=0)

lo = m["start"].min() - pd.Timedelta(days=4)
hi = m["end"].max() + pd.Timedelta(days=16)
if lo <= TODAY <= hi:
    ax.axvline(TODAY, color="#d03b3b", lw=1.6, ls="--", zorder=2)
    ax.text(TODAY, n - 0.35, f"Today, {md(TODAY)}", color="#d03b3b", ha="center", va="bottom", fontsize=12)
ax.set_xlim(lo, hi)
ax.set_ylim(-0.7, n + 0.2)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: md(mdates.num2date(x).replace(tzinfo=None))))
plt.setp(ax.get_xticklabels(), fontsize=12)
ax.grid(axis="x", color=GRID, lw=0.8)
ax.set_axisbelow(True)
fig.suptitle("Project timeline and milestones", x=0.02, ha="left", fontsize=22, fontweight="bold")
ax.legend(handles=[Patch(color=c, label=s) for s, c in STATUS.items()] +
          [Line2D([], [], marker="D", ls="", color=INK, ms=10, label="Milestone")],
          loc="upper left", ncol=4, fontsize=12, bbox_to_anchor=(0, -0.07))
fig.tight_layout()
fig.savefig(FIGS / "08_gantt_chart.png", dpi=160)
plt.close(fig)
print("wrote", FIGS / "08_gantt_chart.png")

# ---------------------------------------------------------------- methodology pipeline
fig = plt.figure(figsize=(12, 6.75), dpi=160)
ax = fig.add_axes([0, 0, 1, 1])          # 1 unit = 16 px in both directions
ax.set_xlim(0, 120); ax.set_ylim(0, 67.5); ax.axis("off")
ax.text(4, 63.5, "How we built the data", fontsize=24, fontweight="bold", color=INK, va="top")
ax.text(4, 58.3, "Three public sources, one Python pipeline, one dashboard page", fontsize=15, color=MUTED, va="top")

def box(x, y, w, h, title, lines, accent=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2",
                                fc="#eaf2fc" if accent else "white", ec="#2a78d6" if accent else EDGE,
                                lw=2.2 if accent else 1.4))
    ax.text(x + w / 2, y + h - 2.4, title, ha="center", va="top", fontsize=15, fontweight="bold", color=INK)
    for k, line in enumerate(lines):
        ax.text(x + w / 2, y + h - 6.4 - 2.9 * k, line, ha="center", va="top", fontsize=12.5, color=MUTED)

def arrow(x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color="#898781", lw=1.6, mutation_scale=18))

src = [("EPA SDWIS", ["Federal violation records"]),
       ("NMED Drinking Water Watch", ["State lab results, violations,", "chlorine, lead and copper"]),
       ("NMED compliance order", ["July 2026 penalty and", "14 listed deficiencies"])]
for (t, l), y in zip(src, [39, 24, 9]):
    box(4, y, 35, 12.5, t, l)
    arrow(39.5, y + 6.25, 45.5, 28)
box(46, 16.5, 25, 23, "Python + pandas", ["Merge by violation ID", "Convert units", "Flag non-detects", "Attach legal limits"], accent=True)
arrow(71.5, 28, 76.5, 28)
box(77, 21, 17, 14, "11 CSV files", ["Tidy, one row", "per result"])
arrow(94.5, 28, 97.5, 37.5)
arrow(94.5, 28, 97.5, 18.5)
box(98, 32, 20, 11, "Charts", ["Python and MATLAB"])
box(98, 13, 20, 11, "Streamlit page", ["Public dashboard"], accent=True)
ax.text(4, 3.5, "Every pull is saved with its date in data/raw_2026-10-27/", fontsize=12, color=MUTED)
fig.savefig(FIGS / "09_method_pipeline.png", dpi=160)
plt.close(fig)
print("wrote", FIGS / "09_method_pipeline.png")
