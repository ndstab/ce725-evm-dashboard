"""Core EVM measures, checked against hand calculations.

The expected values in this file were derived by hand, from the case study
inputs, before the engine was run. The derivations are written out in the
docstrings so that a marker, or any team member in the viva, can follow the
arithmetic without re-running anything.

The full version of this hand calculation, for reporting periods 5 and 6,
is in the manual benchmark workbook and in docs/04-validation-report.md.
"""

from __future__ import annotations

import math

import pytest

import evm
from conftest import RUPEE_TOL

# --------------------------------------------------------------------------
# Hand-calculated figures at the data date, end of Period 6. All in rupees.
# --------------------------------------------------------------------------

# Earned value, package by package: cumulative percent complete x budget.
#
#   1.1  1.00 x   25,00,000  =   25,00,000
#   1.2  1.00 x   18,00,000  =   18,00,000
#   2.1  1.00 x   42,00,000  =   42,00,000
#   2.2  1.00 x   68,00,000  =   68,00,000
#   2.3  1.00 x   95,00,000  =   95,00,000
#   2.4  1.00 x   38,00,000  =   38,00,000
#   3.1  0.22 x 1,45,00,000  =   31,90,000
#   3.2  0.14 x 2,10,00,000  =   29,40,000
#   3.3  0.00 x   55,00,000  =            0
#   everything downstream of the frame has not started
#                              -------------
#                               3,47,30,000
HAND_EV_P6 = 34_730_000.0

# Actual cost, package by package, summing the per-period bookings (Rs lakh):
#
#   1.1  15.0 + 12.0                        =  27.0
#   1.2   9.5 +  9.0                        =  18.5
#   2.1  11.0 + 15.0 + 16.5 + 11.0 + 7.5    =  61.0   (budget 42.0, rock)
#   2.2  11.0 + 19.5 + 25.0 + 18.5          =  74.0   (budget 68.0)
#   2.3  19.0 + 30.0 + 34.0 + 25.0          = 108.0   (budget 95.0)
#   2.4   8.5 + 16.0 + 16.5                 =  41.0   (budget 38.0)
#   3.1  13.0 + 23.0                        =  36.0
#   3.2  12.0 + 21.0                        =  33.0
#                                             ------
#                                             398.5 lakh
HAND_AC_P6 = 39_850_000.0

# Planned value. Packages whose baseline finish is Period 5 or earlier are
# fully planned by the data date:
#   1.1 25 + 1.2 18 + 2.1 42 + 2.2 68 + 2.3 95 + 2.4 38 = 286.00 lakh
# Packages still in progress against the baseline, using the smoothstep
# phasing 3t^2 - 2t^3 for S-shaped packages:
#   3.1  spans P5..P9,  n = 5, two periods elapsed, t = 2/5 = 0.4
#        3(0.16) - 2(0.064) = 0.352          145.00 x 0.352    =  51.040
#   3.2  spans P5..P10, n = 6, two periods elapsed, t = 1/3
#        3(1/9) - 2(1/27) = 7/27             210.00 x 7/27     =  54.444
#   3.3  spans P6..P10, n = 5, linear, one period elapsed, t = 0.2
#                                             55.00 x 0.20     =  11.000
#                                                                --------
#                                                                 402.484 lakh
HAND_PV_P6 = 40_248_444.44

HAND_BAC = 140_000_000.0


class TestBaseMeasures:
    def test_bac_is_the_sum_of_work_package_budgets(self, project):
        assert project.bac == pytest.approx(HAND_BAC, abs=RUPEE_TOL)
        assert project.leaves["budget_inr"].sum() == pytest.approx(
            HAND_BAC, abs=RUPEE_TOL
        )

    def test_earned_value_at_data_date(self, project):
        m = evm.metrics_at(project, 6)
        assert m.ev == pytest.approx(HAND_EV_P6, abs=RUPEE_TOL)

    def test_actual_cost_at_data_date(self, project):
        m = evm.metrics_at(project, 6)
        assert m.ac == pytest.approx(HAND_AC_P6, abs=RUPEE_TOL)

    def test_planned_value_at_data_date(self, project):
        m = evm.metrics_at(project, 6)
        assert m.pv == pytest.approx(HAND_PV_P6, abs=RUPEE_TOL)

    def test_planned_value_reaches_exactly_bac_at_the_end_of_the_baseline(self, project):
        """The S-curve must land on BAC, not near it.

        If the time-phased budget does not sum to BAC, every schedule index
        in the project is quietly scaled by the error.
        """
        curve = evm.planned_value_curve(project)
        assert curve.iloc[-1] == pytest.approx(project.bac, abs=RUPEE_TOL)

    def test_planned_value_curve_never_decreases(self, project):
        curve = evm.planned_value_curve(project).tolist()
        assert all(b >= a - RUPEE_TOL for a, b in zip(curve, curve[1:]))


