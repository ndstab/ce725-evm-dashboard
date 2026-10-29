"""Input validation.

Every test here feeds the loader data that is wrong in a way we have
actually seen in real cost reports, and asserts that it is rejected rather
than quietly turned into an index.

The reason this matters more in EVM than in most calculations: the output
is three ratios near 1.00. There is no sanity check a reader can apply. A
CPI of 0.94 computed from corrupt data looks exactly like a CPI of 0.94
computed from good data, and it will be taken to a client meeting.
"""

from __future__ import annotations

import dataclasses

import pandas as pd
import pytest

import evm
from evm.dataset import DataValidationError, validate


def _mutate(project, *, wbs=None, baseline=None, actuals=None, meta=None):
    """A copy of the project with one frame replaced."""
    return evm.Project(
        meta=project.meta if meta is None else meta,
        wbs=project.wbs if wbs is None else wbs,
        baseline=project.baseline if baseline is None else baseline,
        actuals=project.actuals if actuals is None else actuals,
    )


class TestBudgetReconciliation:
    def test_time_phased_budget_must_sum_to_the_package_budget(self, project):
        """Planned value that does not add up to the budget scales every
        schedule index in the project by the error."""
        broken = project.baseline.copy()
        mask = broken["wbs_id"].eq("2.1") & broken["period"].eq(1)
        broken.loc[mask, "pv_period_inr"] += 50_000
        with pytest.raises(DataValidationError, match="does not reconcile"):
            validate(_mutate(project, baseline=broken))

    def test_package_budgets_must_sum_to_the_declared_bac(self, project):
        """The declared BAC is an independent assertion and must agree.

        Mutating a work package budget would be caught one check earlier by
        per-package reconciliation, so to exercise this rule on its own the
        declared total is what moves. In practice this fires when a
        variation has been added to the contract value but not pushed down
        into the work packages.
        """
        broken_meta = dataclasses.replace(
            project.meta, bac_inr=project.meta.bac_inr + 100_000
        )
        with pytest.raises(DataValidationError, match="does not equal"):
            validate(_mutate(project, meta=broken_meta))

    def test_a_zero_budget_work_package_is_rejected(self, project):
        """It can never earn value however complete it is, so its percent
        complete is meaningless and it silently dilutes the project SPI."""
        broken_wbs = project.wbs.copy()
        broken_wbs.loc[broken_wbs["wbs_id"].eq("6.2"), "budget_inr"] = 0
        with pytest.raises(DataValidationError, match="zero or negative budget"):
            validate(_mutate(project, wbs=broken_wbs))


class TestProgressReporting:
    def test_percent_complete_above_one_is_rejected(self, project):
        """Usually someone has entered 85 meaning 85%, in a column that
        holds fractions. It inflates EV by a factor of a hundred."""
        broken = project.actuals.copy()
        broken.loc[broken["wbs_id"].eq("3.1"), "pct_complete_cum"] = 85.0
        with pytest.raises(DataValidationError, match="fraction, not a percent"):
            validate(_mutate(project, actuals=broken))

    def test_progress_may_not_go_backwards(self, project):
        """Reversing progress means a measurement error or rework. Rework
        is a change to the budget, not a negative percent complete."""
        broken = project.actuals.copy()
        mask = broken["wbs_id"].eq("2.3") & broken["period"].eq(5)
        broken.loc[mask, "pct_complete_cum"] = 0.10
        with pytest.raises(DataValidationError, match="decreases"):
            validate(_mutate(project, actuals=broken))

    def test_negative_actual_cost_is_rejected(self, project):
        broken = project.actuals.copy()
        mask = broken["wbs_id"].eq("2.2") & broken["period"].eq(3)
        broken.loc[mask, "ac_period_inr"] = -500_000
        with pytest.raises(DataValidationError, match="negative actual cost"):
            validate(_mutate(project, actuals=broken))


class TestStructuralIntegrity:
    def test_actuals_may_not_run_past_the_data_date(self, project):
        """The most common way a cost report overstates earned value:
        progress claimed for a period that has not been costed yet."""
        extra = project.actuals.iloc[[0]].copy()
        extra["period"] = project.data_date + 1
        # Carry progress forward rather than reversing it, so this test
        # exercises the data-date rule and not the monotonicity rule.
        extra["pct_complete_cum"] = 1.0
        broken = pd.concat([project.actuals, extra], ignore_index=True)
        with pytest.raises(DataValidationError, match="after the data date"):
            validate(_mutate(project, actuals=broken))

    def test_progress_against_a_branch_rather_than_a_leaf_is_rejected(self, project):
        """Value booked on a branch is counted once there and again on its
        children, double-counting the earned value."""
        broken = project.actuals.copy()
        broken.loc[broken.index[0], "wbs_id"] = "2"
        with pytest.raises(DataValidationError, match="non-leaf or unknown"):
            validate(_mutate(project, actuals=broken))

    def test_duplicate_wbs_ids_are_rejected(self, project):
        broken_wbs = pd.concat(
            [project.wbs, project.wbs.iloc[[5]]], ignore_index=True
        )
        with pytest.raises(DataValidationError, match="duplicate wbs_id"):
            validate(_mutate(project, wbs=broken_wbs))


class TestTheSuppliedCaseStudyIsValid:
    def test_the_case_study_passes_every_check(self, project):
        validate(project)

    def test_it_has_the_structure_the_documentation_claims(self, project):
        assert len(project.leaves) == 19
        assert project.bac == 140_000_000.0
        assert project.n_periods == 12
        assert project.data_date == 6
