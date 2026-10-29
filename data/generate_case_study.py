"""Generate the CE725 case-study project data.

Produces three CSVs and one JSON that together describe a synthetic but
realistic construction project, used as the worked example for the EVM
dashboard and as the source of the manual benchmark case.

The project is a G+4 RCC academic block, BAC Rs 14.00 crore, 12-month
baseline, reported monthly. The data date is the end of Period 6, so six
periods are reported and six remain.

Every figure here is ASSUMED. Budgets are order-of-magnitude plausible for
an institutional building of this size built to CPWD DSR-style item rates,
but they are not taken from any tender, estimate or invoice. The purpose of
the data is to exercise the EVM method, not to price a real building.

The underlying narrative, which the numbers are built to express:

  - Hard rock was encountered in excavation (WBS 2.1). The package finished
    two months late and 45% over budget.
  - The delay cascaded into footings and foundation RCC (2.2, 2.3), both of
    which overran on cost and finished late.
  - Superstructure (3.1, 3.2) therefore started a month late and is running
    well behind its planned slab cycle.
  - Staircase and lift core RCC (3.3) has not started at all.
  - Nothing downstream of the frame has begun.

Run:  python data/generate_case_study.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

LAKH = 100_000
DATA_DIR = Path(__file__).resolve().parent

# --------------------------------------------------------------------------
# Project constants
# --------------------------------------------------------------------------

PROJECT = {
    "project_name": "Academic Block (G+4 RCC) - Institutional Campus",
    "project_code": "CE725-CASE-01",
    "currency": "INR",
    "baseline_periods": 12,
    "period_unit": "month",
    "data_date_period": 6,
    "period_labels": [
        "Apr-2025", "May-2025", "Jun-2025", "Jul-2025",
        "Aug-2025", "Sep-2025", "Oct-2025", "Nov-2025",
        "Dec-2025", "Jan-2026", "Feb-2026", "Mar-2026",
    ],
    "notes": (
        "Synthetic case study. All budgets, progress percentages and actual "
        "costs are assumed for teaching purposes and are not drawn from any "
        "real tender, estimate or invoice."
    ),
}

# --------------------------------------------------------------------------
# Work breakdown structure
#
# budget_lakh    : budget at completion for the work package, in Rs lakh
# start, finish  : baseline start and finish period (inclusive)
# curve          : how the budget is spread across those periods
#                  "linear" - equal amount each period
#                  "s"      - smoothstep, slow start, fast middle, slow finish
# --------------------------------------------------------------------------

WBS = [
    # id,    parent, name,                                        budget, start, finish, curve
    ("1",    None,  "Preliminaries and Site Establishment",          None,  None, None, None),
    ("1.1",  "1",   "Site mobilisation and enabling works",          25,    1,    2,    "linear"),
    ("1.2",  "1",   "Site office, stores and labour accommodation",  18,    1,    2,    "linear"),

    ("2",    None,  "Substructure",                                  None,  None, None, None),
    ("2.1",  "2",   "Excavation and earthwork",                      42,    1,    3,    "linear"),
    ("2.2",  "2",   "PCC and footings",                              68,    2,    4,    "s"),
    ("2.3",  "2",   "Foundation RCC up to plinth",                   95,    3,    5,    "s"),
    ("2.4",  "2",   "Plinth beams and backfilling",                  38,    4,    5,    "linear"),

    ("3",    None,  "Superstructure",                                None,  None, None, None),
    ("3.1",  "3",   "RCC columns, ground to fourth floor",          145,    5,    9,    "s"),
    ("3.2",  "3",   "RCC beams and slabs, ground to fourth floor",  210,    5,   10,    "s"),
    ("3.3",  "3",   "Staircase and lift core RCC",                   55,    6,   10,    "linear"),

    ("4",    None,  "Masonry and Finishes",                          None,  None, None, None),
    ("4.1",  "4",   "Block masonry",                                 88,    7,   11,    "s"),
    ("4.2",  "4",   "Internal plaster",                              52,    9,   12,    "s"),
    ("4.3",  "4",   "External plaster and texture finish",           46,    9,   12,    "linear"),
    ("4.4",  "4",   "Flooring, vitrified tile and kota stone",       95,   10,   12,    "s"),
    ("4.5",  "4",   "Painting, internal and external",               62,   11,   12,    "linear"),

    ("5",    None,  "Building Services",                             None,  None, None, None),
    ("5.1",  "5",   "Internal electrification",                     105,    7,   12,    "s"),
    ("5.2",  "5",   "Plumbing and sanitary installation",            72,    7,   12,    "s"),
    ("5.3",  "5",   "HVAC and fire fighting",                        98,    9,   12,    "s"),

    ("6",    None,  "External Works and Handover",                   None,  None, None, None),
    ("6.1",  "6",   "External development and landscaping",          58,   10,   12,    "linear"),
    ("6.2",  "6",   "Testing, commissioning and handover",           28,   12,   12,    "linear"),
]

# --------------------------------------------------------------------------
# Actuals, reported monthly up to the data date (Period 6)
#
# pct : cumulative physical percent complete of the work package at the end
#       of each reported period. This is the measured quantity; earned value
#       is pct x budget, so the quality of the EV figure is entirely the
#       quality of this measurement.
# ac  : actual cost incurred IN that period, in Rs lakh.
# --------------------------------------------------------------------------

ACTUALS = {
    #          pct complete, cumulative, periods 1..6      actual cost per period, periods 1..6
    "1.1": ([0.55, 1.00, 1.00, 1.00, 1.00, 1.00], [15.0, 12.0,  0.0,  0.0,  0.0,  0.0]),
    "1.2": ([0.50, 1.00, 1.00, 1.00, 1.00, 1.00], [ 9.5,  9.0,  0.0,  0.0,  0.0,  0.0]),

    # Hard rock encountered from the second week of Period 1. Pneumatic
    # breaking and controlled blasting were required for roughly 60% of the
    # excavated volume, against an estimate that assumed ordinary soil
    # throughout. The package finished in Period 5 against a baseline of
    # Period 3, and cost 61.0 lakh against a budget of 42.0 lakh.
    "2.1": ([0.20, 0.45, 0.72, 0.90, 1.00, 1.00], [11.0, 15.0, 16.5, 11.0,  7.5,  0.0]),

    "2.2": ([0.00, 0.15, 0.42, 0.78, 1.00, 1.00], [ 0.0, 11.0, 19.5, 25.0, 18.5,  0.0]),
    "2.3": ([0.00, 0.00, 0.18, 0.46, 0.80, 1.00], [ 0.0,  0.0, 19.0, 30.0, 34.0, 25.0]),
    "2.4": ([0.00, 0.00, 0.00, 0.20, 0.62, 1.00], [ 0.0,  0.0,  0.0,  8.5, 16.0, 16.5]),

    # Superstructure started a month late because the foundation was not
    # released. Slab cycle is running at roughly 18 days against a planned
    # 12 days.
    "3.1": ([0.00, 0.00, 0.00, 0.00, 0.08, 0.22], [ 0.0,  0.0,  0.0,  0.0, 13.0, 23.0]),
    "3.2": ([0.00, 0.00, 0.00, 0.00, 0.05, 0.14], [ 0.0,  0.0,  0.0,  0.0, 12.0, 21.0]),
    "3.3": ([0.00, 0.00, 0.00, 0.00, 0.00, 0.00], [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0]),
}


def smoothstep(t: float) -> float:
    """Cumulative fraction of a package complete at normalised time t.

    3t^2 - 2t^3. Zero slope at both ends, so the package ramps up and tails
    off rather than starting and stopping abruptly. This is the usual shape
    of a construction work package and is what makes the aggregate planned
    value curve an S-curve.
    """
    return 3 * t**2 - 2 * t**3


def period_fractions(start: int, finish: int, curve: str) -> dict[int, float]:
    """Fraction of a package's budget planned in each period it spans."""
    n = finish - start + 1
    cum = []
    for k in range(1, n + 1):
        t = k / n
        cum.append(t if curve == "linear" else smoothstep(t))
    out = {}
    previous = 0.0
    for k, c in enumerate(cum, start=1):
        out[start + k - 1] = c - previous
        previous = c
    return out


