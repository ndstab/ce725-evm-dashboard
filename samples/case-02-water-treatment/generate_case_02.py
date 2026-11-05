"""Generate a second synthetic case study, for testing the upload route.

Produces the same four files as `data/generate_case_study.py` in the same
format, describing a different project with a deliberately *opposite*
diagnosis.

The bundled case study (CE725-CASE-01) is over budget and behind
programme. This one is **under budget and behind programme**, which
exercises branches the first case never reaches:

  - CPI above 1.00, so the cost verdict is favourable
  - VAC positive — a forecast underrun rather than an overrun
  - TCPI below 1.00, meaning the budget is still reachable
  - a mixed verdict rather than a uniformly adverse one

The narrative: statutory approval for the intake structure was late, so
civil works started a month behind and the whole treatment train shifted
with them. What has been built was built efficiently — the delay has not
yet cost money, it has cost time.

Every figure here is ASSUMED. Budgets are order-of-magnitude plausible
for a plant of this capacity but are not taken from any tender, estimate
or invoice.

Run:  python samples/case-02-water-treatment/generate_case_02.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

LAKH = 100_000
OUT_DIR = Path(__file__).resolve().parent

PROJECT = {
    "project_name": "Water Treatment Plant (15 MLD) - Municipal",
    "project_code": "CE725-CASE-02",
    "currency": "INR",
    "baseline_periods": 10,
    "period_unit": "month",
    "data_date_period": 4,
    "period_labels": [
        "Jun-2026", "Jul-2026", "Aug-2026", "Sep-2026", "Oct-2026",
        "Nov-2026", "Dec-2026", "Jan-2027", "Feb-2027", "Mar-2027",
    ],
    "notes": (
        "Synthetic case study. All budgets, progress percentages and actual "
        "costs are assumed for teaching purposes and are not drawn from any "
        "real tender, estimate or invoice."
    ),
}

# id, parent, name, budget (Rs lakh), start, finish, curve
WBS = [
    ("1",   None, "Preliminaries",                             None, None, None, None),
    ("1.1", "1",  "Mobilisation and site establishment",         18,    1,    2, "linear"),
    ("1.2", "1",  "Temporary works and dewatering",              12,    1,    3, "linear"),

    ("2",   None, "Intake and Raw Water",                      None, None, None, None),
    ("2.1", "2",  "Intake structure civil works",                95,    2,    5, "s"),
    ("2.2", "2",  "Raw water pumping station",                   70,    3,    6, "s"),
    ("2.3", "2",  "Raw water rising main",                       55,    4,    7, "linear"),

    ("3",   None, "Treatment Units",                           None, None, None, None),
    ("3.1", "3",  "Flash mixer and flocculator",                 60,    4,    7, "s"),
    ("3.2", "3",  "Clarifier units",                            110,    5,    8, "s"),
    ("3.3", "3",  "Filter beds",                                125,    6,    9, "s"),
    ("3.4", "3",  "Chlorination and dosing house",               48,    7,    9, "linear"),

    ("4",   None, "Clear Water and Distribution",              None, None, None, None),
    ("4.1", "4",  "Clear water sump and pump house",             85,    7,   10, "s"),
    ("4.2", "4",  "Treated water rising main",                   52,    8,   10, "linear"),

    ("5",   None, "Electrical, Instrumentation and Handover",  None, None, None, None),
    ("5.1", "5",  "Electrical and SCADA installation",           90,    7,   10, "s"),
    ("5.2", "5",  "Testing, commissioning and handover",         30,   10,   10, "linear"),
]

# Cumulative percent complete and per-period actual cost (Rs lakh),
# periods 1 to 4.
ACTUALS = {
    # Preliminaries went in cleanly and slightly under estimate.
    "1.1": ([0.60, 1.00, 1.00, 1.00], [10.0,  7.0,  0.0,  0.0]),
    "1.2": ([0.40, 0.80, 1.00, 1.00], [ 4.5,  4.0,  3.0,  0.0]),

    # Intake structure: statutory clearance for the river bank works came
    # a month late, so the package started in Period 2 against a baseline
    # start of Period 2 but has run a month behind ever since. The work
    # done has been efficient — the delay has cost time, not money.
    "2.1": ([0.00, 0.10, 0.35, 0.75], [ 0.0,  7.0, 22.0, 38.0]),

    # Pumping station follows the intake and inherited its delay.
    "2.2": ([0.00, 0.00, 0.12, 0.42], [ 0.0,  0.0, 10.0, 19.5]),

    "2.3": ([0.00, 0.00, 0.00, 0.10], [ 0.0,  0.0,  0.0,  5.5]),
    "3.1": ([0.00, 0.00, 0.00, 0.05], [ 0.0,  0.0,  0.0,  3.2]),
}


def smoothstep(t: float) -> float:
    return 3 * t**2 - 2 * t**3


def period_fractions(start: int, finish: int, curve: str) -> dict[int, float]:
    n = finish - start + 1
    out, previous = {}, 0.0
    for k in range(1, n + 1):
        t = k / n
        cum = t if curve == "linear" else smoothstep(t)
        out[start + k - 1] = cum - previous
        previous = cum
    return out


def build() -> None:
    leaves = [row for row in WBS if row[3] is not None]
    n_periods = PROJECT["baseline_periods"]
    data_date = PROJECT["data_date_period"]

    with open(OUT_DIR / "wbs.csv", "w", newline="") as fh:
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

    with open(OUT_DIR / "baseline.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["wbs_id", "period", "pv_period_inr"])
        for wbs_id, _p, _n, budget, start, finish, curve in leaves:
            fractions = period_fractions(start, finish, curve)
            for period in range(1, n_periods + 1):
                w.writerow([
                    wbs_id, period,
                    round(fractions.get(period, 0.0) * budget * LAKH, 2),
                ])

    with open(OUT_DIR / "actuals.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["wbs_id", "period", "pct_complete_cum", "ac_period_inr"])
        for wbs_id, _p, _n, _b, _s, _f, _c in leaves:
            pct, ac = ACTUALS.get(wbs_id, ([0.0] * data_date, [0.0] * data_date))
            for period in range(1, data_date + 1):
                w.writerow([
                    wbs_id, period,
                    round(pct[period - 1], 4),
                    round(ac[period - 1] * LAKH, 2),
                ])

    bac = sum(row[3] for row in leaves) * LAKH
    meta = dict(PROJECT)
    meta["bac_inr"] = int(round(bac))
    meta["work_package_count"] = len(leaves)
    with open(OUT_DIR / "project.json", "w") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")

    print(f"Work packages : {len(leaves)}")
    print(f"BAC           : Rs {bac:,.0f}  ({bac / 1e7:.2f} crore)")
    print(f"Baseline      : {n_periods} periods, data date end of period {data_date}")
    print(f"Written to    : {OUT_DIR}")


if __name__ == "__main__":
    build()
