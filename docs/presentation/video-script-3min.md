# CE725 Team 40 — EVM Dashboard: 3-minute pitch video

**Written to the 30 October instruction: about 3 minutes, all five members on
video, NO slides, a demonstration of the tool explaining the interface and
presenting the results of the use case.**

Runs ~420 spoken words ≈ **3:00** at 140 words per minute. Each member speaks
once, in one unbroken block, and never returns.

---

## Production notes

| Block | Speaker | Runs | Words | On screen |
|---|---|---|---|---|
| 1 | **Sajjad Nakhwa** | 0:00–0:30 | ~65 | Dashboard top, Period 6 |
| 2 | **Dependar Arya** | 0:30–1:00 | ~55 | Sidebar + Data tab |
| 3 | **Neel Shah** | 1:00–1:45 | ~105 | Verdict bar → summary → CPI → TCPI |
| 4 | **Akshat Karkar** | 1:45–2:22 | ~90 | Variance → Performance trend → Forecast |
| 5 | **Pearsh Gumasta** | 2:22–3:00 | ~100 | Excel export, then repo link |

**No slides.** The deck is not used in this video at all. The screen shows the
running dashboard for the whole three minutes. Put the deck in the deliverables
folder as a document, not in the recording.

**Everyone on camera.** Screen share with the speaker's webcam as
picture-in-picture, bottom-right. Open and close with all five tiles visible so
every face is clearly on video, which is what the instruction asks for.

**One continuous take of the screen.** Set up once — browser at 100% zoom,
1920×1080, reporting period slider at 6, variance breakdown on Sub-level — and
drive the dashboard straight through. Speakers hand over without the screen
jumping.

**Say every number while it is visible.** Never quote a figure the viewer cannot
see on screen at that moment.

**Three things not to do.** Do not call the commentary AI-generated. Do not
describe the case study as real. Do not cut Pearsh's last two sentences.

---

## 1. Sajjad Nakhwa · 0:00–0:30

**ON SCREEN:** dashboard open at the top, Period 6. Cursor rests on the PV, AC and
EV tiles as they are named.

We're Team 40. I'm Sajjad Nakhwa, project lead. This project has spent ₹3.98
crore against a plan of ₹4.02 crore — under budget. Most monthly reports would
call that healthy. It isn't: it's 14.7 percent over budget and 19 days behind.
Spend against budget mixes two questions into one comparison. Our tool adds the
measurement that separates them, earned value, at every work package.

---

## 2. Dependar Arya · 0:30–1:00

**ON SCREEN:** sidebar, then open the **Data** tab so the input tables are visible.

I'm Dependar Arya, data lead. The case is a G+4 academic block: ₹14 crore,
twelve months, nineteen work packages, reported at month six. This data is
synthetic — plausible, but assumed, from no tender or invoice. The tool reads
three files: baseline, work breakdown, actuals. Replace those and everything you
are about to see recomputes.

---

## 3. Neel Shah · 1:00–1:45

**ON SCREEN:** back to the top. Cursor: verdict bar → plain-language summary → CPI
tile → TCPI tile, holding on TCPI.

I'm Neel Shah, I built the tool. It answers before it reports. The top line reads
*behind schedule and overspent* — that verdict comes from thresholds in one file,
so the same inputs always give the same answer.

Below it, in plain English: 24.8 percent complete against a plan of 28.7, 19 days
behind, finishing ₹2.06 crore over budget.

CPI is 0.872: every rupee returns 87 paise of budgeted work. And the number to
hold on to — TCPI, 1.051. That is how efficiently the remaining work must run to
finish on budget: 20 percent better than we have managed in any of six months.
The budget is gone.

---

## 4. Akshat Karkar · 1:45–2:22

**ON SCREEN:** open **Where the variance is** (Sub-level), then **Performance
trend**, then **Forecast**.

I'm Akshat Karkar, validation engineer — so where is the money? Excavation, CPI
0.689, 100 percent complete: that variance is final. Of ₹51 lakh of overrun, ₹38
lakh is already gone. Only ₹7.7 lakh is still live, in the frame.

On schedule, SPI returns to 1.00 on every project ever finished, however late — so
we use Earned Schedule: 19 days behind, which a site manager can act on.

The forecast gives four methods, ₹14.5 to ₹18 crore. We don't pick one; the spread
is the assumption kept visible.

---

## 5. Pearsh Gumasta · 2:22–3:00

**ON SCREEN:** the Excel export, then a final frame with the repository link and
all five members on camera.

I'm Pearsh Gumasta. How do we know it's right? Every number is checked against an
Excel workbook of typed formulas, evaluated by LibreOffice independently of our
code. Fifty of fifty agree, to the paisa, behind 150 passing tests.

But validation has a limit: both sides read the same percent-complete figure. If
site reports a package 60 percent complete when it's really 40, both compute the
same wrong earned value, every comparison agrees, and every index is confidently
wrong.

We validated the arithmetic to nine decimal places. The arithmetic was never the
risk. Everything is at the link on screen — it's live, please try it.
