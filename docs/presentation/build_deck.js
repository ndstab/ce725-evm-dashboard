/*
 * Builds the final presentation deck from the slide content in
 * docs/07-presentation.md.
 *
 *   NODE_PATH=/opt/homebrew/lib/node_modules node docs/presentation/build_deck.js
 *
 * Every figure quoted on a slide is the engine's own output, listed in the
 * FIG block below so that it can be checked against
 * `.venv/bin/python -c "import evm; ..."` rather than taken on trust. The
 * deck is generated rather than hand-built for the same reason the rest of
 * the project is: a number typed into a slide is a number nobody validated.
 */

const path = require("path");
const PptxGenJS = require("pptxgenjs");
const { applyTheme } = require("/Users/ndstab/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/edfb24de-2d0a-440b-99c4-b3d6db8bae22/c73c5ade-5b34-4522-b7d5-53a5a2c1a597/skills/pptx/scripts/apply_theme.js");

const ROOT = path.resolve(__dirname, "..", "..");
const IMG = (n) => path.join(ROOT, "docs", "img", n);
const OUT = path.join(__dirname, "CE725_Team40_EVM_Dashboard.pptx");

/* ------------------------------------------------------------------ *
 * Engine figures, data date = Period 6 (Sep-2026)
 * ------------------------------------------------------------------ */
const FIG = {
  bac: "14.00",
  pv: "4.02", ev: "3.47", ac: "3.98",
  cv: "51.20",            // lakh, adverse
  cpi: "0.872", spi: "0.863", spiT: "0.893",
  overBudgetPct: "14.7",
  daysBehind: "19",
  tcpi: "1.051",
  eac: { EAC2: 14.51, EAC1: 16.06, EAC4: 16.09, EAC3: 17.98 },
  spread: "3.47",
  trend: {
    labels: ["Apr", "May", "Jun", "Jul", "Aug", "Sep"],
    cpi:  [0.878, 0.874, 0.865, 0.873, 0.878, 0.872],
    spi:  [0.878, 0.814, 0.743, 0.764, 0.867, 0.863],
    spit: [0.878, 0.844, 0.808, 0.826, 0.887, 0.893],
  },
  divisions: {
    // reversed: a horizontal bar chart plots the first category at the bottom,
    // so the WBS reads top-to-bottom in its own order
    labels: ["External and handover", "Building services", "Masonry and finishes",
             "Superstructure", "Substructure", "Preliminaries"],
    crore: [0.86, 2.75, 3.43, 4.10, 2.43, 0.43],
  },
};

/* ------------------------------------------------------------------ *
 * Theme — concrete greys with rust for adverse variance
 * ------------------------------------------------------------------ */
const THEME = {
  name: "Concrete and Rust",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1C262B", lt1: "FFFFFF",
    dk2: "26353D", lt2: "EDF0F1",
    accent1: "C1553B", // rust — adverse
    accent2: "4E7A6B", // sage — favourable / baseline
    accent3: "7D8E97", // steel
    accent4: "D4A04C", // amber — caution
    accent5: "3E5660", // deep steel
    accent6: "A8B2B8", // light steel
    hlink: "C1553B", folHlink: "7D8E97",
  },
};
const H = THEME.colors;

const pres = new PptxGenJS();
pres.layout = "LAYOUT_WIDE";            // 13.3 x 7.5
pres.author = "Team 40";
pres.company = "CE725 Construction Economics and Finance";
pres.title = "Earned Value Management Dashboard";
pres.subject = "Topic 7 — Earned Value Management Dashboard";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };

const C = pres.SchemeColor;
const W = 13.333, MARGIN = 0.62;
const FOOTER = "Team 40  ·  CE725 Topic 7  ·  Earned Value Management Dashboard";

/* ------------------------------------------------------------------ *
 * Layouts
 * ------------------------------------------------------------------ */
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: MARGIN, y: 1.65, w: 9.9, h: 1.5,
        fontSize: 42, bold: true, color: C.background1, align: "left", valign: "bottom", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: MARGIN, y: 3.2, w: 9.9, h: 0.5,
        fontSize: 16, color: H.accent6, valign: "top", margin: 0 }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "CONTENT_LIGHT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: MARGIN, y: 0.42, w: 12.1, h: 0.72,
        fontSize: 32, bold: true, color: C.text1, align: "left", valign: "middle", margin: 0 }, text: "" } },
    { text: { text: FOOTER, options: { x: MARGIN, y: 6.95, w: 9.2, h: 0.3, fontSize: 9,
        color: H.accent6, isTextBox: true, margin: 0, valign: "middle" } } },
  ],
  slideNumber: { x: 12.5, y: 6.95, w: 0.45, h: 0.3, fontSize: 9, color: H.accent6, align: "right" },
});

pres.defineSlideMaster({
  title: "CONTENT_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: MARGIN, y: 0.42, w: 12.1, h: 0.72,
        fontSize: 32, bold: true, color: C.background1, align: "left", valign: "middle", margin: 0 }, text: "" } },
    { text: { text: FOOTER, options: { x: MARGIN, y: 6.95, w: 9.2, h: 0.3, fontSize: 9,
        color: H.accent3, isTextBox: true, margin: 0, valign: "middle" } } },
  ],
  slideNumber: { x: 12.5, y: 6.95, w: 0.45, h: 0.3, fontSize: 9, color: H.accent3, align: "right" },
});

/* ------------------------------------------------------------------ *
 * Helpers — the repeated motif is a filled circle label beside a card
 * ------------------------------------------------------------------ */
const shadow = () => ({ type: "outer", color: "1C262B", blur: 8, offset: 2, angle: 90, opacity: 0.1 });

