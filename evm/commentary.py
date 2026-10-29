"""Plain-language monthly progress commentary.

The brief asks for automatic plain-language commentary. This module
generates it from templates and thresholds, deterministically. It does not
call a language model, and that is a deliberate decision rather than a
limitation we failed to overcome.

Three reasons:

  Reproducible. The same inputs must produce the same sentence every
  month. A cost report that a client or a lender reads has to be
  defensible line by line, and "the model phrased it differently this
  time" is not a defence.

  Non-inventing. A language model given a table of indices will readily
  produce a fluent paragraph containing a number that is not in the table.
  Every figure in the output below is interpolated from a computed value;
  there is no path by which a number can enter the text without having
  been calculated first.

  Auditable. Each sentence is traceable to a threshold that is written
  down in this file and justified. A reader who disagrees with the
  "behind schedule" cut-off can find it and argue with it.

Where a language model does earn its place in this project is upstream of
the commentary -- in drafting these templates, in checking formula logic,
and in writing code -- not in generating the numbers a decision rests on.
That distinction is the project's main argument about AI in professional
practice.

The thresholds below are a reporting convention, not a standard. The 0.95
band in particular is the common practice of treating performance within
five percent of plan as noise rather than signal on a monthly construction
report; it would be too loose on a short fit-out and too tight on a
long-duration infrastructure contract.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .core import PeriodMetrics, variance_by_wbs
from .dataset import Project
from .earned_schedule import EarnedScheduleResult
from .forecasting import feasibility_note, forecasts, tcpi_to_bac

# Index bands used throughout the commentary.
GOOD = 1.00      # at or above plan
WATCH = 0.95     # within five percent of plan: worth watching, not alarming
POOR = 0.90      # materially off plan

DAYS_PER_PERIOD = 30.0


def _crore(value: float) -> str:
    """Indian currency formatting. Construction reporting here uses crore
    and lakh, not millions, and a report that uses the wrong unit gets
    read with the wrong order of magnitude."""
    if abs(value) >= 1e7:
        return f"Rs {value / 1e7:,.2f} crore"
    if abs(value) >= 1e5:
        return f"Rs {value / 1e5:,.2f} lakh"
    return f"Rs {value:,.0f}"


def _band(index: float) -> str:
    """Verbal band for an index.

    Worded with "below plan" rather than "behind plan" so the same wording
    serves a cost index and a schedule index. A cost index is never
    "behind".
    """
    if not math.isfinite(index):
        return "not assessable"
    if index >= GOOD:
        return "at or above plan"
    if index >= WATCH:
        return "marginally below plan"
    if index >= POOR:
        return "below plan"
    return "significantly below plan"


def status_flag(metrics: PeriodMetrics) -> str:
    """One-line traffic-light verdict for the top of a report."""
    cpi, spi = metrics.cpi, metrics.spi
    if not (math.isfinite(cpi) and math.isfinite(spi)):
        return "NOT STARTED"
    over = cpi < WATCH
    late = spi < WATCH
    if over and late:
        return "BEHIND SCHEDULE AND OVERSPENT"
    if over:
        return "OVERSPENT"
    if late:
        return "BEHIND SCHEDULE"
    return "ON TRACK"


@dataclass
class Commentary:
    period_label: str
    status: str
    paragraphs: list[str]

    def as_text(self) -> str:
        return "\n\n".join(self.paragraphs)

    def as_markdown(self) -> str:
        body = "\n\n".join(self.paragraphs)
        return f"**{self.period_label} — {self.status}**\n\n{body}"


def _cost_paragraph(m: PeriodMetrics) -> str:
    direction = "under" if m.cv >= 0 else "over"
    return (
        f"Work worth {_crore(m.ev)} has been completed against an actual spend of "
        f"{_crore(m.ac)}, a cost variance of {_crore(abs(m.cv))} {direction} budget "
        f"({abs(m.cv_pct):.1f}% of the work done). The cost performance index is "
        f"{m.cpi:.3f}, which is {_band(m.cpi)}: every rupee spent is returning "
        f"{m.cpi:.2f} rupees of budgeted work."
    )


def _schedule_paragraph(m: PeriodMetrics, es: EarnedScheduleResult) -> str:
    direction = "ahead of" if m.sv >= 0 else "behind"
    days = abs(es.sv_t) * DAYS_PER_PERIOD
    return (
        f"Against a plan of {_crore(m.pv)} by this date, the schedule variance is "
        f"{_crore(abs(m.sv))} {direction} plan and the schedule performance index "
        f"is {m.spi:.3f}. Measured in time rather than money, earned schedule is "
        f"{es.earned_schedule:.2f} periods against {es.actual_time:.0f} elapsed, so "
        f"the project is about {days:.0f} days {direction} plan "
        f"(SPI(t) = {es.spi_t:.3f}). At this rate the {es.planned_duration:.0f}-period "
        f"baseline finishes in {es.independent_eac_time:.1f} periods, an overrun of "
        f"{abs(es.forecast_overrun):.1f} periods."
    )


def _forecast_paragraph(m: PeriodMetrics) -> str:
    results = {f.method: f for f in forecasts(m)}
    optimistic, central, pessimistic = results["EAC2"], results["EAC1"], results["EAC3"]
    tcpi = tcpi_to_bac(m)
    return (
        f"Forecast cost at completion ranges from {_crore(optimistic.eac)} if the "
        f"variance to date proves to be a one-off, through {_crore(central.eac)} if "
        f"current cost performance continues, to {_crore(pessimistic.eac)} if "
        f"schedule pressure continues to carry cost with it. Against a budget of "
        f"{_crore(m.bac)} the central case is an overrun of "
        f"{_crore(abs(central.vac))} ({abs(central.vac_pct):.1f}%). Finishing on "
        f"budget would require the remaining work to run at a cost efficiency of "
        f"{tcpi:.3f}. {feasibility_note(tcpi, m.cpi)}"
    )


def _diagnosis_paragraph(project: Project, period: int) -> str:
    """Name the packages driving the variance.

    This is the sentence a rolled-up S-curve cannot write, and the reason
    the engine carries the WBS through rather than aggregating early.
    """
    breakdown = variance_by_wbs(project, period=period, level=2)
    started = breakdown[breakdown["ev"] > 0].copy()
    if started.empty:
        return "No work package has earned value yet, so no variance can be attributed."

    worst = started.nsmallest(min(3, len(started)), "cv")
    parts = []
    for _, row in worst.iterrows():
        if row["cv"] >= 0:
            continue
        complete = row["pct_complete"]
        state = "complete, so this variance is final" if complete >= 99.95 else (
            f"{complete:.0f}% complete, so it can still move"
        )
        parts.append(
            f"{row['key']} {row['name']} is {_crore(abs(row['cv']))} over at "
            f"CPI {row['cpi']:.2f} and is {state}"
        )

    if not parts:
        return "No work package is currently showing an unfavourable cost variance."

    total_adverse = started[started["cv"] < 0]["cv"].sum()
    share = abs(worst["cv"].sum() / total_adverse * 100) if total_adverse else 0.0
    return (
        "The variance is concentrated rather than general: "
        + "; ".join(parts)
        + f". Together these account for {share:.0f}% of the adverse cost variance, "
        "which is where any recovery effort should be directed."
    )


def monthly_commentary(project: Project, period: int, metrics: PeriodMetrics,
                       es: EarnedScheduleResult) -> Commentary:
    """Full narrative for one reporting period."""
    return Commentary(
        period_label=project.meta.label(period),
        status=status_flag(metrics),
        paragraphs=[
            _cost_paragraph(metrics),
            _schedule_paragraph(metrics, es),
            _diagnosis_paragraph(project, period),
            _forecast_paragraph(metrics),
        ],
    )


def executive_summary(project: Project, metrics: PeriodMetrics,
                      es: EarnedScheduleResult) -> str:
    """Three sentences for someone who will not read the rest.

    Written for a client representative or a lender, not a planner: no
    index is quoted without the plain-language consequence beside it.
    """
    central = {f.method: f for f in forecasts(metrics)}["EAC1"]
    days = abs(es.sv_t) * DAYS_PER_PERIOD
    late = "behind" if es.sv_t < 0 else "ahead of"
    over = "over" if central.vac < 0 else "under"
    return (
        f"The project is {metrics.pct_complete:.1f}% complete against a plan of "
        f"{metrics.pct_scheduled:.1f}%, having spent {metrics.pct_spent:.1f}% of the "
        f"budget. It is approximately {days:.0f} days {late} programme and, if "
        f"current cost performance continues, will finish about "
        f"{_crore(abs(central.vac))} {over} a budget of {_crore(metrics.bac)}. "
        f"Returning to budget would require a "
        f"{(tcpi_to_bac(metrics) / metrics.cpi - 1) * 100:.0f}% improvement in cost "
        f"efficiency on all remaining work."
    )
