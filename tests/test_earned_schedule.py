"""Earned Schedule, checked against hand calculation and against theory.

Hand calculation at the data date, end of Period 6:

    Cumulative planned value, Period 5   Rs 3,16,63,555.56
    Cumulative planned value, Period 6   Rs 4,02,48,444.44
    Earned value                         Rs 3,47,30,000.00

EV lies between the Period 5 and Period 6 points on the baseline, so the
project has earned somewhere in Period 6 of baseline value:

    ES = 5 + (3,47,30,000.00 - 3,16,63,555.56)
             -----------------------------------
             (4,02,48,444.44 - 3,16,63,555.56)

       = 5 + 30,66,444.44 / 85,84,888.88
       = 5 + 0.35719
       = 5.35719 months

    SV(t) = ES - AT = 5.35719 - 6 = -0.64281 months, about 19 days behind
    SPI(t) = ES / AT = 5.35719 / 6 = 0.89287
"""

from __future__ import annotations

import math

import pytest

import evm

HAND_ES_P6 = 5.3571909
HAND_SPI_T_P6 = 0.8928651
HAND_SV_T_P6 = -0.6428091


class TestEarnedScheduleAtDataDate:
    def test_earned_schedule_matches_hand_calculation(self, project):
        result = evm.earned_schedule(project, 6)
        assert result.earned_schedule == pytest.approx(HAND_ES_P6, abs=1e-5)

    def test_time_based_indices(self, project):
        result = evm.earned_schedule(project, 6)
        assert result.spi_t == pytest.approx(HAND_SPI_T_P6, abs=1e-6)
        assert result.sv_t == pytest.approx(HAND_SV_T_P6, abs=1e-5)

    def test_schedule_variance_in_days_is_about_three_weeks(self, project):
        """The figure the site team can actually act on."""
        result = evm.earned_schedule(project, 6)
        days_behind = -result.sv_t * 30.0
        assert 18.0 < days_behind < 20.0

    def test_forecast_duration(self, project):
        """IEAC(t) = PD / SPI(t) = 12 / 0.89287 = 13.44 months."""
        result = evm.earned_schedule(project, 6)
        assert result.independent_eac_time == pytest.approx(13.4404, abs=1e-3)
        assert result.forecast_overrun == pytest.approx(1.4404, abs=1e-3)


class TestEarnedScheduleProperties:
    @pytest.mark.parametrize("period", range(1, 7))
    def test_earned_schedule_never_exceeds_planned_duration(self, project, period):
        result = evm.earned_schedule(project, period)
        assert 0.0 <= result.earned_schedule <= result.planned_duration

    @pytest.mark.parametrize("period", range(1, 7))
    def test_sign_agreement_with_classical_schedule_variance(self, project, period):
        """SV and SV(t) must agree on whether the project is behind.

        They are different magnitudes in different units, but if one says
        ahead and the other says behind, one of them is wrong.
        """
        m = evm.metrics_at(project, period)
        es = evm.earned_schedule(project, period)
        if abs(m.sv) < 1.0:
            return
        assert (m.sv < 0) == (es.sv_t < 0)

    def test_earned_schedule_is_monotonic(self, project):
        """Earned Schedule cannot go backwards while EV is monotonic."""
        values = [evm.earned_schedule(project, p).earned_schedule for p in range(1, 7)]
        assert all(b >= a - 1e-9 for a, b in zip(values, values[1:]))

    def test_spi_t_is_more_pessimistic_than_spi_is_optimistic(self, project):
        """The point of the whole module, demonstrated on the case data.

        Classical SPI reads 0.863 and Earned Schedule SPI(t) reads 0.893.
        They differ because they measure different things: SPI compares
        rupees of value, SPI(t) compares elapsed baseline time. Showing
        both, and explaining the gap, is more honest than picking one.
        """
        m = evm.metrics_at(project, 6)
        es = evm.earned_schedule(project, 6)
        assert m.spi < es.spi_t
        assert abs(es.spi_t - m.spi) > 0.02


class TestEdgeCases:
    def test_no_earned_value_gives_zero_earned_schedule(self, project):
        """Before any work is done ES is zero, not undefined."""
        empty = evm.Project(
            meta=project.meta,
            wbs=project.wbs,
            baseline=project.baseline,
            actuals=project.actuals.assign(pct_complete_cum=0.0),
        )
        result = evm.earned_schedule(empty, 6)
        assert result.earned_schedule == 0.0
        assert result.spi_t == 0.0

    def test_fully_earned_project_caps_at_planned_duration(self, project):
        """At completion ES equals PD and the result says it was capped.

        This is the boundary where interpolating off the end of the
        baseline would silently invent schedule performance.
        """
        complete = evm.Project(
            meta=project.meta,
            wbs=project.wbs,
            baseline=project.baseline,
            actuals=project.actuals.assign(pct_complete_cum=1.0),
        )
        result = evm.earned_schedule(complete, 6)
        assert result.capped is True
        assert result.earned_schedule == pytest.approx(project.n_periods)
        # Finished all the work in half the baseline duration: SPI(t) = 2.0.
        assert result.spi_t == pytest.approx(2.0)

    def test_series_covers_every_reported_period(self, project):
        series = evm.earned_schedule_series(project)
        assert len(series) == project.data_date
        assert all(math.isfinite(r.spi_t) for r in series)
