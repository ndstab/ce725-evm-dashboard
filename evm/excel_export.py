"""Export a live-formula EVM workbook.

The dashboard is the better place to interrogate a project, but a site
quantity surveyor, a client's project manager and a lender's engineer all
live in Excel. A report they cannot open, edit and email is a report they
will retype, and retyping is where errors enter. So the tool exports a
workbook in which every EVM figure is a LIVE FORMULA, not a pasted value:
change a budget or a percent complete on the Inputs sheet and the indices,
the forecasts and the charts all move.

This is a FEATURE of the tool. It is not the manual benchmark. The
benchmark in benchmark/ is built separately and deliberately so, because a
workbook the tool generated cannot be an independent check on the tool.
This export is validated against that benchmark like everything else.

EXCEL CHART DEFAULTS

Writing charts from code is not the same as drawing them. An OOXML element
you never write is not "off", it is "Excel decides", and the default is
often the opposite of what is wanted. Reading the XML back tells you what
you wrote, not what Excel will do with it. Four defaults bite here, and
each is handled explicitly below:

  1. A category axis without <c:auto val="0"/> is promoted to a DATE axis
     when the labels look like dates, laying out a continuous calendar and
     collapsing every bar to a hairline.
  2. <c:invertIfNegative> absent is treated as TRUE, so an all-negative
     series such as cost variance renders as hollow white outlines.
  3. tickLblPos defaults to "nextTo", meaning next to the axis CROSSING.
     On all-negative data that is the top of the plot, so the labels run
     across the chart title.
  4. A formula returning "" is plotted as ZERO, not as a gap. A series
     that should stop at the data date instead dives to the axis.

These were learned from the chart-gotchas notes in
Tahir-yamin/excel-scurve-builder, credited in the method note.
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference, Series
from openpyxl.chart.series import SeriesLabel
from openpyxl.chart.data_source import StrRef
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from .core import metrics_at, variance_by_wbs
from .dataset import Project

RUPEES = "#,##0"
INDEX_FMT = "0.000"
PCT = "0.0%"

HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=10)
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
FORMULA_FILL = PatternFill("solid", fgColor="E2EFDA")
TOTAL_FILL = PatternFill("solid", fgColor="D9D9D9")
TITLE_FONT = Font(bold=True, size=14, color="1F3864")
NOTE_FONT = Font(italic=True, size=9, color="595959")

GOOD_FILL = PatternFill("solid", fgColor="C6EFCE")
WARN_FILL = PatternFill("solid", fgColor="FFEB9C")
BAD_FILL = PatternFill("solid", fgColor="FFC7CE")

THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

FIRST_ROW = 5


def _headers(ws, row, labels, widths=None):
    for col, label in enumerate(labels, start=1):
        c = ws.cell(row=row, column=col, value=label)
        c.fill, c.font = HEADER_FILL, HEADER_FONT
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BOX
    if widths:
        for col, width in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(col)].width = width
    ws.row_dimensions[row].height = 30


def export_workbook(project: Project, destination: str | Path) -> Path:
    """Write a live-formula EVM workbook for the given project."""
    destination = Path(destination)
    leaves = project.leaves.reset_index(drop=True)
    n_leaf = len(leaves)
    n_periods = project.n_periods
    data_date = project.data_date
    last_row = FIRST_ROW + n_leaf - 1

    ac = project.actuals.pivot_table(
        index="wbs_id", columns="period", values="ac_period_inr", aggfunc="sum"
    ).fillna(0.0)
    pct = project.actuals.pivot_table(
        index="wbs_id", columns="period", values="pct_complete_cum", aggfunc="sum"
    ).fillna(0.0)
    pv = project.baseline.pivot_table(
        index="wbs_id", columns="period", values="pv_period_inr", aggfunc="sum"
    ).fillna(0.0)

    wb = Workbook()

    # ======================================================================
    # Inputs
    # ======================================================================
    ws = wb.active
    ws.title = "Inputs"
    ws["A1"] = f"{project.meta.project_name} — EVM Inputs"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = ("Yellow cells are editable. Change any of them and every index, "
                "forecast and chart in this workbook recalculates.")
    ws["A2"].font = NOTE_FONT

    labels = ["WBS ID", "Work Package", "Budget (Rs)"]
    labels += [f"AC P{p}" for p in range(1, data_date + 1)]
    labels += [f"%C P{p}" for p in range(1, data_date + 1)]
    _headers(ws, 4, labels, [10, 42, 14] + [12] * data_date * 2)

    for i, row in leaves.iterrows():
        r = FIRST_ROW + i
        wbs_id = row["wbs_id"]
        ws.cell(row=r, column=1, value=wbs_id).border = BOX
        ws.cell(row=r, column=2, value=row["name"]).border = BOX
        c = ws.cell(row=r, column=3, value=float(row["budget_inr"]))
        c.number_format, c.fill, c.border = RUPEES, INPUT_FILL, BOX
        for p in range(1, data_date + 1):
            c = ws.cell(row=r, column=3 + p, value=float(ac.loc[wbs_id, p]))
            c.number_format, c.fill, c.border = RUPEES, INPUT_FILL, BOX
            c = ws.cell(row=r, column=3 + data_date + p, value=float(pct.loc[wbs_id, p]))
            c.number_format, c.fill, c.border = PCT, INPUT_FILL, BOX

    trow = last_row + 1
    ws.cell(row=trow, column=2, value="TOTAL").font = Font(bold=True)
    for col in [3] + [3 + p for p in range(1, data_date + 1)]:
        letter = get_column_letter(col)
        c = ws.cell(row=trow, column=col,
                    value=f"=SUM({letter}{FIRST_ROW}:{letter}{last_row})")
        c.number_format, c.fill, c.font, c.border = RUPEES, TOTAL_FILL, Font(bold=True), BOX
    ws.freeze_panes = "C5"

    bac_ref = f"Inputs!$C${trow}"

    # ======================================================================
    # Baseline
    # ======================================================================
    ws = wb.create_sheet("Baseline")
    ws["A1"] = "Time-Phased Budget (Planned Value)"
    ws["A1"].font = TITLE_FONT
    _headers(ws, 4, ["WBS ID", "Work Package"] + [f"P{p}" for p in range(1, n_periods + 1)],
             [10, 42] + [12] * n_periods)
    for i, row in leaves.iterrows():
        r = FIRST_ROW + i
        ws.cell(row=r, column=1, value=row["wbs_id"]).border = BOX
        ws.cell(row=r, column=2, value=row["name"]).border = BOX
        for p in range(1, n_periods + 1):
            c = ws.cell(row=r, column=2 + p, value=float(pv.loc[row["wbs_id"], p]))
            c.number_format, c.fill, c.border = RUPEES, INPUT_FILL, BOX
    brow = last_row + 1
    ws.cell(row=brow, column=2, value="TOTAL").font = Font(bold=True)
    for p in range(1, n_periods + 1):
        letter = get_column_letter(2 + p)
        c = ws.cell(row=brow, column=2 + p,
                    value=f"=SUM({letter}{FIRST_ROW}:{letter}{last_row})")
        c.number_format, c.fill, c.font, c.border = RUPEES, TOTAL_FILL, Font(bold=True), BOX
    ws.freeze_panes = "C5"

    # ======================================================================
    # EVM  (one row per period: the S-curve table and the indices)
    # ======================================================================
    ws = wb.create_sheet("EVM")
    ws["A1"] = "Earned Value by Reporting Period"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = (f"Data date: end of Period {data_date}. EV and AC stop there; "
                "beyond it they return NA() so the charts break the line "
                "rather than plotting zero.")
    ws["A2"].font = NOTE_FONT

    _headers(ws, 4,
             ["Period", "Label", "PV cum", "EV cum", "AC cum",
              "CV", "SV", "CPI", "SPI", "% complete", "% spent"],
             [9, 12, 16, 16, 16, 15, 15, 11, 11, 12, 12])

    for p in range(1, n_periods + 1):
        r = FIRST_ROW + p - 1
        pv_col = get_column_letter(2 + p)
        ac_col = get_column_letter(3 + p)
        pct_col = get_column_letter(3 + data_date + p)

        ws.cell(row=r, column=1, value=p).border = BOX
        ws.cell(row=r, column=2, value=project.meta.label(p)).border = BOX

        c = ws.cell(row=r, column=3,
                    value=f"=SUM(Baseline!$C${FIRST_ROW}:{pv_col}${last_row})")
        c.number_format, c.fill, c.border = RUPEES, FORMULA_FILL, BOX

        if p <= data_date:
            # Earned value in a single formula: sum over packages of
            # (budget x percent complete).
            ev = (f"=SUMPRODUCT(Inputs!$C${FIRST_ROW}:$C${last_row},"
                  f"Inputs!{pct_col}${FIRST_ROW}:{pct_col}${last_row})")
            acc = f"=SUM(Inputs!$D${FIRST_ROW}:{ac_col}${last_row})"
        else:
            # Gotcha 4: "" is plotted as zero. NA() is skipped by the chart.
            ev = acc = "=NA()"

        c = ws.cell(row=r, column=4, value=ev)
        c.number_format, c.fill, c.border = RUPEES, FORMULA_FILL, BOX
        c = ws.cell(row=r, column=5, value=acc)
        c.number_format, c.fill, c.border = RUPEES, FORMULA_FILL, BOX

        for col, formula, fmt in (
            (6, f"=IF(ISNA(D{r}),NA(),D{r}-E{r})", RUPEES),
            (7, f"=IF(ISNA(D{r}),NA(),D{r}-C{r})", RUPEES),
            (8, f"=IF(ISNA(D{r}),NA(),IF(E{r}=0,NA(),D{r}/E{r}))", INDEX_FMT),
            (9, f"=IF(ISNA(D{r}),NA(),IF(C{r}=0,NA(),D{r}/C{r}))", INDEX_FMT),
            (10, f"=IF(ISNA(D{r}),NA(),D{r}/{bac_ref})", PCT),
            (11, f"=IF(ISNA(E{r}),NA(),E{r}/{bac_ref})", PCT),
        ):
            c = ws.cell(row=r, column=col, value=formula)
            c.number_format, c.fill, c.border = fmt, FORMULA_FILL, BOX

    evm_last = FIRST_ROW + n_periods - 1
    ws.freeze_panes = "C5"

    # ======================================================================
    # Dashboard
    # ======================================================================
    dash = wb.create_sheet("Dashboard", 0)
    dash["A1"] = project.meta.project_name
    dash["A1"].font = TITLE_FONT
    dash["A2"] = (f"{project.meta.project_code}  |  data date: end of Period "
                  f"{data_date} ({project.meta.label(data_date)})")
    dash["A2"].font = NOTE_FONT
    dash.column_dimensions["A"].width = 4
    dash.column_dimensions["B"].width = 38
    dash.column_dimensions["C"].width = 22
    dash.column_dimensions["D"].width = 46

    d = FIRST_ROW + data_date - 1   # the EVM row for the data date

    rows = [
        ("Position", None, None),
        ("Budget at completion (BAC)", f"={bac_ref}", RUPEES),
        ("Planned value (PV)", f"=EVM!C{d}", RUPEES),
        ("Earned value (EV)", f"=EVM!D{d}", RUPEES),
        ("Actual cost (AC)", f"=EVM!E{d}", RUPEES),
        ("Percent complete", f"=EVM!J{d}", PCT),
        ("Percent spent", f"=EVM!K{d}", PCT),
        ("Variance", None, None),
        ("Cost variance (CV)", f"=EVM!F{d}", RUPEES),
        ("Schedule variance (SV)", f"=EVM!G{d}", RUPEES),
        ("Cost performance index (CPI)", f"=EVM!H{d}", INDEX_FMT),
        ("Schedule performance index (SPI)", f"=EVM!I{d}", INDEX_FMT),
        ("Forecast", None, None),
        ("EAC — performance continues", f"={bac_ref}/EVM!H{d}", RUPEES),
        ("EAC — variance was a one-off", f"=EVM!E{d}+({bac_ref}-EVM!D{d})", RUPEES),
        ("EAC — cost and schedule pressure",
         f"=EVM!E{d}+({bac_ref}-EVM!D{d})/(EVM!H{d}*EVM!I{d})", RUPEES),
        ("ETC (on EAC, performance continues)",
         f"={bac_ref}/EVM!H{d}-EVM!E{d}", RUPEES),
        ("VAC (on EAC, performance continues)",
         f"={bac_ref}-{bac_ref}/EVM!H{d}", RUPEES),
        ("TCPI to finish on budget",
         f"=({bac_ref}-EVM!D{d})/({bac_ref}-EVM!E{d})", INDEX_FMT),
    ]

    explanations = {
        "Cost performance index (CPI)": "Rupees of budgeted work per rupee spent. Below 1.00 is overspending.",
        "Schedule performance index (SPI)": "Work done per unit of work scheduled. Below 1.00 is behind.",
        "EAC — performance continues": "BAC / CPI. The default forecast.",
        "EAC — variance was a one-off": "AC + (BAC - EV). The most optimistic assumption available.",
        "EAC — cost and schedule pressure": "AC + (BAC - EV) / (CPI x SPI). Recovering schedule normally costs money.",
        "TCPI to finish on budget": "Efficiency the REMAINING work must achieve. Compare it with CPI.",
    }

    r = 4
    for label, formula, fmt in rows:
        if formula is None:
            c = dash.cell(row=r, column=2, value=label.upper())
            c.font = Font(bold=True, size=11, color="1F3864")
            r += 2 if label != "Position" else 1
            continue
        dash.cell(row=r, column=2, value=label).border = BOX
        c = dash.cell(row=r, column=3, value=formula)
        c.number_format, c.fill, c.border = fmt, FORMULA_FILL, BOX
        c.font = Font(bold=True, size=11)
        note = explanations.get(label)
        if note:
            n = dash.cell(row=r, column=4, value=note)
            n.font, n.border = NOTE_FONT, BOX
        r += 1

    # Traffic-light verdict. Written as a formula so it tracks edits to the
    # inputs rather than freezing whatever was true at export.
    verdict_row = r + 1
    dash.cell(row=verdict_row, column=2, value="VERDICT").font = Font(
        bold=True, size=11, color="1F3864"
    )
    c = dash.cell(
        row=verdict_row, column=3,
        value=(f'=IF(AND(EVM!H{d}>=0.95,EVM!I{d}>=0.95),"ON TRACK",'
               f'IF(AND(EVM!H{d}<0.95,EVM!I{d}<0.95),"BEHIND SCHEDULE AND OVERSPENT",'
               f'IF(EVM!H{d}<0.95,"OVERSPENT","BEHIND SCHEDULE")))'),
    )
    c.font, c.fill, c.border = Font(bold=True, size=12), BAD_FILL, BOX
    c.alignment = Alignment(horizontal="center")
    dash.cell(row=verdict_row, column=4,
              value="Thresholds: an index within 5% of plan is treated as noise.").font = NOTE_FONT

    # ======================================================================
    # Charts
    # ======================================================================
    labels_ref = Reference(wb["EVM"], min_col=2, min_row=FIRST_ROW, max_row=evm_last)

    # S-curve. PV runs the full baseline; EV and AC stop at the data date
    # because the rows beyond it return NA().
    s_curve = LineChart()
    s_curve.title = "S-Curve — Planned, Earned and Actual"
    s_curve.height, s_curve.width = 10, 26
    s_curve.y_axis.title = "Cumulative value (Rs)"
    s_curve.x_axis.title = "Reporting period"
    # Gotcha 1: without this the date-like labels promote the category axis
    # to a date axis and the layout silently changes.
    s_curve.x_axis.auto = False
    s_curve.x_axis.tickLblPos = "low"
    for col, name in ((3, "PV cum (planned value)"),
                      (4, "EV cum (earned value)"),
                      (5, "AC cum (actual cost)")):
        ref = Reference(wb["EVM"], min_col=col, min_row=FIRST_ROW, max_row=evm_last)
        series = Series(ref, title=None)
        # Gotcha 6: titles_from_data pulls the header cell verbatim,
        # annotations and all. Set them explicitly.
        series.tx = SeriesLabel(v=name)
        series.smooth = False
        s_curve.series.append(series)
    s_curve.set_categories(labels_ref)
    dash.add_chart(s_curve, "F4")

    # Index trend.
    trend = LineChart()
    trend.title = "Cost and Schedule Performance Trend"
    trend.height, trend.width = 9, 26
    trend.y_axis.title = "Index"
    trend.x_axis.title = "Reporting period"
    trend.x_axis.auto = False
    trend.x_axis.tickLblPos = "low"
    # Gotcha 7: an auto-scaled index axis makes 0.87 look catastrophic or
    # negligible depending on the data. Pin it so periods are comparable.
    trend.y_axis.scaling.min, trend.y_axis.scaling.max = 0.5, 1.2
    trend.y_axis.majorUnit = 0.1
    for col, name in ((8, "CPI (cost)"), (9, "SPI (schedule)")):
        ref = Reference(wb["EVM"], min_col=col, min_row=FIRST_ROW,
                        max_row=FIRST_ROW + data_date - 1)
        series = Series(ref, title=None)
        series.tx = SeriesLabel(v=name)
        series.smooth = False
        trend.series.append(series)
    trend.set_categories(
        Reference(wb["EVM"], min_col=2, min_row=FIRST_ROW,
                  max_row=FIRST_ROW + data_date - 1)
    )
    dash.add_chart(trend, "F24")

    # ======================================================================
    # Variance by work package
    # ======================================================================
    ws = wb.create_sheet("Variance")
    ws["A1"] = f"Cost and Schedule Variance by Work Package — Period {data_date}"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = "Where the project variance actually is. Only packages that have started."
    ws["A2"].font = NOTE_FONT
    _headers(ws, 4, ["WBS ID", "Work Package", "Budget", "EV", "AC", "CV", "CPI", "% complete"],
             [10, 42, 16, 16, 16, 16, 11, 12])

    breakdown = variance_by_wbs(project, period=data_date, level=None)
    breakdown = breakdown[breakdown["ev"] > 0].sort_values("cv")
    for i, (_, row) in enumerate(breakdown.iterrows()):
        r = FIRST_ROW + i
        ws.cell(row=r, column=1, value=row["key"]).border = BOX
        ws.cell(row=r, column=2, value=row["name"]).border = BOX
        for col, value, fmt in (
            (3, row["budget"], RUPEES), (4, row["ev"], RUPEES),
            (5, row["ac"], RUPEES), (6, row["cv"], RUPEES),
            (7, row["cpi"], INDEX_FMT), (8, row["pct_complete"] / 100.0, PCT),
        ):
            c = ws.cell(row=r, column=col, value=float(value))
            c.number_format, c.border = fmt, BOX
            if col == 6:
                c.fill = BAD_FILL if value < 0 else GOOD_FILL
    var_last = FIRST_ROW + len(breakdown) - 1

    bars = BarChart()
    bars.type = "bar"
    bars.title = "Cost Variance by Work Package (negative is over budget)"
    bars.height, bars.width = 12, 24
    bars.y_axis.title = "Cost variance (Rs)"
    bars.x_axis.auto = False
    # Gotcha 3: on all-negative data the default puts the category labels at
    # the zero line, which is the top of the plot, over the title.
    bars.x_axis.tickLblPos = "low"
    # Gotcha 2: two series clustered can never exceed 50% of a slot, and a
    # single series at gapWidth 20 fills 83%. One series, narrow gap.
    bars.gapWidth = 30
    ref = Reference(ws, min_col=6, min_row=FIRST_ROW, max_row=var_last)
    series = Series(ref, title=None)
    series.tx = SeriesLabel(v="Cost variance")
    # Gotcha 5: absent, Excel treats invertIfNegative as true and fills
    # every negative bar white, so an all-negative series renders hollow.
    series.invertIfNegative = False
    bars.series.append(series)
    bars.set_categories(Reference(ws, min_col=2, min_row=FIRST_ROW, max_row=var_last))
    ws.add_chart(bars, "J4")

    # ======================================================================
    # Read Me
    # ======================================================================
    ws = wb.create_sheet("Read Me")
    ws.column_dimensions["A"].width = 100
    ws["A1"] = "About this workbook"
    ws["A1"].font = TITLE_FONT
    m = metrics_at(project, data_date)
    for i, line in enumerate([
        "",
        f"Exported from the CE725 EVM Dashboard for {project.meta.project_name}.",
        f"Data date: end of Period {data_date} ({project.meta.label(data_date)}).",
        "",
        "LIVE, NOT A SNAPSHOT",
        "",
        "Every figure on the Dashboard and EVM sheets is an Excel formula. Edit any",
        "yellow cell on Inputs or Baseline and the whole workbook recalculates. That",
        "is the point: the numbers can be interrogated and re-run without the tool.",
        "",
        "WHAT TO EDIT",
        "",
        "    Inputs    budgets, actual cost per period, percent complete per period",
        "    Baseline  the time-phased budget",
        "",
        "Nothing else is meant to be typed into.",
        "",
        "LIMITATIONS",
        "",
        "1. Earned value is only as good as the percent-complete figures on the",
        "   Inputs sheet. Those are a judgement made at site. Neither this workbook",
        "   nor the tool can detect an optimistic one, and an optimistic percent",
        "   complete produces a confident, wrong EV.",
        "2. There is one baseline. Re-baselining is not modelled.",
        "3. Earned Schedule is computed in the dashboard application, not here.",
        "4. The forecast assumes work continues. A suspended project needs a",
        "   re-baseline, not an extrapolation.",
        "",
        "POSITION AT EXPORT",
        "",
        f"    CPI {m.cpi:.3f}    SPI {m.spi:.3f}    "
        f"complete {m.pct_complete:.1f}%    spent {m.pct_spent:.1f}%",
        "",
        "These figures are stated here for reference only. The Dashboard sheet",
        "recomputes them from the inputs and is what should be read.",
    ], start=2):
        ws.cell(row=i, column=1, value=line)

    wb.calculation.fullCalcOnLoad = True
    destination.parent.mkdir(parents=True, exist_ok=True)
    wb.save(destination)
    return destination
