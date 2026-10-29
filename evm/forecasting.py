"""Cost forecasting: EAC, ETC, VAC and TCPI.

Forecasting is where EVM earns its keep. CPI and SPI describe the past; EAC
is a statement about the future, and it is the number a client, a lender or
a board actually asks for.

There is no single EAC formula. There are four standard ones, and they
differ in one assumption only: what do we believe about the cost
performance of the work that remains?

    EAC1 = BAC / CPI
        Performance to date is TYPICAL and will continue. The default, and
        the most commonly cited. Research on large projects has repeatedly
        found that CPI stabilises early -- often by the 20% complete point
        -- and rarely recovers, which is why this formula is hard to beat
        in practice and why an optimistic management forecast should be
        treated with suspicion once CPI has settled.

    EAC2 = AC + (BAC - EV)
        The overrun to date was a ONE-OFF and the remaining work will be
        done at budget. Defensible when the variance has an identified,
        closed cause -- a rock excavation claim that is now finished, a
        single mispriced item. Not defensible as a general assumption.

    EAC3 = AC + (BAC - EV) / (CPI x SPI)
        Both cost and schedule pressure continue. The most pessimistic of
        the four, and often the most realistic on a project that is both
        over and late, because recovering schedule normally costs money:
        acceleration, overtime, extra plant, more crews on the same front.

    EAC4 = AC + (BAC - EV) / (w x CPI + (1-w) x SPI)
        A weighted blend, conventionally w = 0.8. Used when cost
        performance is judged the dominant driver but schedule pressure
        cannot be ignored.

The honest way to present these is together, as a range. A single EAC
implies a precision the method does not have.

TCPI closes the loop. It is the cost efficiency the remaining work must
achieve to land on a target, and it is the sharpest reality check in EVM:
if a project has been running at CPI 0.87 for six months and TCPI says the
rest must be done at 1.05, the budget is gone, whatever the recovery plan
says.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .core import PeriodMetrics

DEFAULT_CPI_WEIGHT = 0.8


@dataclass(frozen=True)
class Forecast:
    """A single EAC method and everything derived from it."""

    method: str
    label: str
    assumption: str
    eac: float
    bac: float
    ac: float
    ev: float

    @property
    def etc(self) -> float:
        """Estimate to complete: what the remaining work will cost."""
        return self.eac - self.ac

    @property
    def vac(self) -> float:
        """Variance at completion. Negative means forecast overrun."""
        return self.bac - self.eac

    @property
    def vac_pct(self) -> float:
        if self.bac == 0:
            return math.nan
        return self.vac / self.bac * 100

    @property
    def tcpi(self) -> float:
        """Cost efficiency the remaining work must achieve to hit this EAC."""
        denominator = self.eac - self.ac
        if denominator == 0:
            return math.nan
        return (self.bac - self.ev) / denominator


def _finite(value: float) -> float:
    return value if math.isfinite(value) else math.nan


def forecasts(metrics: PeriodMetrics, cpi_weight: float = DEFAULT_CPI_WEIGHT,
              spi: float | None = None) -> list[Forecast]:
    """All four standard EAC methods at a given data date.

    spi defaults to the classical EV/PV index on the metrics object. Passing
    SPI(t) from earned_schedule instead gives the Earned Schedule variant of
    EAC3, which is the better choice late in a project where classical SPI
    has started drifting back towards 1.00.
    """
    bac, ev, ac = metrics.bac, metrics.ev, metrics.ac
    cpi = metrics.cpi
    spi = metrics.spi if spi is None else spi
    remaining = bac - ev

    results: list[Forecast] = []

    results.append(Forecast(
        method="EAC1",
        label="BAC / CPI",
        assumption="Cost performance to date is typical and continues",
        eac=_finite(bac / cpi) if cpi not in (0,) and math.isfinite(cpi) else math.nan,
        bac=bac, ac=ac, ev=ev,
    ))

    results.append(Forecast(
        method="EAC2",
        label="AC + (BAC - EV)",
        assumption="The variance was a one-off; remaining work runs at budget",
        eac=ac + remaining,
        bac=bac, ac=ac, ev=ev,
    ))

    composite = cpi * spi if math.isfinite(cpi) and math.isfinite(spi) else math.nan
    results.append(Forecast(
        method="EAC3",
        label="AC + (BAC - EV) / (CPI x SPI)",
        assumption="Both cost and schedule pressure continue to completion",
        eac=_finite(ac + remaining / composite) if composite not in (0,) and math.isfinite(composite) else math.nan,
        bac=bac, ac=ac, ev=ev,
    ))

    weighted = (
        cpi_weight * cpi + (1 - cpi_weight) * spi
        if math.isfinite(cpi) and math.isfinite(spi) else math.nan
    )
    results.append(Forecast(
        method="EAC4",
        label=f"AC + (BAC - EV) / ({cpi_weight:g} x CPI + {1 - cpi_weight:g} x SPI)",
        assumption="Cost performance dominates, schedule pressure partly weighted",
        eac=_finite(ac + remaining / weighted) if weighted not in (0,) and math.isfinite(weighted) else math.nan,
        bac=bac, ac=ac, ev=ev,
    ))

    return results


def tcpi_to_bac(metrics: PeriodMetrics) -> float:
    """Efficiency the remaining work must achieve to finish ON BUDGET.

    Returns NaN once AC has reached BAC, where the question is meaningless:
    there is no budget left to do the remaining work with at any efficiency.
    """
    denominator = metrics.bac - metrics.ac
    if denominator <= 0:
        return math.nan
    return (metrics.bac - metrics.ev) / denominator


def feasibility_note(tcpi: float, cpi: float) -> str:
    """Plain-language verdict on whether a TCPI target is reachable.

    The thresholds are a reporting convention, not a theorem. The 10% band
    reflects the common rule of thumb that a sustained efficiency
    improvement of more than about ten percent mid-project is rare without
    a change in scope, method or crew.
    """
    if not (math.isfinite(tcpi) and math.isfinite(cpi)):
        return "Not assessable."
    if tcpi <= cpi:
        return "Achievable at current performance."
    gap = (tcpi - cpi) / cpi * 100
    if gap <= 5:
        return f"Requires a {gap:.1f}% improvement on current performance. Tight but plausible."
    if gap <= 10:
        return f"Requires a {gap:.1f}% improvement on current performance. Demanding; needs a specific plan."
    return (
        f"Requires a {gap:.1f}% improvement on current performance. "
        "Historically unlikely without a change in scope, method or baseline."
    )
