"""Loading and validation of EVM project data.

Three inputs define a project:

  wbs.csv       the work breakdown structure and the budget of each leaf
                work package. Branch rows carry no budget of their own; a
                branch's budget is the sum of its leaves.

  baseline.csv  the time-phased budget. For every leaf and every baseline
                period, the planned value falling in that period. Summed
                over all periods a leaf's planned value must equal its
                budget, and summed over everything it must equal BAC.

  actuals.csv   for every leaf and every reported period, the cumulative
                physical percent complete and the actual cost booked in
                that period.

Earned value is derived, never supplied:

    EV(leaf, period) = pct_complete_cum(leaf, period) x budget(leaf)

This is the percent-complete method. It is the right default for building
work, where progress is measured by quantity executed against quantity in
the bill. Its weakness is that the percent is a judgement made on site, and
every EVM number inherits that judgement. The tool cannot check it; only a
measurement at site can.

Validation is deliberately strict. An EVM system fed inconsistent data
produces indices that look authoritative and are wrong, which is worse than
producing nothing, so every check below raises rather than warns.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# Planned value must reconcile to budget within this many rupees per work
# package. Allows for rounding in the time-phasing, nothing more.
RECONCILIATION_TOLERANCE_INR = 1.0


class DataValidationError(ValueError):
    """Raised when input data cannot support a defensible EVM calculation."""


@dataclass(frozen=True)
class ProjectMeta:
    project_name: str
    project_code: str
    currency: str
    baseline_periods: int
    period_unit: str
    data_date_period: int
    period_labels: list[str]
    bac_inr: float
    notes: str = ""

    def label(self, period: int) -> str:
        """Human label for a period number, falling back to 'P<n>'."""
        if 1 <= period <= len(self.period_labels):
            return self.period_labels[period - 1]
        return f"P{period}"


@dataclass
class Project:
    """A validated EVM project, ready for metric computation."""

    meta: ProjectMeta
    wbs: pd.DataFrame        # wbs_id, parent_id, name, is_leaf, budget_inr, ...
    baseline: pd.DataFrame   # wbs_id, period, pv_period_inr
    actuals: pd.DataFrame    # wbs_id, period, pct_complete_cum, ac_period_inr

    @property
    def bac(self) -> float:
        return float(self.meta.bac_inr)

    @property
    def data_date(self) -> int:
        return int(self.meta.data_date_period)

    @property
    def n_periods(self) -> int:
        return int(self.meta.baseline_periods)

    @property
    def leaves(self) -> pd.DataFrame:
        return self.wbs[self.wbs["is_leaf"]].copy()

    def budget(self, wbs_id: str) -> float:
        """Budget of a work package, or the rolled-up budget of a branch."""
        row = self.wbs[self.wbs["wbs_id"] == wbs_id]
        if row.empty:
            raise KeyError(f"unknown wbs_id: {wbs_id}")
        if bool(row.iloc[0]["is_leaf"]):
            return float(row.iloc[0]["budget_inr"])
        return float(
            self.leaves[self.leaves["wbs_id"].str.startswith(f"{wbs_id}.")][
                "budget_inr"
            ].sum()
        )


def load_project(data_dir: str | Path) -> Project:
    """Read a project from a directory and validate it."""
    data_dir = Path(data_dir)

    with open(data_dir / "project.json") as fh:
        raw = json.load(fh)
    meta = ProjectMeta(
        project_name=raw["project_name"],
        project_code=raw["project_code"],
        currency=raw["currency"],
        baseline_periods=int(raw["baseline_periods"]),
        period_unit=raw["period_unit"],
        data_date_period=int(raw["data_date_period"]),
        period_labels=list(raw.get("period_labels", [])),
        bac_inr=float(raw["bac_inr"]),
        notes=raw.get("notes", ""),
    )

    wbs = pd.read_csv(data_dir / "wbs.csv", dtype={"wbs_id": str, "parent_id": str})
    wbs["parent_id"] = wbs["parent_id"].fillna("")
    wbs["is_leaf"] = wbs["is_leaf"].astype(str).str.upper().eq("Y")
    wbs["budget_inr"] = pd.to_numeric(wbs["budget_inr"], errors="coerce").fillna(0.0)

    baseline = pd.read_csv(data_dir / "baseline.csv", dtype={"wbs_id": str})
    actuals = pd.read_csv(data_dir / "actuals.csv", dtype={"wbs_id": str})

    project = Project(meta=meta, wbs=wbs, baseline=baseline, actuals=actuals)
    validate(project)
    return project


def validate(project: Project) -> None:
    """Raise DataValidationError on anything that would corrupt the indices."""
    leaves = project.leaves
    leaf_ids = set(leaves["wbs_id"])

    if not leaf_ids:
        raise DataValidationError("the WBS contains no leaf work packages")

    # Every WBS id must be unique. Duplicate ids silently double-count budget.
    duplicates = project.wbs["wbs_id"][project.wbs["wbs_id"].duplicated()].tolist()
    if duplicates:
        raise DataValidationError(f"duplicate wbs_id values: {sorted(set(duplicates))}")

    # Baseline and actuals may only reference leaves. Planned value attached
    # to a branch would be counted once on the branch and again on its
    # children.
    for name, frame in (("baseline", project.baseline), ("actuals", project.actuals)):
        unknown = set(frame["wbs_id"]) - leaf_ids
        if unknown:
            raise DataValidationError(
                f"{name}.csv references non-leaf or unknown wbs_id: {sorted(unknown)}"
            )

    # Budgets must be positive. A zero-budget package earns nothing however
    # complete it is, which makes its percent complete meaningless.
    non_positive = leaves[leaves["budget_inr"] <= 0]["wbs_id"].tolist()
    if non_positive:
        raise DataValidationError(
            f"work packages with zero or negative budget: {sorted(non_positive)}"
        )

    # Planned value must reconcile to budget, per package and in total.
    planned = project.baseline.groupby("wbs_id")["pv_period_inr"].sum()
    for _, row in leaves.iterrows():
        wbs_id = row["wbs_id"]
        budgeted = float(row["budget_inr"])
        phased = float(planned.get(wbs_id, 0.0))
        if abs(phased - budgeted) > RECONCILIATION_TOLERANCE_INR:
            raise DataValidationError(
                f"work package {wbs_id}: time-phased planned value "
                f"{phased:,.2f} does not reconcile to its budget {budgeted:,.2f}"
            )

    total_budget = float(leaves["budget_inr"].sum())
    if abs(total_budget - project.bac) > RECONCILIATION_TOLERANCE_INR:
        raise DataValidationError(
            f"sum of work package budgets {total_budget:,.2f} does not equal "
            f"the declared BAC {project.bac:,.2f}"
        )

    # Percent complete must be a fraction in [0, 1] and must never go
    # backwards. Progress that reverses means either a measurement error or
    # rework, and rework is a change to the budget, not a negative percent.
    if project.actuals["pct_complete_cum"].lt(0).any():
        raise DataValidationError("negative pct_complete_cum found")
    if project.actuals["pct_complete_cum"].gt(1.0).any():
        raise DataValidationError(
            "pct_complete_cum greater than 1.0 found; it is a fraction, not a percent"
        )
    for wbs_id, group in project.actuals.groupby("wbs_id"):
        series = group.sort_values("period")["pct_complete_cum"].tolist()
        if any(b < a for a, b in zip(series, series[1:])):
            raise DataValidationError(
                f"work package {wbs_id}: cumulative percent complete decreases "
                "between periods"
            )

    if project.actuals["ac_period_inr"].lt(0).any():
        raise DataValidationError(
            "negative actual cost found; a credit note is a correction to a "
            "prior period, not a negative cost in this one"
        )

    # Periods must lie inside the baseline, and actuals must stop at the
    # data date. Reporting progress beyond the data date is the single most
    # common way a cost report ends up overstating earned value.
    if project.baseline["period"].lt(1).any() or project.baseline[
        "period"
    ].gt(project.n_periods).any():
        raise DataValidationError("baseline period outside 1..baseline_periods")
    if project.actuals["period"].gt(project.data_date).any():
        raise DataValidationError(
            "actuals.csv contains periods after the data date"
        )