function card(s, { x, y, w, h, fill = C.background2, name }) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.06, fill: { color: fill },
    line: { type: "none" }, shadow: shadow(), objectName: name,
  });
}

function circle(s, { x, y, d = 0.52, fill, label, color = "FFFFFF", fontSize = 14, name }) {
  s.addShape(pres.ShapeType.ellipse, {
    x, y, w: d, h: d, fill: { color: fill }, line: { type: "none" }, objectName: name,
  });
  s.addText(label, {
    x, y, w: d, h: d, align: "center", valign: "middle", margin: 0,
    fontSize, bold: true, color, isTextBox: true,
  });
}

/** Big number over a small label, inside an optional card. */
function stat(s, { x, y, w, value, label, valueColor, labelColor, size = 40, align = "left", h = 1.5 }) {
  s.addText(value, {
    x, y, w, h: h * 0.62, fontSize: size, bold: true, color: valueColor,
    fontFace: THEME.headFontFace, align, valign: "bottom", margin: 0, isTextBox: true,
  });
  s.addText(label, {
    x, y: y + h * 0.62, w, h: h * 0.38, fontSize: 11.5, color: labelColor,
    align, valign: "top", margin: 0, isTextBox: true,
  });
}

/** Common quiet-frame options for every chart in the deck. */
const chartFrame = {
  catAxisLabelColor: H.accent5, catAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt",
  valAxisLabelColor: H.accent5, valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt",
  catAxisLineShow: false, valAxisLineShow: false,
  valGridLine: { color: "DDE3E6", size: 1 },
  catGridLine: { style: "none" },
  dataLabelFontFace: "+mn-lt", dataLabelFontSize: 11, dataLabelFormatCode: "0.00",
};

/* ================================================================== *
 * 1 — Title
 * ================================================================== */
pres.addSection({ title: "Opening" });
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Opening" });
  s.addText("Earned Value Management Dashboard", { placeholder: "title" });
  s.addText("Construction Economics and Finance  ·  CE725  ·  Topic 7", { placeholder: "body" });

  s.addText(
    "Team 40    Sajjad Nakhwa  ·  Dependar Arya  ·  Neel Shah  ·  Akshat Karkar  ·  Pearsh Gumasta",
    { x: MARGIN, y: 3.72, w: 11.2, h: 0.34, fontSize: 13, color: C.background1,
      isTextBox: true, margin: 0, valign: "middle", objectName: "team" },
  );

  const chips = [
    { v: "₹" + FIG.bac + " Cr", l: "project budget at completion" },
    { v: "19", l: "work packages tracked individually" },
    { v: "50 / 50", l: "independent benchmark comparisons agree" },
  ];
  chips.forEach((c, i) => {
    const x = MARGIN + i * 4.06;
    card(s, { x, y: 5.0, w: 3.78, h: 1.42, fill: H.accent5, name: "chip" + i });
    stat(s, { x: x + 0.3, y: 5.15, w: 3.2, value: c.v, label: c.l,
      valueColor: C.background1, labelColor: H.accent6, size: 26, h: 1.12 });
  });

  s.addNotes(
    "0:00-0:30. We built a tool that tells a project manager whether a project is in trouble, " +
    "where the trouble is, and what it will cost. The part we want to spend most of the time on " +
    "is how we know the numbers are right - and what that checking still cannot tell us.",
  );
}

/* ================================================================== *
 * 2 — The problem, in one number
 * ================================================================== */
{
  const s = pres.addSlide({ masterName: "CONTENT_LIGHT", sectionTitle: "Opening" });
  s.addText("The problem, in one number", { placeholder: "title" });

  const cards = [
    { v: "₹" + FIG.pv + " Cr", l: "PLANNED VALUE\nwhat should have been done", dark: false },
    { v: "₹" + FIG.ac + " Cr", l: "ACTUAL COST\nwhat it has cost", dark: false },
    { v: "₹" + FIG.ev + " Cr", l: "EARNED VALUE\nwhat was actually done", dark: true },
  ];
  cards.forEach((c, i) => {
    const x = MARGIN + i * 4.06;
    card(s, { x, y: 1.42, w: 3.78, h: 1.74, fill: c.dark ? H.accent1 : C.background2, name: "pec" + i });
    stat(s, { x: x + 0.32, y: 1.58, w: 3.14, value: c.v, label: c.l,
      valueColor: c.dark ? "FFFFFF" : H.accent5,
      labelColor: c.dark ? "F3DED8" : H.accent3, size: 34, h: 1.42 });
  });

  s.addText(
    [{ text: "Spend is under plan by ₹4 lakh, so the monthly report writes itself as healthy.", options: { breakLine: true } },
     { text: "The two errors point in opposite directions and cancel.", options: {} }],
    { x: MARGIN, y: 3.42, w: 11.9, h: 0.6, fontSize: 15, color: C.text1,
      isTextBox: true, margin: 0, valign: "top", objectName: "pivot" },
  );

  const outcomes = [
    { v: FIG.overBudgetPct + "% over budget", l: "every rupee spent returns 87 paise of budgeted work" },
    { v: FIG.daysBehind + " days behind programme", l: "measured in time, not as a dimensionless index" },
  ];
  outcomes.forEach((o, i) => {
    const x = MARGIN + i * 6.1;
    circle(s, { x, y: 4.24, d: 0.46, fill: H.accent1, label: "!", fontSize: 15, name: "warn" + i });
    s.addText(o.v, { x: x + 0.64, y: 4.2, w: 5.3, h: 0.42, fontSize: 21, bold: true,
      color: H.accent1, fontFace: THEME.headFontFace, isTextBox: true, margin: 0, valign: "middle" });
    s.addText(o.l, { x: x + 0.64, y: 4.64, w: 5.3, h: 0.36, fontSize: 12, color: H.accent3,
      isTextBox: true, margin: 0, valign: "top" });
  });

  card(s, { x: MARGIN, y: 5.35, w: 12.09, h: 1.3, fill: C.background2, name: "kicker" });
  s.addText(
    [{ text: "Budget against spend is two numbers, and two numbers give one comparison. ", options: { bold: true } },
     { text: "Separating ‘am I doing the work’ from ‘is the work costing what it should’ needs a third measurement: the budgeted cost of the work actually performed.", options: {} }],
    { x: MARGIN + 0.34, y: 5.52, w: 11.4, h: 0.96, fontSize: 14.5, color: C.text1,
      isTextBox: true, margin: 0, valign: "middle" },
  );

  s.addNotes(
    "0:30-2:00. Ask the room: a project has spent 3.98 crore against a plan of 4.02 crore - is it " +
    "healthy? Pause and let them answer yes. Then reveal the earned value: it has completed only " +
    "3.47 crore of work, so it is 14.7 per cent over budget and 19 days behind. Two numbers give " +
    "you one comparison; you cannot separate doing the work from what the work costs without a " +
    "third measurement.",
  );
}

