"""Forecasting: EAC, ETC, VAC and TCPI.

Hand calculation at the data date, end of Period 6, with
BAC = Rs 14,00,00,000, EV = Rs 3,47,30,000, AC = Rs 3,98,50,000,
CPI = 0.871518, SPI = 0.862890, and remaining work BAC - EV =
Rs 10,52,70,000:

    EAC1 = BAC / CPI
         = 14,00,00,000 / 0.871518            = Rs 16,06,39,217

    EAC2 = AC + (BAC - EV)
         = 3,98,50,000 + 10,52,70,000         = Rs 14,51,20,000

    EAC3 = AC + (BAC - EV) / (CPI x SPI)
         = 3,98,50,000 + 10,52,70,000 / 0.7520247620
                                              = Rs 17,98,32,092.77

    TCPI(BAC) = (BAC - EV) / (BAC - AC)
              = 10,52,70,000 / 10,01,50,000   = 1.051123

The spread between EAC2 and EAC3 is Rs 3.47 crore on a Rs 14 crore
project. That spread is the honest answer: the method cannot narrow it
without a judgement about whether the rock overrun was a one-off.

A note on the EAC3 figure, because it cost us a round of checking. The
first hand calculation of EAC3 used CPI x SPI rounded to six decimal
places and came out Rs 156 above the engine. The engine was right: carried
at full precision the product is 0.7520247620, and rounding it to
0.752025 moves EAC3 by about Rs 44. The rule this enforced on the rest of
the work is that rounding belongs in presentation only, never in the
calculation chain. See test_rounding_an_intermediate_index_moves_the_forecast
below, which pins the lesson so it cannot quietly come back.
"""

from __future__ import annotations

import math

import pytest

import evm
from conftest import RUPEE_TOL

HAND_EAC1 = 160_639_216.8
HAND_EAC2 = 145_120_000.0
HAND_EAC3 = 179_832_092.77
HAND_TCPI_BAC = 1.0511233


@pytest.fixture
def metrics(project):
    return evm.metrics_at(project, 6)


@pytest.fixture
def by_method(metrics):
    return {f.method: f for f in evm.forecasts(metrics)}


class TestEacMethods:
    def test_eac1_matches_hand_calculation(self, by_method):
        assert by_method["EAC1"].eac == pytest.approx(HAND_EAC1, abs=50.0)

    def test_eac2_matches_hand_calculation(self, by_method):
        assert by_method["EAC2"].eac == pytest.approx(HAND_EAC2, abs=RUPEE_TOL)

    def test_eac3_matches_hand_calculation(self, by_method):
        assert by_method["EAC3"].eac == pytest.approx(HAND_EAC3, abs=1.0)

    def test_rounding_an_intermediate_index_moves_the_forecast(self, metrics):
        """Why the engine must not round mid-chain.

        Rounding the composite index CPI x SPI to six decimal places, which
        looks harmless and is how it would be written on paper, shifts EAC3
        by tens of rupees. Immaterial against a Rs 18 crore forecast, but
        the same habit applied to CPI itself early in a project, when EV is
        small, moves the number by lakhs. Rounding is for presentation.
        """
        composite = metrics.cpi * metrics.spi
        remaining = metrics.bac - metrics.ev
        exact = metrics.ac + remaining / composite
        rounded = metrics.ac + remaining / round(composite, 6)
        assert exact != rounded
        assert abs(exact - rounded) > 10.0

    def test_all_four_methods_are_produced(self, by_method):
        assert set(by_method) == {"EAC1", "EAC2", "EAC3", "EAC4"}

    def test_eac3_is_the_most_pessimistic_when_both_indices_are_below_one(
        self, by_method, metrics
    ):
        """With CPI and SPI both under 1.00, dividing by their product must
        produce the largest forecast of the four."""
        assert metrics.cpi < 1.0 and metrics.spi < 1.0
        assert by_method["EAC3"].eac == max(f.eac for f in by_method.values())

    def test_eac2_is_the_most_optimistic(self, by_method):
        """Assuming the remaining work runs at budget is the kindest
        assumption available, so it must give the lowest EAC."""
        assert by_method["EAC2"].eac == min(f.eac for f in by_method.values())


