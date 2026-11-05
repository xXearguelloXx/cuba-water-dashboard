"""
Cuba, NM Drinking Water dashboard (ENG 220 Peace Engineering)

Run locally:   streamlit run app.py
Data:          the CSV files in data/  (pulled Oct 27, 2026 from EPA SDWIS and NMED)
"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "data"
LIMIT_RED = "#d03b3b"
# Same category order and colors as the video figures (plot_cuba_water.py)
CATEGORIES = ["Contaminant limit exceeded (health-based)", "Treatment technique (health-based)",
              "Monitoring & reporting", "Reporting (CCR)", "Public notice / communication",
              "Operations / staffing", "Other"]
CATEGORY_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"]

st.set_page_config(page_title="Cuba, NM Water", page_icon="💧", layout="wide")


# ---------------------------------------------------------------- 1. Load data (cached, so it runs once)
@st.cache_data
def load(name, dates=()):
    return pd.read_csv(DATA / f"{name}.csv", parse_dates=list(dates))


viol_all = load("violations_all_years", ["determination_date"])
viol = load("violations_2025_2026", ["determination_date"])
chlorine = load("chlorine_residual_monthly_2025_2026", ["month_start"])
detections = load("chemical_detections_2025_2026", ["sample_date"])
chem_all = load("chemical_results_2025_2026_long", ["sample_date"])
lead_taps = load("lead_copper_tap_samples_2025_2026", ["sample_date"])
lead_hist = load("lead_copper_90th_percentile_history", ["last_sample_date"])
coliform = load("coliform_bacteria_samples_2025_2026", ["sample_date"])
penalty = load("nmed_2026_penalty_breakdown")
deficiencies = load("significant_deficiencies_2026_order")
system = load("system_info").iloc[0]


def limit_line(value, axis="y"):
    """A dashed red reference line at a regulatory limit."""
    return alt.Chart(pd.DataFrame({axis: [value]})).mark_rule(
        color=LIMIT_RED, strokeDash=[6, 4], size=1.5
    ).encode(**{axis: f"{axis}:Q"})


# ---------------------------------------------------------------- 2. Header and headline numbers
st.title("Cuba, NM Drinking Water")
st.caption(
    f"{system['name'].title()} · ID {system['pwsid']} · {int(system['population_served']):,} people · "
    f"{int(system['service_connections'])} connections · groundwater from 3 wells. "
    f"Data pulled {pd.Timestamp(system['data_pulled']):%B} {pd.Timestamp(system['data_pulled']).day}, "
    f"{pd.Timestamp(system['data_pulled']):%Y} from EPA SDWIS and NMED Drinking Water Watch."
)

is_open = viol["status"].str.startswith("Open")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Violations since Jan 2025", len(viol))
c2.metric("Still open", int(is_open.sum()))
c3.metric("Health-based", int((viol["health_based"] == "Y").sum()))
c4.metric("State penalty (Jul 2026)", f"${penalty['penalty_usd'].sum():,.0f}")
c5.metric("Bacteria tests clean", f"{int((coliform['total_coliform_present'] == 0).sum())} of {len(coliform)}")

tabs = st.tabs(["Violations", "Water quality", "Lead & copper", "Penalty & fixes",
                "Rainfall", "Conservation", "About the data"])

# ---------------------------------------------------------------- 3. Violations tab
with tabs[0]:
    st.subheader("Violations by year")
    lo, hi = int(viol_all["year"].min()), int(viol_all["year"].max())
    years = st.slider("Years", lo, hi, (2004, hi))
    shown = viol_all[viol_all["year"].between(*years)]
    bars = alt.Chart(shown).mark_bar().encode(
        x=alt.X("year:O", title="Year determined"),
        y=alt.Y("count():Q", title="Violations"),
        color=alt.Color("category:N", title="Category",
                        scale=alt.Scale(domain=CATEGORIES, range=CATEGORY_COLORS),
                        legend=alt.Legend(orient="bottom", columns=2, labelLimit=0)),
        tooltip=["year:O", "category:N", "count():Q"],
    ).properties(height=380)
    st.altair_chart(bars, width="stretch")

    st.subheader("Every violation since January 2025")
    status_pick = st.multiselect("Status", sorted(viol["status"].unique()), default=sorted(viol["status"].unique()))
    table = viol[viol["status"].isin(status_pick)]
    st.dataframe(
        table[["determination_date", "plain_english", "category", "health_based", "status", "days_open"]]
        .sort_values("determination_date", ascending=False),
        hide_index=True, width="stretch",
        column_config={"determination_date": st.column_config.DateColumn("Determined"),
                       "plain_english": "What happened", "category": "Category",
                       "health_based": "Health-based", "status": "Status", "days_open": "Days open"},
    )

# ---------------------------------------------------------------- 4. Water quality tab
with tabs[1]:
    left, right = st.columns(2)
    with left:
        st.subheader("Chlorine residual")
        st.caption("Chlorine keeps water safe on its way through the pipes. Red line: WHO's 0.2 mg/L minimum where people collect water.")
        line = alt.Chart(chlorine).mark_line(point=True).encode(
            x=alt.X("month_start:T", title="Month"),
            y=alt.Y("monthly_avg_mg_L:Q", title="mg/L"),
            tooltip=[alt.Tooltip("month_start:T", format="%b %Y"), "monthly_avg_mg_L:Q"],
        )
        st.altair_chart((line + limit_line(0.2)).properties(height=320), width="stretch")
    with right:
        st.subheader("Bacteria (total coliform)")
        st.caption("Every routine sample, January 2025 to October 2026.")
        st.metric("Positive samples", int(coliform["total_coliform_present"].sum()), help="P = present, A = absent")
        st.dataframe(coliform[["sample_date", "sample_type", "total_coliform", "e_coli"]].sort_values("sample_date", ascending=False),
                     hide_index=True, width="stretch", height=250,
                     column_config={"sample_date": st.column_config.DateColumn("Date"), "sample_type": "Type",
                                    "total_coliform": "Total coliform", "e_coli": "E. coli"})

    st.subheader("Detected contaminants vs. their limit")
    st.caption("Latest result for each contaminant, as a percent of its standard (log scale). Over 100% = above the standard.")
    latest = detections.dropna(subset=["pct_of_limit"]).sort_values("sample_date").drop_duplicates("analyte", keep="last")
    latest["kind"] = latest["limit_type"].where(latest["limit_type"].str.startswith("MCL"), "Secondary (taste, odor, staining)")
    latest.loc[latest["kind"].str.startswith("MCL"), "kind"] = "Health-based (MCL)"
    base = alt.Chart(latest).transform_calculate(
        label="format(datum.pct_of_limit, '.3~r') + '%'"
    ).encode(
        y=alt.Y("analyte:N", sort="-x", title=None, axis=alt.Axis(labelLimit=300)),
        x=alt.X("pct_of_limit:Q", title="% of limit (log scale)",
                scale=alt.Scale(type="log", domain=[0.3, 4000]), axis=alt.Axis(values=[1, 10, 100, 1000])),
    )
    dots = base.mark_circle(size=150, opacity=1).encode(
        color=alt.Color("kind:N", title=None, legend=alt.Legend(orient="bottom", labelLimit=0),
                        scale=alt.Scale(domain=["Health-based (MCL)", "Secondary (taste, odor, staining)"],
                                        range=["#2a78d6", "#eb6834"])),
        tooltip=["analyte", "location", alt.Tooltip("sample_date:T", format="%b %d, %Y"),
                 "result", "unit_reported", "limit", "pct_of_limit"],
    )
    labels = base.mark_text(align="left", dx=11, color="#3d3d3a").encode(text="label:N")
    pct = dots + labels
    st.altair_chart((pct + limit_line(100, "x")).properties(height=380), width="stretch")

    with st.expander("Look up any contaminant (all 2025-2026 results, including non-detects)"):
        pick = st.selectbox("Contaminant", sorted(chem_all["analyte"].unique()))
        st.dataframe(chem_all[chem_all["analyte"] == pick][["sample_date", "location", "detected", "result",
                                                             "unit_reported", "reporting_limit", "limit", "limit_type"]],
                     hide_index=True, width="stretch")

# ---------------------------------------------------------------- 5. Lead & copper tab
with tabs[2]:
    metal = st.radio("Metal", ["LEAD", "COPPER"], horizontal=True, format_func=str.title)
    action = 15.0 if metal == "LEAD" else 1300.0      # action levels in micrograms per liter
    left, right = st.columns(2)
    with left:
        st.subheader("Official 90th percentile, 2005-2026")
        st.caption("This is the number compliance is based on. Red line: action level.")
        h = lead_hist[lead_hist["analyte"] == metal].assign(ug_L=lambda d: d["90th_percentile"] * 1000)
        hl = alt.Chart(h).mark_line(point=True).encode(
            x=alt.X("last_sample_date:T", title="Monitoring period (last sample)"),
            y=alt.Y("ug_L:Q", title="µg/L", scale=alt.Scale(domain=[0, action * 1.2])),
            tooltip=[alt.Tooltip("last_sample_date:T", format="%b %Y"), "ug_L:Q", "n_samples:Q"],
        )
        st.altair_chart((hl + limit_line(action)).properties(height=320), width="stretch")
    with right:
        st.subheader("Individual tap samples, 2025-2026")
        st.caption("Non-detects are plotted at 0. One high tap is not a violation on its own.")
        t = lead_taps[lead_taps["analyte"] == metal].assign(
            ug_L=lambda d: d["result_mg_L_nd_as_zero"] * 1000,
            result=lambda d: d["detected"].map({True: "Detected", False: "Below detection limit"}))
        pts = alt.Chart(t).mark_circle(size=70).encode(
            x=alt.X("sample_date:T", title="Sample date"),
            y=alt.Y("ug_L:Q", title="µg/L"),
            color=alt.Color("result:N", title=None, legend=alt.Legend(orient="bottom"),
                            scale=alt.Scale(domain=["Detected", "Below detection limit"], range=["#2a78d6", "#b9b8b1"])),
            tooltip=[alt.Tooltip("sample_date:T", format="%b %d, %Y"), "ug_L:Q", "result:N"],
        )
        st.altair_chart((pts + limit_line(action)).properties(height=320), width="stretch")

# ---------------------------------------------------------------- 6. Penalty & fixes tab
with tabs[3]:
    st.subheader(f"NMED Order 2026-DW-ACOP-02: ${penalty['penalty_usd'].sum():,.0f} civil penalty")
    pbase = alt.Chart(penalty).encode(
        y=alt.Y("violation:N", sort="-x", title=None, axis=alt.Axis(labelLimit=420)),
        x=alt.X("penalty_usd:Q", title="Penalty (USD)", scale=alt.Scale(domain=[0, 150000])),
    )
    pb = (pbase.mark_bar().encode(tooltip=["violation", alt.Tooltip("penalty_usd:Q", format="$,.0f"), "gravity", "days_counted"])
          + pbase.mark_text(align="left", dx=5, color="#3d3d3a").encode(text=alt.Text("penalty_usd:Q", format="$,.0f"))
          ).properties(height=300)
    st.altair_chart(pb, width="stretch")

    st.subheader("The 14 problems the state ordered fixed")
    comp = st.multiselect("Component", sorted(deficiencies["component"].unique()),
                          default=sorted(deficiencies["component"].unique()))
    st.dataframe(deficiencies[deficiencies["component"].isin(comp)][
                     ["description", "facility", "component", "days_to_correct_after_order"]],
                 hide_index=True, width="stretch",
                 column_config={"description": "Problem", "facility": "Where", "component": "Part of system",
                                "days_to_correct_after_order": "Days allowed to fix"})

# ---------------------------------------------------------------- 7. Placeholder tabs for teammates
with tabs[4]:
    st.subheader("Rainfall")
    st.info("Coming soon. To add it: put a CSV in data/ (for example rainfall_monthly.csv), "
            "load it at the top of app.py with load(), and draw it here.")
with tabs[5]:
    st.subheader("Conservation")
    st.info("Coming soon. Same steps as the Rainfall tab.")

# ---------------------------------------------------------------- 8. About the data
with tabs[6]:
    st.subheader("Sources")
    st.markdown(
        "- [NMED Drinking Water Watch: Cuba Water System](https://dww.water.env.nm.gov/JSP/WaterSystemDetail.jsp?tinwsys_is_number=454&tinwsys_st_code=NM)\n"
        "- [EPA Envirofacts SDWIS: violations for NM3509023](https://data.epa.gov/efservice/VIOLATION/PWSID/NM3509023/JSON)\n"
        "- [NMED Administrative Compliance Order 2026-DW-ACOP-02](https://cloud.env.nm.gov/resources/_translator.php/YTgzMDg5MjQ0YThjZTMwZDViNmU2M2ViN18yMzQ5OTY~.pdf)\n"
        "- [WHO Technical Note 11: Measuring chlorine levels in water supplies](https://wedc-knowledge.lboro.ac.uk/resources/who_notes/WHO_TNE_11_Measuring_chlorine_levels_in_water_supplies.pdf)"
    )
    st.subheader("Things to know")
    st.markdown(
        "- Health-based limits (MCLs) protect health. Secondary standards cover taste, odor and staining.\n"
        "- Lead and copper compliance uses the 90th percentile of tap samples, not any single tap.\n"
        "- Well #3 results are untreated source water, not necessarily what reaches homes.\n"
        "- The two newest violations are in the state database but not yet in EPA's copy."
    )
    st.subheader("Download the data")
    for f in sorted(DATA.glob("*.csv")):
        st.download_button(f.name, f.read_bytes(), file_name=f.name, mime="text/csv", key=f.name)