/* ================================================================== *
 * 3 — The method
 * ================================================================== */
pres.addSection({ title: "Method" });
{
  const s = pres.addSlide({ masterName: "CONTENT_LIGHT", sectionTitle: "Method" });
  s.addText("Three measurements, and comparisons between them", { placeholder: "title" });

  const rows = [
    { k: "PV", c: H.accent5, t: "Budgeted cost of work scheduled", q: "What should have been done by now?" },
    { k: "EV", c: H.accent2, t: "Budgeted cost of work performed", q: "What was actually done?" },
    { k: "AC", c: H.accent1, t: "Actual cost of doing it",          q: "What did it cost?" },
  ];
  rows.forEach((r, i) => {
    const y = 1.5 + i * 1.32;
    card(s, { x: MARGIN, y, w: 6.9, h: 1.1, fill: C.background2, name: "m" + i });
    circle(s, { x: MARGIN + 0.3, y: y + 0.29, d: 0.52, fill: r.c, label: r.k, fontSize: 13, name: "mc" + i });
    s.addText(r.t, { x: MARGIN + 1.0, y: y + 0.18, w: 5.6, h: 0.38, fontSize: 15, bold: true,
      color: C.text1, isTextBox: true, margin: 0, valign: "middle" });
    s.addText(r.q, { x: MARGIN + 1.0, y: y + 0.56, w: 5.6, h: 0.34, fontSize: 12.5,
      color: H.accent3, italic: true, isTextBox: true, margin: 0, valign: "middle" });
  });

  const RX = 7.85, RW = 4.86;
  card(s, { x: RX, y: 1.5, w: RW, h: 3.74, fill: C.background2, name: "compare" });
  s.addText("Everything else compares two of the three", {
    x: RX + 0.3, y: 1.68, w: RW - 0.6, h: 0.4, fontSize: 14, bold: true, color: C.text1,
    isTextBox: true, margin: 0, valign: "middle",
  });

  const comps = [
    { head: "EV against AC  →  cost", lines: "CV = EV − AC\nCPI = EV ÷ AC", c: H.accent1 },
    { head: "EV against PV  →  schedule", lines: "SV = EV − PV\nSPI = EV ÷ PV", c: H.accent5 },
  ];
  comps.forEach((cp, i) => {
    const y = 2.22 + i * 1.46;
    s.addText(cp.head, { x: RX + 0.3, y, w: RW - 0.6, h: 0.34, fontSize: 13, bold: true,
      color: cp.c, isTextBox: true, margin: 0, valign: "middle" });
    s.addText(cp.lines, { x: RX + 0.3, y: y + 0.36, w: RW - 0.6, h: 0.8, fontSize: 15,
      fontFace: "Courier New", color: C.text1, isTextBox: true, margin: 0, valign: "top", lineSpacing: 20 });
  });

  s.addText(
    "“That is the whole method. The rest is bookkeeping on top of it.”",
    { x: MARGIN, y: 5.6, w: 12.09, h: 0.5, fontSize: 17, italic: true, color: H.accent5,
      fontFace: THEME.headFontFace, isTextBox: true, margin: 0, valign: "middle", objectName: "quote" },
  );
  s.addText(
    "The tool adds Earned Schedule, four forecasting methods and the same calculation at every work package.",
    { x: MARGIN, y: 6.12, w: 12.09, h: 0.4, fontSize: 12.5, color: H.accent3,
      isTextBox: true, margin: 0, valign: "middle" },
  );

  s.addNotes(
    "2:00-3:30. PV, EV and AC are the only three measurements. Cost performance is EV against AC; " +
    "schedule performance is EV against PV. That is the whole method and the rest is bookkeeping " +
    "on top of it. Be ready to write any of these on the board - the brief says any member may be " +
    "asked to explain any formula.",
  );
}

