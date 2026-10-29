"""Parity between the Python engine and the manual Excel benchmark.

These tests read docs/generated/benchmark-values.json, a snapshot of the
benchmark workbook's values AS COMPUTED BY LIBREOFFICE. The snapshot is
produced by scripts/validate_benchmark.py, which drives a real spreadsheet
engine over the typed formulas; nothing in this file re-implements them.

Keeping the snapshot in version control means the suite runs in under two
seconds and on a machine with no LibreOffice installed, while the figures
it checks against are still genuine spreadsheet output. The trade is that
the snapshot can go stale, so test_snapshot_is_current_with_the_workbook
compares file timestamps and fails loudly if the workbook has been rebuilt
without regenerating it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import evm

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "docs" / "generated" / "benchmark-values.json"
WORKBOOK = ROOT / "benchmark" / "EVM_Manual_Benchmark.xlsx"

BENCHMARK_PERIODS = (5, 6)
RUPEE_TOL = 0.01
RATIO_TOL = 1e-9


@pytest.fixture(scope="module")
def benchmark() -> dict:
    if not SNAPSHOT.exists():
        pytest.skip(
            "benchmark snapshot missing; run scripts/validate_benchmark.py"
        )
    return json.loads(SNAPSHOT.read_text())


def _expected(project, period):
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from validate_benchmark import engine_values
    return engine_values(project, period)


class TestParity:
    @pytest.mark.parametrize("period", BENCHMARK_PERIODS)
    def test_every_measure_agrees_with_the_manual_benchmark(
        self, project, benchmark, period
    ):
        """The headline validation result.

        Two independently written implementations of the EVM definitions,
        one in Python and one in Excel formulas, agree on every measure to
        the paisa and to nine decimal places on the indices.
        """
        mismatches = []
        for label, (tool_value, kind) in _expected(project, period).items():
            assert label in benchmark, f"{label} missing from the benchmark"
            bench_value = benchmark[label][str(period)]
            tolerance = RUPEE_TOL if kind == "rupee" else RATIO_TOL
            if abs(tool_value - bench_value) > tolerance:
                mismatches.append(
                    f"{label}: tool {tool_value!r} vs benchmark {bench_value!r}"
                )
        assert not mismatches, "\n".join(mismatches)

    def test_the_benchmark_covers_both_required_periods(self, benchmark):
        """The brief requires all indices computed manually for two periods."""
        for label, periods in benchmark.items():
            assert set(periods) == {str(p) for p in BENCHMARK_PERIODS}, label

    def test_the_benchmark_covers_every_measure_the_tool_reports(
        self, project, benchmark
    ):
        """No measure may be validated only against itself.

        If the tool grows a new index and the benchmark is not extended,
        that index is unvalidated. This fails rather than letting it pass
        silently.
        """
        expected = set(_expected(project, 6))
        assert expected <= set(benchmark), expected - set(benchmark)


class TestSnapshotIntegrity:
    def test_snapshot_is_current_with_the_workbook(self):
        """Guard against a stale snapshot.

        If the workbook has been rebuilt more recently than the snapshot,
        the figures below are from an older workbook and the parity result
        is meaningless.
        """
        if not (SNAPSHOT.exists() and WORKBOOK.exists()):
            pytest.skip("workbook or snapshot not built")
        assert SNAPSHOT.stat().st_mtime >= WORKBOOK.stat().st_mtime - 5, (
            "benchmark-values.json is older than the workbook it describes. "
            "Re-run scripts/validate_benchmark.py."
        )

    def test_snapshot_holds_real_numbers(self, benchmark):
        """A workbook that failed to recalculate yields nulls or strings."""
        for label, periods in benchmark.items():
            for period, value in periods.items():
                assert isinstance(value, (int, float)), f"{label} P{period}: {value!r}"


class TestIdentitiesHoldInExcelToo:
    """The algebraic identities, checked on the benchmark's own figures.

    These are the same identities asserted against the Python engine in
    test_forecasting.py. Confirming them on independently computed Excel
    values means the identity holds in both implementations, not just in
    the one that was written to satisfy it.
    """

    @pytest.mark.parametrize("period", BENCHMARK_PERIODS)
    def test_tcpi_to_eac1_equals_cpi(self, benchmark, period):
        key = str(period)
        assert benchmark["TCPI to EAC1"][key] == pytest.approx(
            benchmark["Cost performance index (CPI)"][key], abs=RATIO_TOL
        )

    @pytest.mark.parametrize("period", BENCHMARK_PERIODS)
    def test_vac_on_eac2_equals_cost_variance(self, benchmark, period):
        key = str(period)
        vac2 = benchmark["Budget at completion (BAC)"][key] - benchmark["EAC method 2"][key]
        assert vac2 == pytest.approx(benchmark["Cost variance (CV)"][key], abs=RUPEE_TOL)

    @pytest.mark.parametrize("period", BENCHMARK_PERIODS)
    def test_indices_reconcile_with_the_base_measures(self, benchmark, period):
        key = str(period)
        ev = benchmark["Earned value (EV)"][key]
        ac = benchmark["Actual cost (AC)"][key]
        pv = benchmark["Planned value (PV)"][key]
        assert benchmark["Cost performance index (CPI)"][key] == pytest.approx(
            ev / ac, abs=RATIO_TOL
        )
        assert benchmark["Schedule performance index (SPI)"][key] == pytest.approx(
            ev / pv, abs=RATIO_TOL
        )

    @pytest.mark.parametrize("period", BENCHMARK_PERIODS)
    def test_earned_schedule_is_consistent_with_actual_time(self, benchmark, period):
        key = str(period)
        es = benchmark["Earned schedule (ES)"][key]
        at = benchmark["Actual time (AT)"][key]
        assert at == pytest.approx(float(period))
        assert benchmark["Schedule performance index SPI(t)"][key] == pytest.approx(
            es / at, abs=RATIO_TOL
        )
        assert benchmark["Schedule variance, time SV(t)"][key] == pytest.approx(
            es - at, abs=RATIO_TOL
        )
