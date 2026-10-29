# Earned Value Management Dashboard

**CE725 Construction Economics and Finance — Semester Course Project, Topic 7**

A work-package-level EVM tool for construction projects. It computes the
standard earned value measures, adds Earned Schedule, forecasts cost at
completion under four assumptions, locates the variance in the work
breakdown structure, and writes a plain-language monthly commentary.

Every figure it produces has been validated against an independent manual
benchmark built in Excel formulas and evaluated by a real spreadsheet
engine — **50 of 50 comparisons agree, to ₹0.01 on currency and 1×10⁻⁹ on
the indices**, across two reporting periods.

![Dashboard](docs/img/01-overview.jpg)

---

## The problem in one number

A project has spent **₹3.98 crore** against a plan of **₹4.02 crore**.

By the conventional reading it is marginally under budget and the report
writes itself. It has in fact completed only **₹3.47 crore** of work: it
is 14.7% over budget and 19 days behind programme, and the apparent health
is two errors pointing in opposite directions.

Budget against spend is two numbers, and two numbers give one comparison.
Separating *am I doing the work* from *is the work costing what it should*
needs a third measurement — the budgeted cost of the work actually
performed. That is earned value, and the rest of the method is bookkeeping
on top of it.

---

## Quick start

```bash
git clone https://github.com/ndstab/ce725-evm-dashboard.git
cd ce725-evm-dashboard
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app/streamlit_app.py
```

Opens at `http://localhost:8501` with a worked case study loaded, so it is
usable immediately without supplying data.

```bash
.venv/bin/python -m pytest tests/ -q          # 150 tests
.venv/bin/python scripts/validate_benchmark.py # full benchmark comparison
```

The second needs LibreOffice. The test suite does not.

---

## What it does

**Measures** — PV, EV, AC, BAC; CV, SV and their percentages; CPI, SPI.

**Earned Schedule** — ES, SV(t), SPI(t) and IEAC(t). Classical SPI has a
structural defect: at completion EV equals BAC and PV equals BAC, so
**SPI returns to 1.00 on every project however late it finishes**. The
index is at its most reassuring when the project is latest. Earned
Schedule measures in time instead, and reports "19 days behind" rather
than "0.863".

**Forecasting** — all four standard EAC methods with ETC, VAC and TCPI.
Presented as a range, not a single number, because they differ in one
assumption and the spread is the honest answer.

**Variance by work package** — the part a rolled-up project S-curve cannot
give you. A project CPI of 0.872 says something is wrong; this says that
₹38 lakh of the ₹51.20 lakh sits in three *completed* substructure
packages where it is final, and only ₹7.7 lakh is still live.

![Variance by work package](docs/img/02-variance-by-package.jpg)

**Plain-language commentary** — generated from templates, deterministically.
It does not call a language model, deliberately: a cost report must give
the same sentence from the same inputs every month, must not contain a
number that was never computed, and must have thresholds you can argue
with.

**Live-formula Excel export** — every figure a real formula. Edit a budget
or a percent complete and the indices, forecasts, verdict and charts all
recalculate. A quantity surveyor who has never seen this tool can work
with the output.

---

## Repository layout

```
evm/                  calculation engine
  dataset.py          loading and strict validation
  core.py             base measures, variances, indices, WBS breakdown
  earned_schedule.py  time-based schedule performance
  forecasting.py      EAC methods, ETC, VAC, TCPI
  commentary.py       deterministic plain-language narrative
  excel_export.py     live-formula workbook

app/                  Streamlit dashboard and Plotly charts
data/                 case study generator and generated inputs
benchmark/            the independent manual benchmark workbook
scripts/              benchmark evaluation and comparison
tests/                150 tests, expected values hand-derived
docs/                 all written deliverables
```

---

## Deliverables

| | |
|---|---|
| [Project charter](docs/01-project-charter.md) | Annexure B format, scope boundaries |
| [Method note and data sources](docs/02-method-note.md) | The method, why synthetic data, prior art |
| [User manual](docs/03-user-manual.md) | Inputs, how to read it, assumptions, limitations |
| [Validation report](docs/04-validation-report.md) | Hand calculations, 50-measure comparison, discrepancy log |
| [AI usage log](docs/05-ai-usage-log.md) | 31 entries, Annexure A format |
| [Learnings and reflection](docs/06-learnings-and-reflection.md) | All six required sections |
| [Presentation and viva prep](docs/07-presentation.md) | Slide content, demo script, expected questions |

---

## How it is validated

```
         Raw inputs
              |
      +-------+--------+
      |                |
 Python engine    Excel formulas
      |                |
      |         evaluated by
      |      LibreOffice headless
      |                |
      +----> compare <-+
           50 measures
```

The benchmark is **not** a second Python implementation, and that was the
most consequential decision in the project. A Python re-implementation
validates only your own understanding: misread a formula and both sides
misread it identically, the comparison passes, and both are wrong. So the
benchmark lives in a different execution environment and is **executed,
not re-implemented**.

Four discrepancies surfaced during development. All are recorded in the
validation report, including the two where the tool was right and we were
wrong — a hand calculation of EAC3 that rounded an intermediate index
mid-chain and came out ₹156 off, and two validation tests that were
themselves mis-constructed.

---

## What it does not do

No critical path (it reads a time-phased budget, not a network, so it
cannot say whether a slip moves the completion date). No re-baselining. No
retention, advance or cash flow — a project can be green on every index
here and still run out of money. Equal-length periods assumed. Single
project. Synthetic data only.

**And the one that governs the rest:**

Earned value is percent complete multiplied by budget, and percent
complete is a judgement made at site, often by someone with an interest in
the answer. If a package is reported at 60% when it is really 40%, the
engine computes a wrong EV, the benchmark computes **the same** wrong EV,
all 50 comparisons agree, and every index is confidently, precisely wrong.

No spreadsheet and no test suite detects this. Only a measurement at site
does. The quality of an EVM system is the quality of its percent-complete
measurement; everything in this repository is arithmetic on top of a
judgement made by a person standing on a site.

---

## Case study data

Synthetic. A G+4 RCC academic block, BAC ₹14.00 crore, 12-month baseline,
19 work packages, data date at the end of Period 6. Budgets are
order-of-magnitude plausible for an institutional building built to CPWD
DSR-style item rates — **they are assumed, and are not drawn from any
tender, estimate or invoice.** Reasoning in the
[method note](docs/02-method-note.md#22-why-synthetic-data).

---

## Prior art

[`Tahir-yamin/excel-scurve-builder`](https://github.com/Tahir-yamin/excel-scurve-builder)
(MIT) was read before this was designed. Three things were taken from it,
credited here and at each point of use: the live-formula workbook
approach; the argument that a self-check re-implementing the intended
logic validates only your own understanding; and its documentation of
Excel chart defaults that silently render broken charts. No code was
reused. It rolls each project up to a single percentage curve and lists
the absence of a WBS breakdown as a known limitation — that breakdown is
the main thing this tool adds, along with Earned Schedule and the
four-method forecast range.

---

## Built with

Python 3.12 · pandas · Streamlit · Plotly · openpyxl · pytest ·
LibreOffice (headless, for benchmark evaluation)

Built with AI assistance throughout, logged in full in
[docs/05-ai-usage-log.md](docs/05-ai-usage-log.md) — including where it
was wrong, where we were wrong, and where its output was rejected on
principle.