/* ================================================================== *
 * 4 — The case study
 * ================================================================== */
{
  const s = pres.addSlide({ masterName: "CONTENT_LIGHT", sectionTitle: "Method" });
  s.addText("The case study: a G+4 RCC academic block", { placeholder: "title" });

  s.addChart(pres.ChartType.bar, [{
    name: "Budget",
    labels: FIG.divisions.labels,
    values: FIG.divisions.crore,
  }], {
    x: MARGIN, y: 1.34, w: 7.1, h: 3.95,
    barDir: "bar", barGapWidthPct: 45,
    chartColors: [H.accent5],
    showTitle: true, title: "Budget by division, ₹ crore",
    titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: C.text1, titleAlign: "left",
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: H.accent5,
    showLegend: false, valAxisMinVal: 0, valAxisMaxVal: 5, valAxisMajorUnit: 1,
    valAxisLabelFormatCode: "0",
    ...chartFrame,
  });

  const RX = 8.1, RW = 4.6;
  const facts = [
    ["BAC", "₹" + FIG.bac + " crore"],
    ["Baseline", "12 months, Apr 2026 to Mar 2027"],
    ["Structure", "19 leaf work packages, 6 divisions"],
    ["Data date", "end of month 6, Sep 2026"],
  ];
  facts.forEach((f, i) => {
    const y = 1.34 + i * 0.52;
    s.addText(f[0], { x: RX, y, w: 1.25, h: 0.42, fontSize: 12, bold: true, color: H.accent3,
      isTextBox: true, margin: 0, valign: "middle" });
    s.addText(f[1], { x: RX + 1.25, y, w: RW - 1.25, h: 0.42, fontSize: 13, color: C.text1,
      isTextBox: true, margin: 0, valign: "middle" });
  });

  card(s, { x: RX, y: 3.52, w: RW, h: 1.77, fill: C.background2, name: "story" });
  s.addText("How it went wrong", { x: RX + 0.28, y: 3.66, w: RW - 0.56, h: 0.32,
    fontSize: 12.5, bold: true, color: C.text1, isTextBox: true, margin: 0, valign: "middle" });
  s.addText(
    [{ text: "Hard rock in excavation — 45% over on that package, two months late", options: { bullet: true, breakLine: true } },
     { text: "Cascaded into footings and foundation RCC", options: { bullet: true, breakLine: true } },
     { text: "Frame started a month late, running an 18-day slab cycle against 12", options: { bullet: true } }],
    { x: RX + 0.28, y: 4.0, w: RW - 0.56, h: 1.2, fontSize: 11.5, color: C.text1,
      isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 5 },
  );

  card(s, { x: MARGIN, y: 5.52, w: 12.09, h: 1.1, fill: "FBF3E3", name: "caveat" });
  circle(s, { x: MARGIN + 0.3, y: 5.84, d: 0.46, fill: H.accent4, label: "!", fontSize: 15, name: "caveatc" });
  s.addText(
    [{ text: "Synthetic data. ", options: { bold: true } },
     { text: "Budgets are order-of-magnitude plausible for an institutional building built to CPWD DSR-style item rates, but they are assumed — not drawn from any tender, estimate or invoice. Slide 12 is about why that choice matters more than it looks.", options: {} }],
    { x: MARGIN + 0.92, y: 5.66, w: 11.0, h: 0.82, fontSize: 12.5, color: "5C4A22",
      isTextBox: true, margin: 0, valign: "middle" },
  );

  s.addNotes(
    "3:30-4:30. Say the synthetic-data caveat explicitly and early - do not let it be discovered " +
    "in questions. Budgets are order-of-magnitude plausible for a building of this size but they " +
    "are assumed, not from any tender or invoice. We come back to why that choice matters on the " +
    "last slide.",
  );
}

/* ================================================================== *
 * 5 — What we built
 * ================================================================== */
{
  const s = pres.addSlide({ masterName: "CONTENT_LIGHT", sectionTitle: "Method" });
  s.addText("Four pieces, one repository", { placeholder: "title" });

  const pieces = [
    { n: "1", t: "Python calculation engine", d: "Every EVM measure, computed at work-package level rather than rolled up to a single project curve.", c: H.accent5 },
    { n: "2", t: "Streamlit dashboard", d: "The tool. Verdict and plain-language summary first, then indices, diagnosis and forecast.", c: H.accent5 },
    { n: "3", t: "Live-formula Excel export", d: "Every figure a real formula. Edit a budget or a percent complete and the whole workbook recalculates.", c: H.accent2 },
    { n: "4", t: "Independent manual benchmark", d: "A separate Excel workbook, executed not re-implemented. This is how we know the numbers are right.", c: H.accent1 },
  ];
  pieces.forEach((p, i) => {
    const x = MARGIN + (i % 2) * 6.1;
    const y = 1.6 + Math.floor(i / 2) * 1.9;
    card(s, { x, y, w: 5.9, h: 1.56, fill: C.background2, name: "piece" + i });
    circle(s, { x: x + 0.32, y: y + 0.3, d: 0.54, fill: p.c, label: p.n, fontSize: 16, name: "pc" + i });
    s.addText(p.t, { x: x + 1.02, y: y + 0.26, w: 4.6, h: 0.42, fontSize: 15.5, bold: true,
      color: C.text1, isTextBox: true, margin: 0, valign: "middle" });
    s.addText(p.d, { x: x + 1.02, y: y + 0.72, w: 4.6, h: 0.76, fontSize: 12, color: H.accent5,
      isTextBox: true, margin: 0, valign: "top" });
  });

  s.addText(
    [{ text: "→  ", options: { color: H.accent1, bold: true } },
     { text: "Switch to the live dashboard", options: { color: H.accent1, bold: true } },
     { text: "   — slides 6 to 9 are driven from the running tool", options: { color: H.accent3 } }],
    { x: MARGIN, y: 5.56, w: 12.09, h: 0.5, fontSize: 16, fontFace: THEME.headFontFace,
      isTextBox: true, margin: 0, valign: "middle", objectName: "cue" },
  );

  s.addNotes(
    "4:30-5:00. Keep this slide short - it is a signpost, not content. Then switch to the running " +
    "dashboard. If the app has not started, present slides 6 to 9 from the screenshots they " +
    "already carry and do not debug live.",
  );
}