class TestVariancesAndIndices:
    def test_cost_variance(self, project):
        m = evm.metrics_at(project, 6)
        # CV = EV - AC = 3,47,30,000 - 3,98,50,000 = -51,20,000
        assert m.cv == pytest.approx(-5_120_000.0, abs=RUPEE_TOL)

    def test_schedule_variance(self, project):
        m = evm.metrics_at(project, 6)
        # SV = EV - PV = 3,47,30,000 - 4,02,48,444 = -55,18,444
        assert m.sv == pytest.approx(-5_518_444.44, abs=RUPEE_TOL)

    def test_cost_performance_index(self, project):
        m = evm.metrics_at(project, 6)
        # CPI = 3,47,30,000 / 3,98,50,000 = 0.871518...
        assert m.cpi == pytest.approx(0.8715182, abs=1e-6)

    def test_schedule_performance_index(self, project):
        m = evm.metrics_at(project, 6)
        # SPI = 3,47,30,000 / 4,02,48,444 = 0.862890...
        assert m.spi == pytest.approx(0.8628896, abs=1e-6)

    def test_percent_complete_and_percent_spent(self, project):
        m = evm.metrics_at(project, 6)
        # 3,47,30,000 / 14,00,00,000 = 24.81%
        assert m.pct_complete == pytest.approx(24.8071, abs=1e-3)
        # 3,98,50,000 / 14,00,00,000 = 28.46%
        assert m.pct_spent == pytest.approx(28.4643, abs=1e-3)

    @pytest.mark.parametrize("period", range(1, 7))
    def test_index_identities_hold_in_every_period(self, project, period):
        """CPI x AC = EV and SPI x PV = EV, by definition.

        A tautology, deliberately. It catches the realistic failure mode
        where an index is computed from one period's EV and another
        period's AC after a column misalignment.
        """
        m = evm.metrics_at(project, period)
        if m.ac:
            assert m.cpi * m.ac == pytest.approx(m.ev, abs=RUPEE_TOL)
        if m.pv:
            assert m.spi * m.pv == pytest.approx(m.ev, abs=RUPEE_TOL)

    @pytest.mark.parametrize("period", range(1, 7))
    def test_variance_and_index_agree_on_direction(self, project, period):
        """Negative variance and index below one must always coincide."""
        m = evm.metrics_at(project, period)
        if math.isfinite(m.cpi):
            assert (m.cv < 0) == (m.cpi < 1.0)
        if math.isfinite(m.spi):
            assert (m.sv < 0) == (m.spi < 1.0)


class TestCumulativeConsistency:
    @pytest.mark.parametrize("period", range(1, 7))
    def test_cumulative_measures_never_decrease(self, project, period):
        """EV, AC and PV are cumulative, so they are monotonic."""
        if period == 1:
            return
        now = evm.metrics_at(project, period)
        before = evm.metrics_at(project, period - 1)
        assert now.ev >= before.ev - RUPEE_TOL
        assert now.ac >= before.ac - RUPEE_TOL
        assert now.pv >= before.pv - RUPEE_TOL

    def test_earned_value_never_exceeds_budget_for_any_package(self, project):
        """A package cannot earn more than it is worth.

        EV above budget means percent complete above 100, which is the
        classic symptom of progress claimed against a package whose scope
        has grown without the budget being revised.
        """
        ev = evm.ev_matrix(project)[project.data_date]
        budgets = project.leaves.set_index("wbs_id")["budget_inr"]
        for wbs_id, earned in ev.items():
            assert earned <= budgets[wbs_id] + RUPEE_TOL, wbs_id

    def test_metrics_series_matches_metrics_at(self, project):
        """The trend table and the single-period figures must not disagree."""
        series = evm.metrics_series(project)
        for period in range(1, project.data_date + 1):
            m = evm.metrics_at(project, period)
            assert series.loc[period, "ev"] == pytest.approx(m.ev, abs=RUPEE_TOL)
            assert series.loc[period, "pv"] == pytest.approx(m.pv, abs=RUPEE_TOL)
            assert series.loc[period, "ac"] == pytest.approx(m.ac, abs=RUPEE_TOL)


class TestWbsBreakdown:
    def test_breakdown_reconciles_to_the_project_totals(self, project):
        """Rolling the WBS up must reproduce the project position exactly.

        This is the check that makes the breakdown trustworthy: if the
        parts do not sum to the whole, the diagnosis is pointing at the
        wrong package.
        """
        m = evm.metrics_at(project, 6)
        breakdown = evm.variance_by_wbs(project, period=6, level=1)
        assert breakdown["ev"].sum() == pytest.approx(m.ev, abs=RUPEE_TOL)
        assert breakdown["pv"].sum() == pytest.approx(m.pv, abs=RUPEE_TOL)
        assert breakdown["ac"].sum() == pytest.approx(m.ac, abs=RUPEE_TOL)
        assert breakdown["budget"].sum() == pytest.approx(project.bac, abs=RUPEE_TOL)

    def test_breakdown_is_consistent_across_levels(self, project):
        level1 = evm.variance_by_wbs(project, period=6, level=1)
        level2 = evm.variance_by_wbs(project, period=6, level=2)
        leaves = evm.variance_by_wbs(project, period=6, level=None)
        for frame in (level2, leaves):
            assert frame["ev"].sum() == pytest.approx(level1["ev"].sum(), abs=RUPEE_TOL)
            assert frame["ac"].sum() == pytest.approx(level1["ac"].sum(), abs=RUPEE_TOL)

    def test_substructure_carries_the_cost_overrun(self, project):
        """The diagnosis the dashboard exists to deliver.

        Substructure (WBS 2) is complete, so its cost variance is final and
        cannot recover. Confirming it here means the breakdown is actually
        locating the overrun rather than smearing it across the project.
        """
        breakdown = evm.variance_by_wbs(project, period=6, level=1).set_index("key")
        substructure = breakdown.loc["2"]
        # Budget 2,43,00,000 against actual 2,84,00,000.
        assert substructure["cv"] == pytest.approx(-4_100_000.0, abs=RUPEE_TOL)
        assert substructure["pct_complete"] == pytest.approx(100.0, abs=1e-6)
        # It is the single largest contributor to the project cost variance.
        assert substructure["cv"] == breakdown["cv"].min()
