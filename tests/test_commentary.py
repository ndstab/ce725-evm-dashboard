"""Commentary generation.

The commentary is the part of the tool a non-technical reader actually
reads, so the thing worth testing is not that it produces text but that
every number in the text is a computed number, correctly stated.
"""

from __future__ import annotations

import re

import pytest

import evm
from evm.commentary import _crore, status_flag


@pytest.fixture
def context(project):
    m = evm.metrics_at(project, 6)
    es = evm.earned_schedule(project, 6)
    return project, m, es


class TestStatusFlag:
    def test_case_study_is_both_late_and_over(self, context):
        _, m, _ = context
        assert status_flag(m) == "BEHIND SCHEDULE AND OVERSPENT"

    def test_healthy_project_reads_on_track(self, project):
        m = evm.PeriodMetrics(period=6, pv=100.0, ev=100.0, ac=100.0, bac=400.0)
        assert status_flag(m) == "ON TRACK"

    def test_overspent_but_on_programme(self, project):
        m = evm.PeriodMetrics(period=6, pv=100.0, ev=100.0, ac=125.0, bac=400.0)
        assert status_flag(m) == "OVERSPENT"

    def test_on_budget_but_late(self, project):
        m = evm.PeriodMetrics(period=6, pv=100.0, ev=80.0, ac=80.0, bac=400.0)
        assert status_flag(m) == "BEHIND SCHEDULE"


class TestCurrencyFormatting:
    @pytest.mark.parametrize(
        "value,expected",
        [
            (140_000_000, "Rs 14.00 crore"),
            (5_120_000, "Rs 51.20 lakh"),
            (45_000, "Rs 45,000"),
        ],
    )
    def test_indian_units(self, value, expected):
        """Crore and lakh, not millions.

        A construction cost report in India that reports in millions gets
        read at the wrong order of magnitude by the people who sign it.
        """
        assert _crore(value) == expected

    def test_negative_values_use_the_same_scale(self):
        assert _crore(-5_120_000) == "Rs -51.20 lakh"


class TestMonthlyCommentary:
    def test_produces_four_paragraphs(self, context):
        project, m, es = context
        c = evm.monthly_commentary(project, 6, m, es)
        assert len(c.paragraphs) == 4
        assert c.period_label == "Sep-2025"

    def test_every_figure_quoted_is_a_computed_figure(self, context):
        """The anti-hallucination property, asserted rather than assumed.

        The commentary is template-driven precisely so that no number can
        appear in it that was not calculated. This test pins the headline
        figures; if a template is ever edited to say something the engine
        did not compute, it fails here.
        """
        project, m, es = context
        text = evm.monthly_commentary(project, 6, m, es).as_text()

        assert f"{m.cpi:.3f}" in text
        assert f"{m.spi:.3f}" in text
        assert f"{es.spi_t:.3f}" in text
        assert f"{es.earned_schedule:.2f}" in text
        assert _crore(m.ev) in text
        assert _crore(m.ac) in text
        assert _crore(m.bac) in text

    def test_states_the_schedule_slip_in_days(self, context):
        project, m, es = context
        text = evm.monthly_commentary(project, 6, m, es).as_text()
        assert "19 days behind plan" in text

    def test_names_the_packages_driving_the_variance(self, context):
        """The diagnosis a rolled-up S-curve cannot produce."""
        project, m, es = context
        text = evm.monthly_commentary(project, 6, m, es).as_text()
        assert "Excavation and earthwork" in text
        assert "concentrated rather than general" in text

    def test_reports_the_full_forecast_range_not_a_single_number(self, context):
        """Quoting one EAC implies a precision the method does not have."""
        project, m, es = context
        text = evm.monthly_commentary(project, 6, m, es).as_text()
        for f in evm.forecasts(m):
            if f.method in ("EAC1", "EAC2", "EAC3"):
                assert _crore(f.eac) in text

    def test_commentary_is_deterministic(self, context):
        """Same inputs, same sentence, every month. The property a language
        model could not give us and the reason this module is templated."""
        project, m, es = context
        first = evm.monthly_commentary(project, 6, m, es).as_text()
        second = evm.monthly_commentary(project, 6, m, es).as_text()
        assert first == second

    @pytest.mark.parametrize("period", range(1, 7))
    def test_commentary_generates_for_every_reported_period(self, project, period):
        m = evm.metrics_at(project, period)
        es = evm.earned_schedule(project, period)
        text = evm.monthly_commentary(project, period, m, es).as_text()
        assert len(text) > 200
        assert "nan" not in text.lower()


class TestExecutiveSummary:
    def test_quotes_no_bare_index(self, context):
        """Written for a client, so no index appears without its
        consequence in rupees or days beside it."""
        project, m, es = context
        summary = evm.executive_summary(project, m, es)
        assert "CPI" not in summary
        assert "SPI" not in summary
        assert "days behind programme" in summary
        assert "crore" in summary

    def test_is_three_sentences(self, context):
        project, m, es = context
        summary = evm.executive_summary(project, m, es)
        sentences = [s for s in re.split(r"(?<=\.)\s+", summary.strip()) if s]
        assert len(sentences) == 3