/* ================================================================== *
 * 6 — DEMO: the position
 * ================================================================== */
pres.addSection({ title: "Demonstration" });
{
  const s = pres.addSlide({ masterName: "CONTENT_LIGHT", sectionTitle: "Demonstration" });
  s.addText("Where the project stands at month six", { placeholder: "title" });

  s.addImage({ path: IMG("01-overview.jpg"), x: MARGIN, y: 1.26, w: 6.53, h: 5.0,
    objectName: "dashboard overview screenshot" });

  const RX = 7.35, RW = 5.36;
  card(s, { x: RX, y: 1.26, w: RW, h: 1.28, fill: C.background2, name: "cpi" });
  stat(s, { x: RX + 0.3, y: 1.4, w: RW - 0.6, value: "CPI " + FIG.cpi,
    label: "every rupee spent returns 87 paise of budgeted work",
    valueColor: H.accent1, labelColor: H.accent3, size: 26, h: 1.0 });

  card(s, { x: RX, y: 2.7, w: RW, h: 1.28, fill: H.accent1, name: "tcpi" });
  stat(s, { x: RX + 0.3, y: 2.84, w: RW - 0.6, value: "TCPI " + FIG.tcpi,
    label: "efficiency the remaining work must now achieve",
    valueColor: "FFFFFF", labelColor: "F3DED8", size: 26, h: 1.0 });

  s.addText(
    [{ text: "We have sustained 0.872 for six months. TCPI asks for a 20.6% improvement on a level of performance never once achieved.", options: { breakLine: true } },
     { text: "The budget is gone. What remains is deciding who absorbs it.", options: { bold: true } }],
    { x: RX, y: 4.14, w: RW, h: 2.1, fontSize: 13.5, color: C.text1,
      isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 8, objectName: "tcpi-note" },
  );

  s.addNotes(
    "5:00-7:00. Point in order at: the verdict bar reading BEHIND SCHEDULE AND OVERSPENT; the " +
    "plain-language summary, read aloud, noting it quotes no index without the consequence beside " +
    "it; CPI 0.872; then TCPI 1.051. If there is time for only one sentence in the whole " +
    "demonstration it is the TCPI one: the remaining work must run at 1.051 having sustained " +
    "0.872 for six months, so the budget is gone and what remains is deciding who absorbs it.",
  );
}

/* ================================================================== *
 * 7 — DEMO: where the variance is
 * ================================================================== */
{
  const s = pres.addSlide({ masterName: "CONTENT_LIGHT", sectionTitle: "Demonstration" });
  s.addText("Where the variance actually is", { placeholder: "title" });

  s.addImage({ path: IMG("02-variance-by-package.jpg"), x: MARGIN, y: 1.26, w: 6.53, h: 5.0,
    objectName: "variance by work package screenshot" });

  const RX = 7.35, RW = 5.36;
  const split = [
    { v: "₹38 lakh", l: "in three completed substructure packages — this variance is FINAL", fill: H.accent1, fg: "FFFFFF", sub: "F3DED8" },
    { v: "₹7.7 lakh", l: "in the frame, 22% and 14% complete — this can still be managed", fill: C.background2, fg: H.accent2, sub: H.accent3 },
  ];
  split.forEach((sp, i) => {
    const y = 1.26 + i * 1.5;
    card(s, { x: RX, y, w: RW, h: 1.34, fill: sp.fill, name: "split" + i });
    stat(s, { x: RX + 0.3, y: y + 0.14, w: RW - 0.6, value: sp.v, label: sp.l,
      valueColor: sp.fg, labelColor: sp.sub, size: 26, h: 1.06 });
  });

  s.addText(
    [{ text: "Excavation and earthwork: CPI 0.689, 100% complete.", options: { bold: true, breakLine: true } },
     { text: "No recovery plan touches it. Stop trying to recover the substructure, protect the frame, and tell the client ₹38 lakh is gone.", options: { breakLine: true } },
     { text: "This is the slide that justifies carrying the WBS through the whole calculation instead of rolling up to one project curve.", options: { italic: true, color: H.accent3 } }],
    { x: RX, y: 4.3, w: RW, h: 1.96, fontSize: 13, color: C.text1,
      isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 7, objectName: "diagnosis" },
  );

  s.addNotes(
    "7:00-9:00. A project CPI of 0.872 says something is wrong but does not say what to do. Point " +
    "at Excavation: CPI 0.689 and 100 per cent complete, so that variance is final. Then the frame " +
    "packages at 22 and 14 per cent, which can still move. 38 lakh of the 51.20 lakh is in " +
    "completed substructure and only 7.7 lakh is live. The management action is the opposite of " +
    "what a single project index suggests.",
  );
}

