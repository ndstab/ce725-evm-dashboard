# CE725 Team 20 — EVM Dashboard: Video Script (15:00)

**Speaker order revised so each member speaks once, in one unbroken block.**

The script runs about 2,090 spoken words, which is roughly 15:00 at 140 words a
minute; the remaining seconds go to the staged pause on slide 2, the beat before
the last line of slide 12, and cursor moves in the demo.

---

## Production notes

| Slide | Speaker | Runs | Words |
|---|---|---|---|
| 1 Title | **Sajjad** | 0:30 | ~75 |
| 2 The problem | **Sajjad** | 1:30 | ~205 |
| 3 The method | **Sajjad** | 1:30 | ~205 |
| 4 Case study | **Deependra** | 1:00 | ~150 |
| 5 What we built | **Deependra** | 0:30 | ~70 |
| 6 Demo: position | **Neel** | 2:00 | ~255 |
| 7 Demo: variance | **Neel** | 2:00 | ~245 |
| 8 Demo: schedule defect | **Akshat** | 1:30 | ~200 |
| 9 Demo: forecast | **Akshat** | 1:00 | ~135 |
| 10 Validation | **Akshat** | 1:30 | ~205 |
| 11 What we got wrong | **Pearsh** | 1:00 | ~145 |
| 12 What validation cannot do | **Pearsh** | 1:00 | ~160 |
| End card | **Pearsh** | 0:10 | ~15 |

**Time per speaker:** Sajjad 3:30 · Deependra 1:30 · Neel 4:00 · Akshat 4:00 ·
Pearsh 2:10.

**Names on screen.** Put a lower-third (name and role) once, on each speaker's
first slide: **Sajjad on 1, Deependra on 4, Neel on 6, Akshat on 8, Pearsh on 11.**
Because nobody returns, no second lower-third is ever needed.

**Numbers on screen.** Every figure is on its slide or on the dashboard when it
is said.

**Demo capture.** Record slides 6 to 9 separately: browser at 100% zoom,
1920×1080, reporting period slider at 6, variance breakdown on Sub-level. Cut it
in under the narration. Note that the demo block now spans two speakers — Neel
hands to Akshat between slides 7 and 8 — so record it in two passes.

**Three things not to do.** Do not call the commentary AI-generated. Do not
describe the case study as real. Do not soften slide 12.

---

## Slide 1 — Title · Sajjad Nakhwa · 0:00–0:30

**ON SCREEN:** title slide. Lower-third: *Sajjad Nakhwa, Project Lead and Finance
Modeller.*

Hello, we're Team 20. I'm Sajjad Nakhwa, project lead and finance modeller, and
you'll hear from all five of us today. We built a tool that tells a project
manager whether a project is in trouble, where the trouble is, and what it will
cost. But we want to spend most of our time on a harder question: how do we know
the numbers are right, and what can that checking still not tell us?

---

## Slide 2 — The problem, in one number · Sajjad Nakhwa · 0:30–2:00

**ON SCREEN, no voice:** a white card with only the question: *A project has spent
₹3.98 crore against a plan of ₹4.02 crore. Is it healthy?* Hold it for two seconds
of silence. Then continue.

Start with that question. A project has spent ₹3.98 crore against a plan of ₹4.02
crore. Spend is under plan. Most monthly reports would call that healthy.

**ON SCREEN:** the reveal, *14.7% over budget and 19 days behind programme.*

It isn't. The work actually completed is worth only ₹3.47 crore. The project is
14.7 percent over budget, and 19 days behind programme.

**ON SCREEN:** the three tiles, PV ₹4.02 Cr, AC ₹3.98 Cr, EV ₹3.47 Cr.

Put it in rupees. We have earned ₹3.47 crore of value, and it cost us ₹3.98 crore
to earn it. The gap is the overrun. Against the plan, we should have earned ₹4.02
crore by now, and we have earned ₹3.47. That shortfall is the lateness.

