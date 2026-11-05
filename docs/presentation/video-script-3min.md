# CE725 Team 40 — EVM Dashboard: 3-minute pitch video

**Written to the 30 October instruction: about 3 minutes, all five members on
video, NO slides, a demonstration of the tool explaining the interface and
presenting the results of the use case.**

451 spoken words. That is 3:13 at a careful 140 words a minute and 3:00 at
the 150 most people actually hit in conversation — so time a read-through
before recording, and if you are running long, the sentence to lose is
Neel's "twenty percent better than we've managed in any of six months".

Written to be **spoken, not read**. Contractions, short sentences, the odd
"so" and "right" — say it the way you would to someone standing next to you at
the screen. Don't read it off the page; learn the shape of your bit and the
figures, then talk.

---

## Production notes

| Block | Speaker | Runs | On screen |
|---|---|---|---|
| 1 | **Sajjad Nakhwa** | 0:00–0:30 | Dashboard top, Period 6 |
| 2 | **Dependar Arya** | 0:30–1:00 | Sidebar + Data tab |
| 3 | **Neel Shah** | 1:00–1:45 | Verdict bar → summary → CPI → TCPI |
| 4 | **Akshat Karkar** | 1:45–2:22 | Variance → Performance trend → Forecast |
| 5 | **Pearsh Gumasta** | 2:22–3:00 | Excel export, then the live link |

**No slides.** The running dashboard fills all three minutes. The deck goes in
the deliverables folder as a document, not in the recording.

**Everyone on camera.** Screen share with the speaker's webcam
picture-in-picture, bottom-right. Open and close with all five tiles visible.

**One continuous screen take.** Set up once — browser at 100% zoom, 1920×1080,
reporting period slider at 6, variance breakdown on Sub-level — and drive it
straight through.

**Say every number while it is visible.** Never quote a figure the viewer
cannot see on screen at that moment.

**The numbers are the one thing to get exactly right.** Everything else can
come out however it comes out. 0.872, 1.051, 19 days, ₹38 lakh, ₹7.7 lakh,
50 of 50, 151 tests.

**Three things not to do.** Don't call the commentary AI-generated. Don't
describe the case study as real. Don't cut Pearsh's last two lines.

---

## 1. Sajjad Nakhwa · 0:00–0:30

**ON SCREEN:** dashboard open at the top, Period 6. Cursor on the PV, AC and EV
tiles as they are named.

Hi, we're Team 40 — I'm Sajjad, I led the project. So, look at this. We've
spent 3.98 crore against a plan of 4.02. Under budget, right? Most reports
would call that healthy.

It's not. It's 14.7 percent over budget, and 19 days behind.

Budget versus spend is one comparison trying to answer two questions at once.
So we add the measurement that separates them — earned value.

---

## 2. Dependar Arya · 0:30–1:00

**ON SCREEN:** sidebar, then open the **Data** tab so the input tables show.

Hi, I'm Dependar, I handled the data. So the case is a G+4 academic block —
fourteen crore, twelve months, nineteen packages, reported at the end of month
six.

One thing upfront: this data is synthetic. Plausible for a building this size,
but assumed — not from any real tender or invoice.

The tool reads three files. Baseline, work breakdown, actuals. Swap those out
and everything recalculates.

---

## 3. Neel Shah · 1:00–1:45

**ON SCREEN:** back to the top. Cursor: verdict bar → summary → CPI tile →
TCPI, holding on TCPI.

I'm Neel, I built the tool. So it answers before it reports. Top line — behind
schedule and overspent. That verdict comes from thresholds in one file, so the
same inputs always give you the same answer.

Below it, in plain English. 24.8 percent complete against a plan of 28.7, 19
days behind, finishing 2.06 crore over budget.

CPI is 0.872 — every rupee you spend buys 87 paise of budgeted work.

And this one I'd remember. TCPI, 1.051. That's how efficiently the rest has to
run to finish on budget. Twenty percent better than we've managed in any of six
months. So, realistically — the budget's gone.

---

## 4. Akshat Karkar · 1:45–2:22

**ON SCREEN:** open **Where the variance is** (Sub-level), then **Performance
trend**, then **Forecast**.

I'm Akshat, I did the validation. So where's the money actually gone?

Excavation — CPI 0.689, and it's 100 percent complete, so that variance is
final. Of 51 lakh of overrun, 38 lakh is already spent. Only 7.7 lakh is still
live, in the frame.

On schedule, here's the thing. SPI goes back to 1.00 on every project that ever
finished, however late. So we use Earned Schedule — 19 days behind. You can act
on that.

The forecast gives four methods, 14.5 up to 18 crore. We don't pick one. The
spread is the assumption, kept visible.

---

## 5. Pearsh Gumasta · 2:22–3:00

**ON SCREEN:** the Excel export, then a final frame showing the live tool link
with all five members on camera.

I'm Pearsh. So how do we know any of this is right?

Every number's checked against an Excel workbook of typed formulas, evaluated
by LibreOffice — independent of our code. Fifty out of fifty agree, to the
paisa. Plus 151 tests passing.

But here's the limit. Both sides read the same percent-complete figure. So if
site reports a package at 60 percent when it's really 40, both compute the same
wrong earned value, all fifty still agree, and every index is confidently
wrong.

We validated the arithmetic to nine decimal places. The arithmetic was never
the risk.

It's all at the link on screen. It's live — please try it.
