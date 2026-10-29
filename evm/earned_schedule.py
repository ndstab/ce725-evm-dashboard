"""Earned Schedule: schedule performance measured in time, not currency.

Classical schedule variance has a defect that matters on exactly the
projects where schedule control matters most. SV = EV - PV is measured in
rupees, and at completion EV necessarily equals BAC and PV necessarily
equals BAC, so SV returns to zero and SPI returns to 1.00 no matter how
late the project finished. The indices improve as the project ends, and the
improvement is an artefact. On a project running late, SPI typically peaks
in misleading optimism over the final third.

Earned Schedule (Lipke, 2003) fixes this by asking a different question.
Instead of "how much value is the completed work worth compared with what
was scheduled", it asks "at what point on the baseline was this much value
scheduled to have been earned". That point is a time, so:

    ES          the baseline time at which cumulative PV equals current EV
    AT          actual time, the data date
    SV(t) = ES - AT     schedule variance IN PERIODS
    SPI(t) = ES / AT    schedule efficiency, dimensionless

SV(t) is directly interpretable: minus 0.64 months is about nineteen days
behind, which a site manager can act on. SPI(t) converges on the true
schedule outcome instead of drifting back to 1.00.

The interpolation assumes planned value accrues linearly within a period.
Over a monthly reporting period on a construction project that is a mild
assumption; it would not be safe on very long periods or very lumpy spend.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .core import metrics_at, planned_value_curve
from .dataset import Project


@dataclass(frozen=True)
class EarnedScheduleResult:
    earned_schedule: float      # ES, in periods
    actual_time: float          # AT, in periods
    planned_duration: float     # PD, baseline duration in periods
    capped: bool                # True if EV exceeded the whole baseline PV

    @property
    def sv_t(self) -> float:
        """Schedule variance in periods. Negative is behind schedule."""
        return self.earned_schedule - self.actual_time

    @property
    def spi_t(self) -> float:
        """Time-based schedule performance index."""
        if self.actual_time == 0:
            return math.nan
        return self.earned_schedule / self.actual_time

    @property
    def independent_eac_time(self) -> float:
        """Forecast total duration, IEAC(t) = PD / SPI(t).

        The time analogue of EAC = BAC / CPI: it assumes schedule
        performance to date continues for the remaining work.
        """
        spi_t = self.spi_t
        if spi_t is None or math.isnan(spi_t) or spi_t == 0:
            return math.nan
        return self.planned_duration / spi_t

    @property
    def forecast_overrun(self) -> float:
        """Forecast completion delay, in periods."""
        return self.independent_eac_time - self.planned_duration


def earned_schedule(project: Project, period: int | None = None) -> EarnedScheduleResult:
    """Compute ES and the time-based schedule indices at a data date."""
    period = project.data_date if period is None else period

    ev = metrics_at(project, period).ev
    pv_curve = planned_value_curve(project)
    planned_duration = float(project.n_periods)

    # Nothing earned yet: ES is zero, not undefined.
    if ev <= 0:
        return EarnedScheduleResult(0.0, float(period), planned_duration, capped=False)

    # More earned than the entire baseline plans for. Can only happen with
    # inconsistent data, or genuinely at completion. Cap at PD and say so
    # rather than extrapolating off the end of the baseline.
    if ev >= float(pv_curve.iloc[-1]):
        return EarnedScheduleResult(
            planned_duration, float(period), planned_duration, capped=True
        )

    # Find the last whole period n where cumulative PV(n) <= EV, then
    # interpolate the fraction of period n+1 needed to reach EV.
    n = 0
    for p in range(1, project.n_periods + 1):
        if float(pv_curve.loc[p]) <= ev:
            n = p
        else:
            break

    pv_n = float(pv_curve.loc[n]) if n >= 1 else 0.0
    pv_next = float(pv_curve.loc[n + 1])

    increment = pv_next - pv_n
    fraction = 0.0 if increment == 0 else (ev - pv_n) / increment

    return EarnedScheduleResult(
        earned_schedule=n + fraction,
        actual_time=float(period),
        planned_duration=planned_duration,
        capped=False,
    )


def earned_schedule_series(project: Project) -> list[EarnedScheduleResult]:
    """Earned Schedule at every reported period, for trending."""
    return [earned_schedule(project, p) for p in range(1, project.data_date + 1)]