So how did the simple comparison miss both? Because budget against spend is two
numbers, and two numbers give you one comparison. That one comparison mixes two
different questions: are we doing the work, and is the work costing what it
should? Here the two errors point in opposite directions. We are behind on the
work, which makes spend look low. We are overpaying for the work we do, which
makes it look high. They cancel, and the report writes itself as healthy. You
cannot separate them without a third measurement. That third number is earned
value: the budgeted cost of the work actually performed.

---

## Slide 3 — The method · Sajjad Nakhwa · 2:00–3:30

**ON SCREEN:** the PV, EV, AC slide. As each is named, highlight its row. As the
comparisons are named, highlight the CV/CPI box, then the SV/SPI box.

I chose the formulas, so let me give you the whole method.

There are three measurements. Planned value, PV, is the budgeted cost of work
scheduled: what should have been done by now. Earned value, EV, is the budgeted
cost of work performed: what was actually done. And actual cost, AC, is what it
cost to do it.

Everything else is a comparison of two of those three. Put earned value against
actual cost, and you get cost. Cost variance is EV minus AC. The cost performance
index, CPI, is EV divided by AC. Put earned value against planned value, and you
get schedule. Schedule variance is EV minus PV, and the schedule performance
index, SPI, is EV divided by PV.

For both indices, one means on plan, and below one means we are getting less than
we planned for.

Take our project. EV is ₹3.47 crore and AC is ₹3.98 crore, so CPI is 0.872.
Against a PV of ₹4.02 crore, SPI is 0.863.

That is the whole method. The rest is bookkeeping on top of it. What our tool
adds is Earned Schedule, four forecasting methods, and the same calculation
repeated at every work package, not just for the project as a whole. Over to
Deependra for the data.

---

## Slide 4 — The case study · Deependra Arya · 3:30–4:30

**ON SCREEN:** case-study slide. Lower-third: *Deependra Arya, Data Lead.* Keep the
**Synthetic data** callout visible for the whole segment.

I'm Deependra Arya, data lead. Our case study is a G+4 reinforced-concrete
academic block. Budget at completion is ₹14.00 crore, over twelve months, split
into nineteen work packages. Our data date is the end of month six, September
2026.

One thing before anything else: this data is synthetic. The budgets are plausible
for a building of this size, but they are assumed. They do not come from any
tender, estimate or invoice. We will come back to why that choice matters.

We built the trouble in on purpose, and concentrated it, so the tool has
something to find. Hard rock in excavation puts that package 45 percent over
budget and two months late. That cascades into the footings and foundation
concrete. The frame then starts a month late, and runs an 18-day slab cycle
against a planned 12.

---

## Slide 5 — What we built · Deependra Arya · 4:30–5:00

**ON SCREEN:** the four-pieces slide. Light each piece as it is named. Cut to the
dashboard on the last line.

We built four pieces, in one repository. A Python engine that
computes every measure at work-package level. A Streamlit dashboard, which is the
tool you're about to see. A live-formula Excel export, for people who work in
Excel. And an independent manual benchmark, which is how we know the numbers are
right. The next four slides are all driven from the live dashboard, so over to Neel,
who built it.

---

## Slide 6 — DEMO: the position · Neel Shah · 5:00–7:00

**SCREEN CAPTURE:** top of the dashboard, period 6. Lower-third: *Neel Shah, AI and
Tool Developer.* Cursor moves in the order below. Zoom in on each figure as it is
named.

I'm Neel Shah, AI and tool developer.

*Cursor on the verdict bar (BEHIND SCHEDULE AND OVERSPENT)*

This is the top of the dashboard at reporting period six. The first thing you see
is the verdict bar: behind schedule and overspent. The answer comes before any of
the numbers. Its wording comes from thresholds written down in a single file, so
the same inputs give the same verdict every month.

*Cursor on the plain-language summary*

Below it is a plain-language summary. I'll read it as written.

> The project is 24.8 percent complete against a plan of 28.7 percent, having
> spent 28.5 percent of the budget. It is approximately 19 days behind
> programme and, if current cost performance continues, will finish about ₹2.06
> crore over a budget of ₹14.00 crore. Returning to budget would require a 21
> percent improvement in cost efficiency on all remaining work.

