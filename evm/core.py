"""Core earned value measures, variances and performance indices.

All three base measures are cumulative to a data date and expressed in the
same currency, which is what makes them comparable at all:

    PV   planned value      budgeted cost of the work SCHEDULED to be done
    EV   earned value       budgeted cost of the work ACTUALLY done
    AC   actual cost        what was actually SPENT doing it

Everything else in EVM is a comparison of two of those three:

    CV  = EV - AC     cost variance      EV vs AC: did the work done cost
                                         what it was budgeted to cost?
    SV  = EV - PV     schedule variance  EV vs PV: was as much work done as
                                         was scheduled?
    CPI = EV / AC     cost efficiency, rupees earned per rupee spent
    SPI = EV / PV     schedule efficiency, work done per work scheduled

Sign convention: negative variance is unfavourable, index below 1.00 is
unfavourable. This is the convention in PMBOK and in every standard text,
and it is worth stating because the opposite convention does appear in some
contractor reporting formats.

The structural weakness of SV and SPI is that both are measured in currency,
not time. As the project approaches completion EV converges on PV whatever
the delay, so SPI returns to 1.00 and SV returns to zero even on a project
that finishes a year late. See earned_schedule.py for the standard fix.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import pandas as pd

from .dataset import Project


def _matrix(project: Project, frame: pd.DataFrame, value_col: str,
            n_periods: int, fill_forward: bool) -> pd.DataFrame:
    """Leaf x period matrix of a value column, with gaps filled sensibly.

    fill_forward is True for cumulative quantities such as percent complete,
    where a missing period means "unchanged since last report", and False
    for per-period quantities such as cost, where it means "nothing booked".
    """
    leaf_ids = project.leaves["wbs_id"].tolist()
    periods = list(range(1, n_periods + 1))

    grid = (
        frame.pivot_table(
            index="wbs_id", columns="period", values=value_col, aggfunc="sum"
        )
        .reindex(index=leaf_ids, columns=periods)
        .astype(float)
    )

    if fill_forward:
        # A period with no report means progress is unchanged, so carry the
        # last reported figure forward. Anything before the first report is
        # zero, not NaN.
        grid = grid.ffill(axis=1)
    return grid.fillna(0.0)


def pv_matrix(project: Project) -> pd.DataFrame:
    """Cumulative planned value by leaf and period, over the full baseline."""
    per_period = _matrix(
        project, project.baseline, "pv_period_inr", project.n_periods, fill_forward=False
    )
    return per_period.cumsum(axis=1)


def ev_matrix(project: Project) -> pd.DataFrame:
    """Cumulative earned value by leaf and period, up to the data date.

    EV = cumulative percent complete x budget at completion of the package.
    """
    pct = _matrix(
        project, project.actuals, "pct_complete_cum", project.data_date, fill_forward=True
    )
    budgets = project.leaves.set_index("wbs_id")["budget_inr"]
    return pct.mul(budgets, axis=0)


def ac_matrix(project: Project) -> pd.DataFrame:
    """Cumulative actual cost by leaf and period, up to the data date."""
    per_period = _matrix(
        project, project.actuals, "ac_period_inr", project.data_date, fill_forward=False
    )
    return per_period.cumsum(axis=1)


def _safe_div(numerator: float, denominator: float) -> float:
    """Index value, or NaN where the denominator is zero.

    Before any work is scheduled PV is zero and SPI is genuinely undefined.
    Returning NaN rather than 0 or 1 keeps that honest; a tool that reports
    SPI = 1.00 for a project that has not started is lying by default.
    """
    if denominator == 0:
        return math.nan
    return numerator / denominator


@dataclass(frozen=True)
class PeriodMetrics:
    """Cumulative EVM position at the end of one reporting period."""

    period: int
    pv: float
    ev: float
    ac: float
    bac: float

    @property
    def cv(self) -> float:
        """Cost variance. Negative means the work done cost more than budgeted."""
        return self.ev - self.ac

    @property
    def sv(self) -> float:
        """Schedule variance in currency. Negative means behind schedule."""
        return self.ev - self.pv

    @property
    def cv_pct(self) -> float:
        """Cost variance as a percentage of the work done."""
        return _safe_div(self.cv, self.ev) * 100

    @property
    def sv_pct(self) -> float:
        """Schedule variance as a percentage of the work scheduled."""
        return _safe_div(self.sv, self.pv) * 100

    @property
    def cpi(self) -> float:
        """Cost performance index. Rupees of budgeted work per rupee spent."""
        return _safe_div(self.ev, self.ac)

    @property
    def spi(self) -> float:
        """Schedule performance index. Work done per unit of work scheduled."""
        return _safe_div(self.ev, self.pv)

    @property
    def pct_complete(self) -> float:
        """Physical progress: EV as a percentage of BAC."""
        return _safe_div(self.ev, self.bac) * 100

    @property
    def pct_spent(self) -> float:
        """Budget consumed: AC as a percentage of BAC."""
        return _safe_div(self.ac, self.bac) * 100

    @property
    def pct_scheduled(self) -> float:
        """Planned progress: PV as a percentage of BAC."""
        return _safe_div(self.pv, self.bac) * 100

    def to_dict(self) -> dict:
        base = asdict(self)
        base.update(
            cv=self.cv, sv=self.sv, cv_pct=self.cv_pct, sv_pct=self.sv_pct,
            cpi=self.cpi, spi=self.spi, pct_complete=self.pct_complete,
            pct_spent=self.pct_spent, pct_scheduled=self.pct_scheduled,
        )
        return base


def metrics_at(project: Project, period: int) -> PeriodMetrics:
    """EVM position at the end of a given reporting period."""
    if not 1 <= period <= project.data_date:
        raise ValueError(
            f"period {period} is outside the reported range 1..{project.data_date}"
        )
    return PeriodMetrics(
        period=period,
        pv=float(pv_matrix(project)[period].sum()),
        ev=float(ev_matrix(project)[period].sum()),
        ac=float(ac_matrix(project)[period].sum()),
        bac=project.bac,
    )


def metrics_series(project: Project) -> pd.DataFrame:
    """One row per reported period, every cumulative measure and index."""
    pv, ev, ac = pv_matrix(project), ev_matrix(project), ac_matrix(project)
    rows = []
    for period in range(1, project.data_date + 1):
        m = PeriodMetrics(
            period=period,
            pv=float(pv[period].sum()),
            ev=float(ev[period].sum()),
            ac=float(ac[period].sum()),
            bac=project.bac,
        )
        row = m.to_dict()
        row["label"] = project.meta.label(period)
        rows.append(row)
    return pd.DataFrame(rows).set_index("period")


def planned_value_curve(project: Project) -> pd.Series:
    """Cumulative planned value over the whole baseline, the S-curve."""
    curve = pv_matrix(project).sum(axis=0)
    curve.index.name = "period"
    return curve


def variance_by_wbs(project: Project, period: int | None = None,
                    level: int = 2) -> pd.DataFrame:
    """Cost and schedule variance broken down by WBS element.

    This is the part a rolled-up project S-curve cannot give you. A project
    CPI of 0.87 tells a manager that something is wrong; it does not tell
    them where. Breaking EV, PV and AC down by work package turns a single
    unfavourable index into a short list of packages to go and look at.

    level=1 rolls up to the top WBS branches, level=2 to their children, and
    level=None reports every leaf.
    """
    period = project.data_date if period is None else period
    pv, ev, ac = pv_matrix(project)[period], ev_matrix(project)[period], ac_matrix(project)[period]

    leaves = project.leaves.set_index("wbs_id")
    rows = []
    for wbs_id in leaves.index:
        key = wbs_id if level is None else ".".join(wbs_id.split(".")[:level])
        rows.append({
            "key": key,
            "pv": float(pv.get(wbs_id, 0.0)),
            "ev": float(ev.get(wbs_id, 0.0)),
            "ac": float(ac.get(wbs_id, 0.0)),
            "budget": float(leaves.loc[wbs_id, "budget_inr"]),
        })

    grouped = pd.DataFrame(rows).groupby("key", as_index=False).sum(numeric_only=True)

    names = project.wbs.set_index("wbs_id")["name"]
    grouped["name"] = grouped["key"].map(names).fillna(grouped["key"])
    grouped["cv"] = grouped["ev"] - grouped["ac"]
    grouped["sv"] = grouped["ev"] - grouped["pv"]
    grouped["cpi"] = [
        _safe_div(e, a) for e, a in zip(grouped["ev"], grouped["ac"])
    ]
    grouped["spi"] = [
        _safe_div(e, p) for e, p in zip(grouped["ev"], grouped["pv"])
    ]
    grouped["pct_complete"] = [
        _safe_div(e, b) * 100 for e, b in zip(grouped["ev"], grouped["budget"])
    ]
    return grouped.sort_values("key").reset_index(drop=True)
