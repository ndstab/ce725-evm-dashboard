"""Plotly figures for the dashboard.

Charting conventions followed throughout, which are project-control
conventions rather than aesthetic ones:

  The actual and earned curves STOP at the data date. Nothing is drawn
  beyond it. A line that continues past the last reported period invites
  the reader to treat a forecast as a measurement.

  The baseline plateaus at BAC while the forecast runs past the end of the
  baseline, so a delay reads as a horizontal gap between the point where
  the baseline reaches 100% and the point where the forecast does.

  Index axes are pinned rather than auto-scaled. An auto-scaled axis makes
  a CPI of 0.95 look either catastrophic or negligible depending on the
  rest of the series, and makes two periods incomparable.

  Negative is unfavourable everywhere, and unfavourable is red.
"""

from __future__ import annotations

import plotly.graph_objects as go

import evm

CRORE = 1e7

COLOUR_PV = "#5B7C99"    # planned: muted blue, it is the reference
COLOUR_EV = "#2E7D32"    # earned: green, it is the achievement
COLOUR_AC = "#C62828"    # actual cost: red, it is the money gone
COLOUR_FORECAST = "#EF6C00"
GRID = "#E6E6E6"

ADVERSE = "#C62828"
FAVOURABLE = "#2E7D32"


def _layout(fig: go.Figure, title: str, y_title: str, height: int = 420) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15)),
        height=height,
        margin=dict(l=60, r=30, t=60, b=50),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, title=y_title)
    return fig


def s_curve(project: evm.Project, period: int) -> go.Figure:
    """Planned, earned and actual cumulative curves, with a forecast tail."""
    labels = [project.meta.label(p) for p in range(1, project.n_periods + 1)]
    pv = evm.planned_value_curve(project) / CRORE

    series = evm.metrics_series(project)
    reported = list(range(1, period + 1))
    ev = [series.loc[p, "ev"] / CRORE for p in reported]
    ac = [series.loc[p, "ac"] / CRORE for p in reported]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=pv.tolist(), name="PV — planned value",
        line=dict(color=COLOUR_PV, width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=labels[:period], y=ev, name="EV — earned value",
        line=dict(color=COLOUR_EV, width=3),
    ))
    fig.add_trace(go.Scatter(
        x=labels[:period], y=ac, name="AC — actual cost",
        line=dict(color=COLOUR_AC, width=3),
    ))

    # Forecast tail. It shares exactly one point with the actual curve, so
    # it branches from it rather than overlapping it, and it is dashed
    # because it is an extrapolation, not a measurement.
    m = evm.metrics_at(project, period)
    eac = {f.method: f for f in evm.forecasts(m)}["EAC1"].eac
    es = evm.earned_schedule(project, period)
    finish = min(es.independent_eac_time, project.n_periods + 4)
    tail_labels = [labels[period - 1], f"forecast finish ~P{finish:.1f}"]
    fig.add_trace(go.Scatter(
        x=tail_labels, y=[ac[-1], eac / CRORE],
        name=f"Forecast — EAC {eac / CRORE:.2f} Cr at ~P{finish:.1f}",
        line=dict(color=COLOUR_FORECAST, width=2, dash="dash"),
        mode="lines+markers",
        hovertemplate="%{x}<br>Rs %{y:,.2f} crore<extra></extra>",
    ))

    fig.add_hline(
        y=project.bac / CRORE, line=dict(color="#9E9E9E", width=1.5, dash="dot"),
        annotation_text=f"BAC {project.bac / CRORE:.2f} Cr",
        annotation_position="top left",
    )
    fig.add_vline(
        x=period - 1, line=dict(color="#616161", width=1.5, dash="dot"),
        annotation_text="data date", annotation_position="top right",
    )
    return _layout(fig, "S-Curve — planned, earned and actual", "Rs crore", 460)


def index_trend(project: evm.Project, period: int) -> go.Figure:
    """CPI, SPI and SPI(t) over the reported periods.

    The point of plotting all three: CPI typically stabilises early and
    does not recover, which is the single most useful empirical regularity
    in EVM. Seeing it flat for six periods is what justifies distrusting
    an optimistic recovery plan.
    """
    reported = list(range(1, period + 1))
    labels = [project.meta.label(p) for p in reported]
    series = evm.metrics_series(project)

    cpi = [series.loc[p, "cpi"] for p in reported]
    spi = [series.loc[p, "spi"] for p in reported]
    spi_t = [evm.earned_schedule(project, p).spi_t for p in reported]

    fig = go.Figure()
    for values, name, colour in (
        (cpi, "CPI — cost", COLOUR_AC),
        (spi, "SPI — schedule (cost-based)", COLOUR_PV),
        (spi_t, "SPI(t) — schedule (time-based)", COLOUR_EV),
    ):
        fig.add_trace(go.Scatter(
            x=labels, y=values, name=name,
            line=dict(color=colour, width=2.5), mode="lines+markers",
        ))

    fig.add_hline(y=1.0, line=dict(color="#9E9E9E", width=1.5, dash="dot"),
                  annotation_text="on plan", annotation_position="right")
    fig = _layout(fig, "Cost and schedule performance trend", "Index")
    # Pinned, not auto-scaled: periods must be comparable with each other.
    fig.update_yaxes(range=[0.5, 1.2], dtick=0.1)
    return fig