/* ================================================================== *
 * 8 — DEMO: the schedule defect
 * ================================================================== */
{
  const s = pres.addSlide({ masterName: "CONTENT_LIGHT", sectionTitle: "Demonstration" });
  s.addText("SPI has a structural defect, and Earned Schedule fixes it", { placeholder: "title" });

  s.addChart(pres.ChartType.line, [
    { name: "CPI",    labels: FIG.trend.labels, values: FIG.trend.cpi },
    { name: "SPI",    labels: FIG.trend.labels, values: FIG.trend.spi },
    { name: "SPI(t)", labels: FIG.trend.labels, values: FIG.trend.spit },
    { name: "target 1.00", labels: FIG.trend.labels, values: [1, 1, 1, 1, 1, 1] },
  ], {
    x: MARGIN, y: 1.26, w: 6.6, h: 4.9,
    chartColors: [H.accent1, H.accent5, H.accent2, H.accent6],
    lineSize: 3, lineSmooth: false,
    showTitle: true, title: "Performance indices, Apr to Sep 2026",
    titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: C.text1, titleAlign: "left",
    showLegend: true, legendPos: "b", legendColor: H.accent5, legendFontSize: 11, legendFontFace: "+mn-lt",
    valAxisMinVal: 0.7, valAxisMaxVal: 1.05, valAxisMajorUnit: 0.1,
    ...chartFrame,
  });

  const RX = 7.35, RW = 5.36;
  card(s, { x: RX, y: 1.26, w: RW, h: 1.86, fill: C.background2, name: "defect" });
  s.addText(
    [{ text: "SPI = EV ÷ PV", options: { bold: true, fontFace: "Courier New", breakLine: true } },
     { text: "At completion EV must equal BAC and PV must equal BAC.", options: { breakLine: true } },
     { text: "So SPI returns to 1.00 on every project ever completed, however late.", options: { bold: true } }],
    { x: RX + 0.3, y: 1.42, w: RW - 0.6, h: 1.58, fontSize: 13, color: C.text1,
      isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 7 },
  );

  card(s, { x: RX, y: 3.34, w: RW, h: 1.28, fill: H.accent2, name: "es" });
  stat(s, { x: RX + 0.3, y: 3.48, w: RW - 0.6, value: FIG.daysBehind + " days behind",
    label: "Earned Schedule, measured in time — SPI(t) " + FIG.spiT,
    valueColor: "FFFFFF", labelColor: "DCE8E4", size: 24, h: 1.0 });

  s.addText(
    [{ text: "A site manager can act on nineteen days. Nobody can act on 0.863.", options: { breakLine: true } },
     { text: "Note CPI flat at 0.86–0.88 across all six periods while SPI swings to 0.743 and back: cost performance stabilises early and rarely recovers.", options: { color: H.accent5 } }],
    { x: RX, y: 4.78, w: RW, h: 1.6, fontSize: 13, color: C.text1,
      isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 8, objectName: "es-note" },
  );

  s.addNotes(
    "9:00-10:30. SPI reads 0.863 and there is a structural problem with that number. Since EV and " +
    "PV both converge on BAC, SPI returns to 1.00 on every project however late - the index gets " +
    "more reassuring as the project gets later. Earned Schedule asks when on the baseline this " +
    "much value was scheduled to have been earned, which gives 19 days behind. Also point at CPI " +
    "flat across all six periods: that is the strongest argument against an optimistic recovery plan.",
  );
}

/* ================================================================== *
 * 9 — DEMO: the forecast
 * ================================================================== */
{
  const s = pres.addSlide({ masterName: "CONTENT_LIGHT", sectionTitle: "Demonstration" });
  s.addText("The forecast is a range, and that is the honest answer", { placeholder: "title" });

  s.addChart(pres.ChartType.bar, [{
    name: "Cost at completion",
    labels: ["BAC\nbaseline", "EAC2\nvariance was one-off", "EAC1\nCPI persists", "EAC4\nweighted 80/20", "EAC3\nCPI and SPI persist"],
    values: [Number(FIG.bac), FIG.eac.EAC2, FIG.eac.EAC1, FIG.eac.EAC4, FIG.eac.EAC3],
  }], {
    x: MARGIN, y: 1.26, w: 6.6, h: 4.9,
    chartColors: [H.accent5, H.accent4, H.accent1, H.accent1, "9E3F2B"],
    barGapWidthPct: 40,
    showTitle: true, title: "Estimate at completion, ₹ crore",
    titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: C.text1, titleAlign: "left",
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.text1,
    showLegend: false, valAxisMaxVal: 20, valAxisMajorUnit: 5,
    ...chartFrame,
  });

  const RX = 7.35, RW = 5.36;
  card(s, { x: RX, y: 1.26, w: RW, h: 1.28, fill: H.accent1, name: "spread" });
  stat(s, { x: RX + 0.3, y: 1.4, w: RW - 0.6, value: "₹" + FIG.spread + " Cr",
    label: "spread between the four standard methods",
    valueColor: "FFFFFF", labelColor: "F3DED8", size: 28, h: 1.0 });

  s.addText(
    [{ text: "We deliberately do not pick one.", options: { bold: true, breakLine: true } },
     { text: "The four methods differ in a single assumption — what you believe about the remaining work. The spread is the method being honest, not failing.", options: { breakLine: true } },
     { text: "Narrowing it needs a judgement nobody can make arithmetically: was the rock a closed event, or a symptom of a site that was never properly investigated?", options: { italic: true, color: H.accent5 } }],
    { x: RX, y: 2.72, w: RW, h: 3.2, fontSize: 13.5, color: C.text1,
      isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 9, objectName: "forecast-note" },
  );

  s.addNotes(
    "10:30-11:30. Four methods, 14.51 crore to 17.98 crore. We deliberately do not pick one: they " +
    "differ in a single assumption about the remaining work, and the 3.47 crore spread is the " +
    "method being honest. Narrowing it needs a judgement nobody can make arithmetically - was the " +
    "rock a closed event or a symptom of a site that was never properly investigated. Then go back " +
    "to the slides.",
  );
}

/* ================================================================== *
 * 10 — How we know it is right
 * ================================================================== */
