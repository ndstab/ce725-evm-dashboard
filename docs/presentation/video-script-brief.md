# Brief for the video script

**CE725 Topic 7 — Earned Value Management Dashboard · Team 20**

We are submitting the presentation as a pre-recorded video instead of
presenting live. This is everything the person writing the script needs.
Read this page first, then `docs/07-presentation.md`.

---

## 1. What the video has to be

The brief asks for a **15-minute demonstration**, and adds that any team
member may be asked to explain any formula or result. Recording the
presentation does not remove that second part — the individual viva is a
separate 15% of the grade, so the script is not a substitute for everyone
understanding the content.

Target **15:00**, and treat it as a hard number. A live presenter can
compress on the fly; a recording cannot, and running to 17 minutes is a
visible failure to follow the brief.

---

## 2. Start here: the two source files

| File | What it gives you |
|---|---|
| [`docs/07-presentation.md`](../07-presentation.md) | Slide-by-slide content, timings, what to point at during the demo, and 30-odd anticipated questions with answers |
| [`docs/presentation/CE725_Team20_EVM_Dashboard.pptx`](CE725_Team20_EVM_Dashboard.pptx) | The 12 slides themselves. Every slide's speaker notes already hold its narration cue |

Everything else listed in §7 below is background you can draw on, not
required reading.

---

## 3. The thing to know before you start

**`docs/07-presentation.md` is not yet a script.** Its *Say:* paragraphs
total **357 words — about two and a half minutes of the fifteen**. They
were written as cue cards for a presenter standing in a room who fills the
gaps by talking around the slides.

A recorded video has no gaps to fill. At a clear technical delivery pace
of roughly 140 words per minute, 15 minutes needs **1,900 to 2,100 words
of finished script**. So there is about five times as much writing to do
as there is already written, and the existing *Say:* lines are the spine
of it rather than a draft of it.

Budget per slide, at 140 wpm:

| Slide | Runs | Words |
|---|---|---|
| 1 Title | 0:30 | ~70 |
| 2 The problem in one number | 1:30 | ~210 |
| 3 The method | 1:30 | ~210 |
| 4 The case study | 1:00 | ~140 |
| 5 What we built | 0:30 | ~70 |
| 6 DEMO: the position | 2:00 | ~280 |
| 7 DEMO: where the variance is | 2:00 | ~280 |
| 8 DEMO: the schedule defect | 1:30 | ~210 |
| 9 DEMO: the forecast | 1:00 | ~140 |
| 10 How we know it is right | 1:30 | ~210 |
| 11 What we got wrong | 1:00 | ~140 |
| 12 What validation cannot do | 1:00 | ~140 |

Demo segments can carry slightly fewer words than this, because pointing
at the screen takes time. Everything else should hit its count.

---

## 4. Who speaks when

Every member should be heard, and each should speak to the part they
owned, because the examiner may come back to them on it individually.
Name each speaker on screen the first time they talk.

| Member | Role | Slides | Total |
|---|---|---|---|
| **Sajjad Nakhwa** | Project Lead and Finance Modeller | 1, 3, 9 | 3:00 |
| **Pearsh Gumasta** | Documentation and Reflection Lead | 2, 12 | 2:30 |
| **Deependra Arya** | Data Lead | 4, 7 | 3:00 |
| **Neel Shah** | AI and Tool Developer | 5, 6 | 2:30 |
| **Akshat Karkar** | Validation Engineer | 8, 10, 11 | 4:00 |

The logic: Sajjad takes the method and the forecasting because he chose
the formulas; Deependra takes the case study and the variance breakdown
because both come out of the WBS he built; Neel takes the tool itself;
Akshat takes validation, the discrepancies and the SPI defect; Pearsh
takes the opening framing and the closing argument, which are the two
"explain it to a non-specialist" moments.

---

## 5. What changes because it is recorded

**Slide 2 has a live-audience device that will not survive.** The script
says to ask "is this project healthy?", pause, and let the room answer
yes. On video there is no room. Replace it with a written question on
screen, two seconds of silence, then the reveal. The point still lands —
it just has to be staged rather than played.