def variance_by_package(project: evm.Project, period: int, level: int | None = None) -> go.Figure:
    """Cost variance by work package.

    The chart a rolled-up S-curve cannot produce. A project CPI says
    something is wrong; this says which package to go and look at.
    """
    breakdown = evm.variance_by_wbs(project, period=period, level=level)
    breakdown = breakdown[breakdown["ev"] > 0].sort_values("cv")
    if breakdown.empty:
        return _layout(go.Figure(), "No work package has earned value yet", "")

    names = [f"{row['key']}  {row['name']}" for _, row in breakdown.iterrows()]
    values = (breakdown["cv"] / 1e5).tolist()

    fig = go.Figure(go.Bar(
        x=values, y=names, orientation="h",
        marker_color=[ADVERSE if v < 0 else FAVOURABLE for v in values],
        text=[f"{v:+,.1f}" for v in values],
        textposition="outside",
        hovertemplate="%{y}<br>Cost variance: Rs %{x:,.2f} lakh<extra></extra>",
    ))
    fig.add_vline(x=0, line=dict(color="#616161", width=1.5))
    fig = _layout(
        fig, "Cost variance by work package (negative is over budget)",
        "", max(360, 60 + 34 * len(names)),
    )
    fig.update_xaxes(title="Cost variance (Rs lakh)")
    fig.update_yaxes(autorange="reversed", title=None)
    return fig


def forecast_range(project: evm.Project, period: int) -> go.Figure:
    """The four EAC methods against BAC.

    Shown together deliberately. A single EAC implies a precision the
    method does not have; the spread is the honest answer.
    """
    m = evm.metrics_at(project, period)
    results = evm.forecasts(m)

    names = [f"{f.method}<br>{f.label}" for f in results]
    values = [f.eac / CRORE for f in results]

    fig = go.Figure(go.Bar(
        x=names, y=values,
        marker_color=[ADVERSE if f.vac < 0 else FAVOURABLE for f in results],
        text=[f"{v:,.2f}" for v in values],
        textposition="outside",
        hovertemplate="%{x}<br>EAC: Rs %{y:,.2f} crore<extra></extra>",
    ))
    fig.add_hline(
        y=project.bac / CRORE, line=dict(color="#1565C0", width=2),
        annotation_text=f"BAC {project.bac / CRORE:.2f} Cr",
        annotation_position="top left",
    )
    fig = _layout(fig, "Forecast cost at completion — four standard methods", "Rs crore")
    lowest = min(values + [project.bac / CRORE])
    highest = max(values)
    fig.update_yaxes(range=[lowest * 0.9, highest * 1.08])
    fig.update_xaxes(tickfont=dict(size=10))
    return fig


def earned_schedule_chart(project: evm.Project, period: int) -> go.Figure:
    """How Earned Schedule is read off the baseline.

    Included because the measure is unfamiliar to most readers and the
    geometry explains it faster than the formula: drop a horizontal line
    from current EV to the baseline curve, and read the time underneath.
    """
    labels = [project.meta.label(p) for p in range(1, project.n_periods + 1)]
    pv = evm.planned_value_curve(project) / CRORE
    m = evm.metrics_at(project, period)
    es = evm.earned_schedule(project, period)
    ev = m.ev / CRORE

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=pv.tolist(), name="Baseline (PV)",
        line=dict(color=COLOUR_PV, width=2.5),
    ))
    fig.add_hline(y=ev, line=dict(color=COLOUR_EV, width=2, dash="dash"),
                  annotation_text=f"EV {ev:.2f} Cr", annotation_position="top left")
    fig.add_vline(x=es.earned_schedule - 1,
                  line=dict(color=COLOUR_EV, width=2, dash="dash"),
                  annotation_text=f"ES = {es.earned_schedule:.2f}",
                  annotation_position="bottom right")
    fig.add_vline(x=period - 1, line=dict(color="#616161", width=2, dash="dot"),
                  annotation_text=f"AT = {period}", annotation_position="top right")
    fig.add_trace(go.Scatter(
        x=[labels[int(es.earned_schedule) - 1], labels[period - 1]], y=[ev, ev],
        name=f"SV(t) = {es.sv_t:.2f} periods",
        line=dict(color=ADVERSE, width=4), mode="lines",
    ))
    return _layout(
        fig,
        "Earned Schedule — reading schedule performance off the baseline in time",
        "Rs crore", 440,
    )