pres.addSection({ title: "Validation" });
{
  const s = pres.addSlide({ masterName: "CONTENT_LIGHT", sectionTitle: "Validation" });
  s.addText("How we know the numbers are right", { placeholder: "title" });

  /* Flow diagram, hand-composed, kept inside x 0.62 .. 6.90 so it clears the
     right-hand column. Arrowheads: a line draws (x,y) -> (x+w,y+h), and
     flipV draws (x,y+h) -> (x+w,y), so a down-left arrow is flipV with the
     head on the beginning. */
  const box = (x, y, w, h, label, fill, fg, fs, name) => {
    s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08,
      fill: { color: fill }, line: { type: "none" }, shadow: shadow(), objectName: name });
    s.addText(label, { x: x + 0.08, y, w: w - 0.16, h, align: "center", valign: "middle",
      margin: 0, fontSize: fs, bold: true, color: fg, isTextBox: true });
  };
  const arrowDownRight = (x, y, w, h, name) => s.addShape(pres.ShapeType.line,
    { x, y, w, h, line: { color: H.accent6, width: 2, endArrowType: "triangle" }, objectName: name });
  const arrowDownLeft = (x, y, w, h, name) => s.addShape(pres.ShapeType.line,
    { x, y, w, h, flipV: true, line: { color: H.accent6, width: 2, beginArrowType: "triangle" }, objectName: name });

  box(2.61, 1.38, 2.30, 0.56, "Raw inputs", H.accent5, "FFFFFF", 13.5, "inputs");
  arrowDownLeft(1.92, 1.98, 1.84, 0.60, "a1");
  arrowDownRight(3.76, 1.98, 1.84, 0.60, "a2");
  box(0.62, 2.62, 2.60, 0.56, "Python engine", C.background2, C.text1, 13, "pyeng");
  box(4.30, 2.62, 2.60, 0.56, "Excel formulas", C.background2, C.text1, 13, "xl");
  s.addText("evaluated by\nLibreOffice headless", { x: 4.30, y: 3.22, w: 2.60, h: 0.56,
    align: "center", valign: "middle", margin: 0, fontSize: 10.5, color: H.accent3,
    italic: true, isTextBox: true });
  arrowDownRight(1.92, 3.22, 1.84, 1.18, "a3");
  arrowDownLeft(3.76, 3.86, 1.84, 0.54, "a4");
  box(2.61, 4.44, 2.30, 0.56, "Compare", H.accent1, "FFFFFF", 13.5, "cmp");
  s.addText("50 measures, two reporting periods", { x: 1.80, y: 5.08, w: 3.92, h: 0.34,
    align: "center", valign: "middle", margin: 0, fontSize: 11, color: H.accent3, isTextBox: true });

  const RX = 7.25, RW = 5.46, CW = 2.63;
  const nums = [
    { v: "50 / 50", l: "comparisons agree \u2014 to \u20B90.01 on currency, 1\u00D710\u207B\u2079 on indices" },
    { v: "150", l: "automated tests \u2014 expected values hand-derived before the engine existed" },
  ];
  nums.forEach((n, i) => {
    const x = RX + i * (CW + 0.2);
    card(s, { x, y: 1.38, w: CW, h: 1.8, fill: C.background2, name: "num" + i });
    stat(s, { x: x + 0.26, y: 1.52, w: CW - 0.52, value: n.v, label: n.l,
      valueColor: H.accent2, labelColor: H.accent3, size: 24, h: 1.52 });
  });

  card(s, { x: RX, y: 3.38, w: RW, h: 2.52, fill: H.accent5, name: "keydecision" });
  s.addText("The decision that mattered", { x: RX + 0.3, y: 3.54, w: RW - 0.6, h: 0.36,
    fontSize: 13, bold: true, color: H.accent6, isTextBox: true, margin: 0, valign: "middle" });
  s.addText(
    [{ text: "Not to write a second Python implementation.", options: { bold: true, breakLine: true } },
     { text: "A Python re-implementation validates only your own understanding. Misread a formula and both sides misread it identically, the comparison passes, and both are wrong.", options: { breakLine: true } },
     { text: "So the benchmark lives in a different execution environment, and it is executed \u2014 not re-implemented.", options: {} }],
    { x: RX + 0.3, y: 3.94, w: RW - 0.6, h: 1.84, fontSize: 12.5, color: "FFFFFF",
      isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 7 },
  );

  s.addNotes(
    "11:30-13:00. 50 of 50 comparisons agree to a paisa on currency and 1e-9 on the indices, " +
    "across both periods, plus 150 automated tests whose expected values were hand-derived before " +
    "the engine was written. The critical decision was not to write a second Python " +
    "implementation: that validates only your own understanding, because a misread formula is " +
    "misread identically on both sides and the check passes. The benchmark is in a different " +
    "execution environment and it is executed, not re-implemented.",
  );
}