def build() -> None:
    leaves = [row for row in WBS if row[3] is not None]
    n_periods = PROJECT["baseline_periods"]
    data_date = PROJECT["data_date_period"]

    # ---- wbs.csv --------------------------------------------------------
    with open(DATA_DIR / "wbs.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "wbs_id", "parent_id", "name", "is_leaf", "budget_inr",
            "planned_start_period", "planned_finish_period", "curve",
        ])
        for wbs_id, parent, name, budget, start, finish, curve in WBS:
            w.writerow([
                wbs_id, parent or "", name, "Y" if budget is not None else "N",
                int(round(budget * LAKH)) if budget is not None else "",
                start or "", finish or "", curve or "",
            ])

    # ---- baseline.csv ---------------------------------------------------
    with open(DATA_DIR / "baseline.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["wbs_id", "period", "pv_period_inr"])
        for wbs_id, _parent, _name, budget, start, finish, curve in leaves:
            fractions = period_fractions(start, finish, curve)
            for period in range(1, n_periods + 1):
                pv = fractions.get(period, 0.0) * budget * LAKH
                w.writerow([wbs_id, period, round(pv, 2)])

    # ---- actuals.csv ----------------------------------------------------
    with open(DATA_DIR / "actuals.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["wbs_id", "period", "pct_complete_cum", "ac_period_inr"])
        for wbs_id, _parent, _name, _budget, _start, _finish, _curve in leaves:
            pct_series, ac_series = ACTUALS.get(
                wbs_id, ([0.0] * data_date, [0.0] * data_date)
            )
            for period in range(1, data_date + 1):
                w.writerow([
                    wbs_id, period,
                    round(pct_series[period - 1], 4),
                    round(ac_series[period - 1] * LAKH, 2),
                ])

    # ---- project.json ---------------------------------------------------
    bac = sum(row[3] for row in leaves) * LAKH
    meta = dict(PROJECT)
    meta["bac_inr"] = int(round(bac))
    meta["work_package_count"] = len(leaves)
    with open(DATA_DIR / "project.json", "w") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")

    print(f"Work packages : {len(leaves)}")
    print(f"BAC           : Rs {bac:,.0f}  ({bac / 1e7:.2f} crore)")
    print(f"Baseline      : {n_periods} periods, data date end of period {data_date}")
    print(f"Written to    : {DATA_DIR}")


if __name__ == "__main__":
    build()