Notice that it never quotes an index without the consequence beside it. A CPI of
0.872 means nothing to most readers on its own, so the tool says what it means.

*Cursor on CPI 0.872*

CPI is 0.872: every rupee spent returns 87 paise of budgeted work. The other 12.8
paise bought nothing that appears in the budget.

*Cursor on TCPI 1.051, hold there to the end of the segment*

Now the number I'd ask you to hold on to. TCPI is 1.051. It answers one question:
from here to the end, how efficiently must the remaining work run if we are to
finish on budget?

The remaining work must run at 1.051 efficiency. We have sustained 0.872 for six
months. That is a 20.6 percent improvement on performance never once achieved.
The budget is gone; what remains is deciding who absorbs it.

---

## Slide 7 — DEMO: where the variance is · Neel Shah · 7:00–9:00

**SCREEN CAPTURE:** open *Where the variance is*, breakdown set to Sub-level. Cursor
order: excavation row, then the two frame rows, then the ₹38 lakh and ₹7.7 lakh
figures.

A project CPI of 0.872 says something is wrong. It does not say what to do. This
screen, *Where the variance is*, does. I've set the breakdown to sub-level, so
every work package is visible.

*Cursor on excavation and earthwork*

Start with excavation and earthwork. CPI 0.689, and it is 100 percent complete.
This variance is final. No recovery plan touches it: the work is done and the
money is spent.

*Cursor on the two frame packages*

Now the frame packages, 22 and 14 percent complete. Those can still move. That is
why percent complete matters here. At 100 percent there is nothing left to spend,
so the overrun is permanent. At 22 percent, most of the work is still ahead, and
the cost trend can still be changed. Two packages can show a poor CPI and need
opposite responses.

*Cursor on ₹38 lakh, then ₹7.7 lakh*

Of the ₹51.20 lakh cost variance, ₹38 lakh sits in three completed substructure
packages. Only ₹7.7 lakh is live, in the frame. So the advice is: stop trying to
recover the substructure, protect the frame, and tell the client ₹38 lakh is
gone.

This is why we carried the work breakdown structure through the whole
calculation, instead of rolling up to one project curve. A single CPI tells you
the project is in trouble. The package view tells you which part of that trouble
is already history, and which part is still ours to manage.

---

## Slide 8 — DEMO: the schedule defect · Akshat Karkar · 9:00–10:30

**SCREEN CAPTURE:** open *Performance trend*. Lower-third: *Akshat Karkar, Validation
Engineer.* Cursor order: SPI figure, the 19 days behind figure, then the CPI and
SPI lines across the six periods.

I'm Akshat Karkar, validation engineer. SPI reads 0.863. There is a problem with
that number, and it is structural.

SPI is EV divided by PV. At completion, EV must equal BAC, and PV must equal BAC.
So SPI returns to 1.00 on every project ever completed, however late. Picture a
project that finishes a year late. On its last day everything has been earned and
everything was scheduled, and SPI reads a perfect 1.00. The index gets more
reassuring as the project gets later.

*Cursor on 19 days behind*

Earned Schedule fixes that by asking when, on the baseline, this much value was
scheduled to have been earned. The answer is a time: 19 days behind. Its index,
SPI(t), reads 0.893. A site manager can act on nineteen days. Nobody can act on
0.863.

*Cursor along the CPI and SPI lines*

Now the trend. CPI is flat, between 0.86 and 0.88, across all six periods, while
SPI swings down to about 0.74 and back. Cost performance stabilises early and
rarely recovers. That is the strongest argument against an optimistic recovery
plan.

---

## Slide 9 — DEMO: the forecast · Akshat Karkar · 10:30–11:30

**SCREEN CAPTURE:** open *Forecast*. Cursor on the lowest figure (₹14.51 Cr), then
the highest (₹17.98 Cr), then the spread (₹3.47 Cr). Cut back to slides on the
last line.

Last screen: the forecast. Four standard methods for estimate at completion,
running from ₹14.51 crore to ₹17.98 crore, a spread of ₹3.47 crore.