**The demo can be recorded separately and cut in.** Slides 6 to 9 are
driven from the running dashboard. Record that screen capture on its own,
get it clean, and edit it under the narration. Which means:

- The contingency in §2 of the presentation document — "if the app fails
  to start, present from the screenshots" — is no longer needed. Delete
  that worry.
- Set the browser to 100% zoom and a 1920×1080 window so the figures are
  readable after compression.
- Reporting period slider on **6**, variance breakdown on **Sub-level**.

**Nobody can ask a clarifying question.** Anything ambiguous stays
ambiguous. Every number said aloud should also be visible on screen when
it is said.

**Add a 10-second close.** A live presentation ends by taking questions.
A video needs an ending: the repository link, and the fact that the tool,
the benchmark and all seven documents are in it.

---

## 6. The figures — use these, do not recompute

Every number below is the engine's own output at the data date, Period 6
(Sep 2026). If the script needs a figure that is not here, ask rather
than estimating it.

| | |
|---|---|
| BAC | ₹14.00 crore |
| Planned value (PV) | ₹4.02 crore |
| Earned value (EV) | ₹3.47 crore |
| Actual cost (AC) | ₹3.98 crore |
| Cost variance (CV) | −₹51.20 lakh, 14.7% over |
| CPI | 0.872 |
| SPI | 0.863 |
| SPI(t), Earned Schedule | 0.893 — **19 days behind** |
| TCPI to finish on budget | 1.051 |
| EAC range, four methods | ₹14.51 Cr to ₹17.98 Cr, a spread of ₹3.47 Cr |
| Variance that is final | ₹38 lakh, in three completed substructure packages |
| Variance still live | ₹7.7 lakh, in the frame |
| Worst package | Excavation and earthwork, CPI 0.689, 100% complete |
| Benchmark result | 50 of 50 comparisons agree, to ₹0.01 and 1×10⁻⁹ |
| Tests | 151, all passing |

**Three sentences worth getting word-perfect**, because they are the
argument of the whole project:

1. *"The remaining work must run at 1.051 efficiency. We have sustained
   0.872 for six months. The budget is gone; what remains is deciding who
   absorbs it."*
2. *"A Python re-implementation validates only your own understanding —
   misread a formula and both sides misread it identically, the
   comparison passes, and both are wrong."*
3. *"We validated the arithmetic to nine decimal places. The arithmetic
   was never the risk."*

---

## 7. Background, if you want it

Only if something in the above needs explaining. None of it is required
to write the script.

| File | Covers |
|---|---|
| [`docs/04-validation-report.md`](../04-validation-report.md) | How the benchmark works, and the six discrepancies behind slide 11 |
| [`docs/06-learnings-and-reflection.md`](../06-learnings-and-reflection.md) | Each member's own account of what they learned — useful for giving each speaker their own voice |
| [`docs/03-user-manual.md`](../03-user-manual.md) | What each dashboard screen shows, if a demo segment needs describing precisely |
| [`docs/02-method-note.md`](../02-method-note.md) | Why Earned Schedule, why synthetic data, what we took from prior art |
| `docs/img/` | Dashboard screenshots, if any segment cannot be screen-recorded |

---

## 8. Three things not to do

**Do not say the commentary is AI-generated.** It is template-driven and
deterministic, deliberately, and slide 12 and the AI usage log both turn
on that choice. Calling it AI-written contradicts our own argument and
invites a question we would then have to walk back.

**Do not present the case study as real.** Say "synthetic" early — slide
4 does it — and do not later describe it as though it came from a tender
or an invoice. The data is assumed and the documents say so in five
places.

**Do not soften slide 12.** It is the strongest thing in the project and
the temptation when recording is to end on something upbeat. The closing
point is that both implementations read the same inputs, so a wrong
percent-complete figure produces a wrong EV on both sides, all 50
comparisons still agree, and every index is confidently wrong. End there.