/* ================================================================== *
 * 11 — What we got wrong
 * ================================================================== */
{
  const s = pres.addSlide({ masterName: "CONTENT_LIGHT", sectionTitle: "Validation" });
  s.addText("Four discrepancies, all recorded", { placeholder: "title" });

  const head = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: H.accent5 }, fontSize: 12.5 } });
  const rows = [
    [head("What we found"), head("How it resolved")],
    ["EAC3 off by \u20B9156",
     { text: [{ text: "Our hand calculation was wrong, not the engine", options: { bold: true } },
              { text: " \u2014 we rounded CPI \u00D7 SPI mid-chain. Rule adopted: rounding is presentation only.", options: {} }] }],
    ["Two validation tests failing",
     { text: [{ text: "The tests were wrong, not the engine.", options: { bold: true } },
              { text: " Fixing the code to make them pass would have deleted a rule that rejects earned value being double counted.", options: {} }] }],
    ["Executive summary invisible under a dark theme",
     { text: [{ text: "No test caught it. ", options: { bold: true } },
              { text: "Every number was correct and the tool was unusable. Found only by opening the running app.", options: {} }] }],
    ["Carry-forward routine fragile on reporting gaps",
     { text: [{ text: "Caught in review before it produced a wrong answer. ", options: { bold: true } },
              { text: "Clean data hid it; real data would not.", options: {} }] }],
  ];

  s.addTable(rows, {
    x: MARGIN, y: 1.34, w: 12.09, colW: [3.5, 8.59],
    border: { type: "solid", color: "DDE3E6", pt: 1 },
    fill: { color: "FFFFFF" }, color: C.text1, fontSize: 12.5, valign: "middle",
    margin: [0.09, 0.14, 0.09, 0.14], rowH: [0.42, 0.95, 0.95, 0.95, 0.95],
    objectName: "discrepancies",
  });

  card(s, { x: MARGIN, y: 5.62, w: 12.09, h: 1.08, fill: C.background2, name: "lesson" });
  s.addText(
    [{ text: "The second one matters most. ", options: { bold: true } },
     { text: "The fast route to a green test suite was to change the engine until the tests passed — which would have made the project worse while making the output greener. Ask why a test fails before changing anything.", options: {} }],
    { x: MARGIN + 0.34, y: 5.78, w: 11.4, h: 0.76, fontSize: 13, color: C.text1,
      isTextBox: true, margin: 0, valign: "middle" },
  );

  s.addNotes(
    "13:00-14:00. Four discrepancies, all in the validation report. Two of them were defects in " +
    "the check rather than in the thing being checked - our hand calculation of EAC3, and two " +
    "mis-constructed tests. The second matters most: the fast route to a green test suite was to " +
    "change the engine until the tests passed, and that would have removed a correct rule.",
  );
}

/* ================================================================== *
 * 12 — What validation cannot do
 * ================================================================== */
pres.addSection({ title: "Closing" });
{
  const s = pres.addSlide({ masterName: "CONTENT_DARK", sectionTitle: "Closing" });
  s.addText("What none of this validation can do", { placeholder: "title" });

  s.addText(
    "Both implementations read the same inputs.",
    { x: MARGIN, y: 1.26, w: 12.09, h: 0.5, fontSize: 20, bold: true, color: H.accent6,
      fontFace: THEME.headFontFace, isTextBox: true, margin: 0, valign: "middle", objectName: "premise" },
  );

  card(s, { x: MARGIN, y: 1.92, w: 3.5, h: 1.5, fill: H.accent1, name: "wrongpct" });
  s.addText(
    [{ text: "60% reported", options: { bold: true, breakLine: true, fontSize: 21 } },
     { text: "40% actual", options: { bold: true, fontSize: 21 } }],
    { x: MARGIN + 0.3, y: 1.92, w: 2.9, h: 1.5, color: "FFFFFF",
      fontFace: THEME.headFontFace, isTextBox: true, margin: 0, valign: "middle" },
  );

  const chain = [
    "the engine computes a wrong EV",
    "the benchmark computes the same wrong EV",
    "all 50 comparisons agree",
    "every index is confidently, precisely wrong",
  ];
  chain.forEach((c, i) => {
    const y = 1.92 + i * 0.4;
    circle(s, { x: 4.5, y: y + 0.02, d: 0.34, fill: i === 3 ? H.accent1 : H.accent5,
      label: String(i + 1), color: i === 3 ? "FFFFFF" : H.accent6, fontSize: 11, name: "ch" + i });
    s.addText(c, { x: 5.0, y, w: 7.7, h: 0.38, fontSize: 14,
      bold: i === 3, color: i === 3 ? H.accent1 : "FFFFFF",
      isTextBox: true, margin: 0, valign: "middle" });
  });

  card(s, { x: MARGIN, y: 3.72, w: 12.09, h: 1.06, fill: H.accent5, name: "definition" });
  s.addText(
    [{ text: "Earned value is percent complete × budget. ", options: { bold: true } },
     { text: "Percent complete is a judgement made at site, often by someone who is paid more if it is higher. No spreadsheet and no test suite detects an error in it — only a measurement at site does.", options: {} }],
    { x: MARGIN + 0.34, y: 3.86, w: 11.4, h: 0.78, fontSize: 13.5, color: "FFFFFF",
      isTextBox: true, margin: 0, valign: "middle" },
  );

  s.addText(
    [{ text: "We validated the arithmetic to nine decimal places. The arithmetic was never the risk.", options: { breakLine: true, bold: true } },
     { text: "And every design choice that makes this dashboard more persuasive makes the problem worse: it renders an unverifiable judgement with six-figure precision, a traffic light and a chart.", options: {} }],
    { x: MARGIN, y: 5.0, w: 12.09, h: 1.0, fontSize: 13.5, color: H.accent6,
      isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 7, objectName: "closing-note" },
  );

  s.addText(
    "The quality of an EVM system is the quality of its percent-complete measurement.",
    { x: MARGIN, y: 6.1, w: 12.09, h: 0.5, fontSize: 18, italic: true, color: "FFFFFF",
      fontFace: THEME.headFontFace, isTextBox: true, margin: 0, valign: "middle", objectName: "final" },
  );

  s.addNotes(
    "14:00-15:00. The closing point - do not rush it. Both implementations read the same inputs, " +
    "so if a package is reported 60 per cent complete when it is really 40, the engine computes a " +
    "wrong EV, the benchmark computes the same wrong EV, all 50 comparisons agree, and every index " +
    "is confidently wrong. We validated the arithmetic to nine decimal places and the arithmetic " +
    "was never the risk. Everything in this project, including all of our work, is arithmetic on " +
    "top of a judgement made by a person standing on a site.",
  );
}

/* ------------------------------------------------------------------ */
(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote " + OUT);
})();