We deliberately do not pick one. They differ in a single assumption: what you
believe about the remaining work. One assumes performance continues as it is now.
One assumes the overrun was a one-off. The others assume schedule pressure
continues, which normally costs money, because acceleration does. Choosing one
quietly would hide that assumption; showing the range keeps it visible to whoever
has to decide who absorbs the overrun.

That spread is the method being honest, not failing. Narrowing it needs a
judgement nobody can make arithmetically: was the rock a closed event, or a
symptom of a site that was never properly investigated? Now, back to the slides.

---

## Slide 10 — How we know it is right · Akshat Karkar · 11:30–13:00

**ON SCREEN:** the pipeline diagram. Light each box as it is named: Raw inputs,
Python engine, Excel formulas, LibreOffice headless, Compare. Then the 50 / 50 and
151 tiles as they are said.

So how do we know any of this is right? Raw inputs go down two paths. One is our
Python engine. The other is an Excel workbook of typed formulas, evaluated by
LibreOffice running headless. That workbook is not our logic re-written in Python;
LibreOffice calculates it independently of our code, and we read its results back.
We then compare fifty measures across two reporting periods. Fifty of fifty agree,
to one paisa on currency and one part in a billion on indices.

Behind that sit 151 automated tests, all passing. We worked out their expected
values by hand before the engine existed, so the tests could not simply echo the
code.

But the decision that mattered most was what we did not do. We did not write a
second Python implementation. A Python re-implementation validates only your own
understanding. Misread a formula and both sides misread it identically, the
comparison passes, and both are wrong. So the benchmark lives in a different
execution environment, and it is executed, not re-implemented. That is the
difference between two checks, and one check done twice.

---

## Slide 11 — What we got wrong · Pearsh Gumasta · 13:00–14:00

**ON SCREEN:** the four-row discrepancy table. Lower-third: *Pearsh Gumasta,
Documentation and Reflection Lead.* Highlight each row as it is named, and hold on
row two for the last paragraph.

I'm Pearsh Gumasta, documentation and reflection lead. Validation also found four
things we got wrong, all recorded.

First: EAC3 was off by ₹156. Our hand calculation was wrong, not the engine; we
had rounded mid-chain. The rule we adopted: rounding is presentation only.
Second: two validation tests failed, and the tests were wrong, not the engine.
Third: the executive summary was invisible under the dark theme. Every number was
right and the tool was unusable, and no test caught it. Fourth: the carry-forward
routine was fragile on gaps. Clean data hid it; real data would not.

The second one matters most. The fast route to a green test suite was to change
the engine until the tests passed. That would have deleted a correct rule, the one
that rejects earned value being double-counted.

---

## Slide 12 — What validation cannot do · Pearsh Gumasta · 14:00–15:00

**ON SCREEN:** the 60% reported / 40% actual slide. Reveal the four numbered steps
one at a time, timed to the sentences below. Do not rush this slide. Leave one
second of silence before the final paragraph.

This brings me to the closing point, and I'd ask you to stay with it. Both
implementations read the same inputs. Suppose a package is reported 60 percent
complete when it is really 40. The engine computes a wrong earned value. The
benchmark computes the same wrong earned value. All fifty comparisons agree. Every
index is confidently wrong.

Earned value is percent complete times budget. And percent complete is a
judgement, made at site, by someone who may be paid more if it is higher. We
validated the arithmetic to nine decimal places. The arithmetic was never the
risk.

Every design choice that makes this dashboard more persuasive makes the problem
worse. It renders an unverifiable judgement with six-figure precision, a traffic
light and a chart.

The quality of an EVM system is the quality of its percent-complete measurement.
Everything else, including all of our work, is arithmetic on top of a judgement
made by a person standing on a site.

---

## End card · Pearsh Gumasta · about 10 seconds

**ON SCREEN:** plain card, no music sting, no thank-you slide. Live tool:
`https://ce725-evm-dashboard-3hfqkptabnvbzvzyb8uopr.streamlit.app`
and `github.com/ndstab/ce725-evm-dashboard`. Team 20 names underneath.

The tool, the benchmark and all seven documents are in our repository, linked on
screen.