class TestDerivedQuantities:
    @pytest.mark.parametrize("method", ["EAC1", "EAC2", "EAC3", "EAC4"])
    def test_etc_is_eac_less_actual_cost(self, by_method, metrics, method):
        f = by_method[method]
        assert f.etc == pytest.approx(f.eac - metrics.ac, abs=RUPEE_TOL)

    @pytest.mark.parametrize("method", ["EAC1", "EAC2", "EAC3", "EAC4"])
    def test_vac_is_budget_less_eac(self, by_method, metrics, method):
        f = by_method[method]
        assert f.vac == pytest.approx(metrics.bac - f.eac, abs=RUPEE_TOL)

    @pytest.mark.parametrize("method", ["EAC1", "EAC2", "EAC3", "EAC4"])
    def test_every_method_forecasts_an_overrun(self, by_method, method):
        """On this project no defensible assumption lands inside budget."""
        assert by_method[method].vac < 0

    def test_vac_of_eac2_equals_the_cost_variance_to_date(self, by_method, metrics):
        """An algebraic identity worth asserting.

        VAC2 = BAC - (AC + BAC - EV) = EV - AC = CV. If the remaining work
        runs exactly at budget, the final overrun is precisely the overrun
        already incurred. It is a useful reading of EAC2 and a clean check
        that the arithmetic chain is intact.
        """
        assert by_method["EAC2"].vac == pytest.approx(metrics.cv, abs=RUPEE_TOL)


class TestTcpi:
    def test_tcpi_to_budget_matches_hand_calculation(self, metrics):
        assert evm.tcpi_to_bac(metrics) == pytest.approx(HAND_TCPI_BAC, abs=1e-6)

    def test_tcpi_against_eac1_equals_cpi(self, by_method, metrics):
        """Another identity. Substituting EAC = BAC/CPI into
        TCPI = (BAC - EV)/(EAC - AC) reduces to CPI exactly.

        Its meaning: a forecast built on "performance continues" is, by
        construction, a forecast that demands no change in performance.
        """
        assert by_method["EAC1"].tcpi == pytest.approx(metrics.cpi, abs=1e-9)

    def test_tcpi_against_eac2_is_exactly_one(self, by_method):
        """EAC2 assumes the rest runs at budget, so it requires CPI = 1.00."""
        assert by_method["EAC2"].tcpi == pytest.approx(1.0, abs=1e-9)

    def test_the_budget_is_not_recoverable(self, metrics):
        """The headline finding of the case study.

        Six months in, the project has run at CPI 0.87 throughout. Landing
        on budget now requires 1.05 on everything remaining, a 21%
        improvement that nothing in the record supports.
        """
        tcpi = evm.tcpi_to_bac(metrics)
        assert tcpi > metrics.cpi
        note = evm.feasibility_note(tcpi, metrics.cpi)
        assert "unlikely" in note.lower()

    def test_tcpi_is_undefined_once_the_budget_is_exhausted(self, metrics):
        """With AC at BAC there is no budget left to finish with, at any
        efficiency, so the honest answer is NaN rather than a number."""
        exhausted = evm.PeriodMetrics(
            period=metrics.period, pv=metrics.pv, ev=metrics.ev,
            ac=metrics.bac, bac=metrics.bac,
        )
        assert math.isnan(evm.tcpi_to_bac(exhausted))


class TestEarnedScheduleVariant:
    def test_passing_spi_t_changes_eac3(self, project, metrics):
        """EAC3 can be driven by SPI(t) instead of classical SPI.

        Because SPI(t) is the less pessimistic index here, the Earned
        Schedule variant gives a smaller EAC3. Late in a project the
        relationship reverses, which is exactly when classical SPI stops
        being trustworthy.
        """
        spi_t = evm.earned_schedule(project, 6).spi_t
        classical = {f.method: f for f in evm.forecasts(metrics)}["EAC3"]
        variant = {f.method: f for f in evm.forecasts(metrics, spi=spi_t)}["EAC3"]
        assert variant.eac < classical.eac
        assert variant.eac > metrics.bac
