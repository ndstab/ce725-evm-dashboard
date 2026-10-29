"""CE725 Earned Value Management Dashboard.

Run:  streamlit run app/streamlit_app.py

The design brief for this screen, in one sentence: a project manager
opening it should know within ten seconds whether the project is in
trouble, and within a minute which work package is causing it and what
the budget is now expected to be.

That ordering drives the layout. The verdict and the plain-language
summary come first, before any index. Indices come next, each with its
consequence beside it. The diagnosis by work package comes before the
forecast, because knowing the EAC without knowing what is driving it
gives a manager nothing to act on.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import evm  # noqa: E402
from app import charts  # noqa: E402
from evm.excel_export import export_workbook  # noqa: E402

CRORE = 1e7
LAKH = 1e5

st.set_page_config(
    page_title="EVM Dashboard — CE725",
    page_icon="chart_with_upwards_trend",
    layout="wide",
)

STYLE = """
<style>
  .block-container { padding-top: 2.2rem; max-width: 1500px; }
  div[data-testid="stMetricValue"] { font-size: 1.45rem; }
  div[data-testid="stMetricLabel"] { font-size: 0.80rem; }
  .verdict {
      padding: 0.85rem 1.2rem; border-radius: 7px; font-weight: 700;
      font-size: 1.05rem; letter-spacing: 0.02em; margin-bottom: 0.6rem;
  }
  .v-bad  { background:#FFEBEE; color:#B71C1C; border-left:6px solid #C62828; }
  .v-warn { background:#FFF8E1; color:#E65100; border-left:6px solid #EF6C00; }
  .v-good { background:#E8F5E9; color:#1B5E20; border-left:6px solid #2E7D32; }
  /* Text colour is set explicitly on every panel. Setting a light
     background without a colour leaves the text inheriting the theme's,
     which renders white-on-white if the browser asks for dark mode. */
  .summary {
      background:#F7F9FB; color:#1A1A1A; border-left:4px solid #5B7C99;
      padding:1rem 1.2rem; border-radius:5px; font-size:1.02rem;
      line-height:1.65;
  }
  .caveat {
      background:#FFFDE7; color:#3E2723; border-left:4px solid #F9A825;
      padding:0.8rem 1rem; border-radius:5px; font-size:0.88rem;
      line-height:1.55;
  }
  .caveat code { background:#FFF3C4; color:#3E2723; padding:0 3px; }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load(data_dir: str) -> evm.Project:
    return evm.load_project(data_dir)


def rupees(value: float) -> str:
    if abs(value) >= CRORE:
        return f"Rs {value / CRORE:,.2f} Cr"
    if abs(value) >= LAKH:
        return f"Rs {value / LAKH:,.2f} L"
    return f"Rs {value:,.0f}"


# ==========================================================================
# Sidebar
# ==========================================================================
with st.sidebar:
    st.markdown("### EVM Dashboard")
    st.caption("CE725 Construction Economics and Finance")

    data_dir = st.text_input("Project data folder", value=str(ROOT / "data"))
    try:
        project = load(data_dir)
    except Exception as error:  # noqa: BLE001 - surfaced to the user verbatim
        st.error(f"Could not load the project.\n\n{error}")
        st.stop()

    st.divider()
    period = st.slider(
        "Reporting period", min_value=1, max_value=project.data_date,
        value=project.data_date,
        help="Move back to see the position as it was reported at the time.",
    )
    st.caption(f"Period {period} — {project.meta.label(period)}")

    st.divider()
    st.markdown("**Forecast assumptions**")
    use_spi_t = st.checkbox(
        "Use SPI(t) in EAC method 3", value=False,
        help=(
            "Classical SPI drifts back towards 1.00 as a project ends, "
            "whatever the delay. SPI(t) does not. Late in a project the "
            "time-based index is the more trustworthy driver."
        ),
    )
    wbs_level = st.radio(
        "Variance breakdown", options=[1, 2, None],
        format_func=lambda v: {1: "Top level", 2: "Sub-level", None: "Work package"}[v],
        index=1, horizontal=True,
    )

    st.divider()
    st.markdown("**Export**")
    if st.button("Build Excel workbook", width="stretch"):
        destination = ROOT / "output" / "EVM_Report.xlsx"
        export_workbook(project, destination)
        st.session_state["export_path"] = str(destination)
    if "export_path" in st.session_state:
        path = Path(st.session_state["export_path"])
        if path.exists():
            st.download_button(
                "Download workbook", path.read_bytes(),
                file_name="EVM_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
            )
            st.caption("Every figure in it is a live formula, not a pasted value.")

    st.divider()
    st.caption(
        f"{len(project.leaves)} work packages · BAC {rupees(project.bac)} · "
        f"{project.n_periods}-period baseline"
    )


# ==========================================================================
# Computation
# ==========================================================================
metrics = evm.metrics_at(project, period)
schedule = evm.earned_schedule(project, period)
spi_for_forecast = schedule.spi_t if use_spi_t else None
forecasts = {f.method: f for f in evm.forecasts(metrics, spi=spi_for_forecast)}
tcpi = evm.tcpi_to_bac(metrics)
status = evm.status_flag(metrics)

# ==========================================================================
# Header, verdict, summary
# ==========================================================================
st.markdown(f"## {project.meta.project_name}")
st.caption(
    f"{project.meta.project_code}  ·  data date: end of Period {period} "
    f"({project.meta.label(period)})  ·  baseline {project.n_periods} months"
)

css_class = {
    "ON TRACK": "v-good",
    "OVERSPENT": "v-warn",
    "BEHIND SCHEDULE": "v-warn",
    "BEHIND SCHEDULE AND OVERSPENT": "v-bad",
    "NOT STARTED": "v-warn",
}[status]
st.markdown(f'<div class="verdict {css_class}">{status}</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="summary">{evm.executive_summary(project, metrics, schedule)}</div>',
    unsafe_allow_html=True,
)
st.write("")

# ==========================================================================
# Headline measures
# ==========================================================================
a, b, c, d = st.columns(4)
a.metric("Earned value (EV)", rupees(metrics.ev),
         f"{metrics.pct_complete:.1f}% complete", delta_color="off")
b.metric("Actual cost (AC)", rupees(metrics.ac),
         f"{metrics.pct_spent:.1f}% of budget spent", delta_color="off")
c.metric("Planned value (PV)", rupees(metrics.pv),
         f"{metrics.pct_scheduled:.1f}% scheduled", delta_color="off")
d.metric("Budget (BAC)", rupees(project.bac),
         f"{len(project.leaves)} work packages", delta_color="off")

a, b, c, d = st.columns(4)
a.metric("Cost variance (CV)", rupees(metrics.cv), f"{metrics.cv_pct:+.1f}% of work done")
b.metric("Schedule variance (SV)", rupees(metrics.sv), f"{metrics.sv_pct:+.1f}% of plan")
c.metric("CPI", f"{metrics.cpi:.3f}", f"{(metrics.cpi - 1) * 100:+.1f}% vs plan")
d.metric("SPI", f"{metrics.spi:.3f}", f"{(metrics.spi - 1) * 100:+.1f}% vs plan")

a, b, c, d = st.columns(4)
a.metric("Earned schedule SPI(t)", f"{schedule.spi_t:.3f}",
         f"{schedule.sv_t * 30:+.0f} days")
b.metric("Forecast at completion", rupees(forecasts["EAC1"].eac),
         f"{forecasts['EAC1'].vac_pct:+.1f}% vs budget")
c.metric("Variance at completion", rupees(forecasts["EAC1"].vac),
         "overrun" if forecasts["EAC1"].vac < 0 else "saving", delta_color="off")
d.metric("TCPI to finish on budget", f"{tcpi:.3f}",
         f"{(tcpi / metrics.cpi - 1) * 100:+.1f}% vs current CPI",
         delta_color="inverse")

st.write("")

# ==========================================================================
# Tabs
# ==========================================================================
tab_curve, tab_trend, tab_variance, tab_forecast, tab_report, tab_data = st.tabs([
    "S-Curve", "Performance trend", "Where the variance is",
    "Forecast", "Monthly report", "Data",
])

with tab_curve:
    st.plotly_chart(charts.s_curve(project, period), width="stretch")
    st.caption(
        "The earned and actual curves stop at the data date; nothing is drawn "
        "beyond it. The dashed tail is an extrapolation, not a measurement. "
        "The vertical gap between PV and EV at the data date is the schedule "
        "variance in money; the gap between EV and AC is the cost variance."
    )
    st.plotly_chart(charts.earned_schedule_chart(project, period), width="stretch")
    st.caption(
        "Earned Schedule read geometrically: drop a line across from current "
        "earned value to the baseline curve, and read off the time underneath. "
        f"The project has earned {schedule.earned_schedule:.2f} periods of "
        f"baseline value in {period} elapsed periods."
    )

with tab_trend:
    st.plotly_chart(charts.index_trend(project, period), width="stretch")
    st.markdown(
        "**Why all three are shown.** CPI and SPI are both measured in money. "
        "As a project approaches completion EV converges on PV whatever the "
        "delay, so SPI returns to 1.00 and SV returns to zero even on a "
        "project finishing a year late — the indices improve and the "
        "improvement is an artefact. SPI(t) is measured in time and does not "
        "have that defect.\n\n"
        "**What to look for in CPI.** Research on large projects has "
        "repeatedly found that CPI stabilises early, often by the 20% "
        "complete point, and rarely recovers. A flat CPI well below 1.00 is "
        "the strongest single argument against an optimistic recovery plan."
    )
    st.dataframe(
        evm.metrics_series(project).loc[:period, [
            "label", "pv", "ev", "ac", "cv", "sv", "cpi", "spi",
        ]].rename(columns={
            "label": "Period", "pv": "PV", "ev": "EV", "ac": "AC",
            "cv": "CV", "sv": "SV", "cpi": "CPI", "spi": "SPI",
        }).style.format({
            "PV": "{:,.0f}", "EV": "{:,.0f}", "AC": "{:,.0f}",
            "CV": "{:,.0f}", "SV": "{:,.0f}", "CPI": "{:.3f}", "SPI": "{:.3f}",
        }),
        width="stretch",
    )

with tab_variance:
    st.plotly_chart(
        charts.variance_by_package(project, period, level=wbs_level), width="stretch"
    )
    breakdown = evm.variance_by_wbs(project, period=period, level=wbs_level)
    breakdown = breakdown[breakdown["ev"] > 0].sort_values("cv")
    st.dataframe(
        breakdown[["key", "name", "budget", "ev", "ac", "cv", "cpi", "pct_complete"]]
        .rename(columns={
            "key": "WBS", "name": "Work package", "budget": "Budget",
            "ev": "EV", "ac": "AC", "cv": "CV", "cpi": "CPI",
            "pct_complete": "% complete",
        })
        .style.format({
            "Budget": "{:,.0f}", "EV": "{:,.0f}", "AC": "{:,.0f}",
            "CV": "{:,.0f}", "CPI": "{:.3f}", "% complete": "{:.1f}%",
        }),
        width="stretch", hide_index=True,
    )
    st.caption(
        "This breakdown is the reason the engine carries the WBS through "
        "rather than aggregating to a single project curve. A project CPI "
        "says something is wrong; only this says which package to go and "
        "look at, and whether its variance is still recoverable."
    )

with tab_forecast:
    st.plotly_chart(charts.forecast_range(project, period), width="stretch")
    st.markdown("#### The four methods differ in one assumption only")
    for f in forecasts.values():
        st.markdown(
            f"**{f.method} — {f.label}**  ·  {rupees(f.eac)}  "
            f"(VAC {rupees(f.vac)}, {f.vac_pct:+.1f}%)  \n"
            f"<span style='color:#555'>{f.assumption}</span>",
            unsafe_allow_html=True,
        )
    st.divider()
    st.markdown("#### Can the budget still be met?")
    st.metric("TCPI to finish on budget", f"{tcpi:.3f}",
              f"current CPI is {metrics.cpi:.3f}", delta_color="off")
    st.info(evm.feasibility_note(tcpi, metrics.cpi))
    st.caption(
        "TCPI is the cost efficiency the REMAINING work must achieve. It is "
        "the sharpest reality check in EVM: compare it with the CPI the "
        "project has actually sustained."
    )

with tab_report:
    commentary = evm.monthly_commentary(project, period, metrics, schedule)
    st.markdown(commentary.as_markdown())
    st.divider()
    st.markdown(
        '<div class="caveat"><b>How this text is produced.</b> It is '
        "generated from templates and thresholds, deterministically. It does "
        "not call a language model. The same inputs produce the same "
        "sentence every month, every figure quoted is one the engine "
        "computed, and each threshold is written down in "
        "<code>evm/commentary.py</code> where it can be argued with. A "
        "language model given a table of indices will readily produce a "
        "fluent paragraph containing a number that is not in the table, "
        "which is not a property a cost report can tolerate.</div>",
        unsafe_allow_html=True,
    )
    st.download_button(
        "Download this month's commentary",
        f"{project.meta.project_name}\n"
        f"Period {period} ({project.meta.label(period)})\n\n"
        f"{evm.executive_summary(project, metrics, schedule)}\n\n"
        f"{commentary.as_text()}\n",
        file_name=f"evm-commentary-period-{period}.txt",
    )

with tab_data:
    st.markdown("#### Work breakdown structure")
    st.dataframe(
        project.wbs[["wbs_id", "parent_id", "name", "is_leaf", "budget_inr"]],
        width="stretch", hide_index=True,
    )
    left, right = st.columns(2)
    with left:
        st.markdown("#### Time-phased budget")
        st.dataframe(project.baseline, width="stretch", hide_index=True, height=320)
    with right:
        st.markdown("#### Reported progress and cost")
        st.dataframe(project.actuals, width="stretch", hide_index=True, height=320)
    st.markdown(
        '<div class="caveat"><b>The limitation that matters most.</b> Earned '
        "value is percent complete multiplied by budget, and percent complete "
        "is a judgement made at site. If a work package is reported at 60% "
        "when it is really 40%, every index on this dashboard is confidently "
        "wrong, and nothing here can detect it. The arithmetic has been "
        "validated against an independent manual benchmark; the "
        "<i>measurements</i> can only be validated at site.</div>",
        unsafe_allow_html=True,
    )
    st.caption(project.meta.notes)
