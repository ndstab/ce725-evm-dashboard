# Case study 2 — Water Treatment Plant (15 MLD)

A second synthetic project, in the same four-file format as `data/`, for
testing the dashboard's **Upload your own** route.

## How to use it

Open the tool, choose **Upload your own** in the sidebar, and supply the
four files in this folder: `wbs.csv`, `baseline.csv`, `actuals.csv` and
`project.json`. The whole dashboard recomputes on them.

Regenerate them at any time with:

```bash
python samples/case-02-water-treatment/generate_case_02.py
```

## Why this project is different

The bundled case study (CE725-CASE-01) is **over budget and behind
programme** — adverse on both axes. That leaves every favourable branch of
the tool unexercised. This project is **under budget and behind
programme**, which is a genuinely different diagnosis and a different
management conversation.

| | Case 01 (bundled) | Case 02 (this one) |
|---|---|---|
| Project | G+4 academic block | 15 MLD water treatment plant |
| BAC | ₹14.00 crore | ₹8.50 crore |
| Baseline | 12 months | 10 months |
| Data date | Period 6 | Period 4 |
| Work packages | 19 | 13 |
| CPI | 0.872 — over budget | **1.041 — under budget** |
| SPI | 0.863 | 0.827 |
| SPI(t) | 0.893, 19 days behind | 0.909, 11 days behind |
| TCPI to BAC | 1.051 — budget unreachable | **0.992 — budget still reachable** |
| VAC | −₹2.06 crore overrun | **+₹33.29 lakh underrun** |
| Verdict | BEHIND SCHEDULE AND OVERSPENT | **BEHIND SCHEDULE** |

The EAC range is also more interesting here: it **straddles the budget**,
running from ₹8.17 crore under EAC1 to ₹9.60 crore under EAC3. The four
methods disagree about whether this project overruns at all, which is a
sharper illustration of why the tool shows the range than the first case
study manages.

## The narrative behind the numbers

Statutory clearance for the river-bank intake works came a month late, so
civil works started behind and the treatment train shifted with them. What
has been built has been built efficiently. The delay has cost time, not
money — so far. Whether it stays that way depends on whether the
programme can be recovered without acceleration, which is precisely the
question EAC3 is asking.

## What it found

Running this project through the tool immediately exposed a defect. The
executive summary's closing sentence was generated unconditionally from
TCPI ÷ CPI, so a project already forecast to underrun was told that
"returning to budget would require a **−5% improvement** in cost
efficiency". Every number was correct and the sentence was nonsense.

It is written up as discrepancy 5.5 in `docs/04-validation-report.md`, and
`tests/test_commentary.py` now pins the corrected behaviour against this
project. That is the argument for this folder existing: a single case
study, however carefully built, only tests the paths it happens to take.

## These figures are assumed

Budgets are order-of-magnitude plausible for a plant of this capacity.
They are **not** taken from any tender, estimate or invoice, and no claim
is made that they are accurate unit rates.
