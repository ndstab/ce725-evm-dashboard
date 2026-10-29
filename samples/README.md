# Sample output

`EVM_Report_Period6.xlsx` is a workbook exported from the dashboard for
the case study at its data date, committed so the output can be inspected
without running the tool.

Every figure in it is a **live Excel formula**. Edit any yellow cell on
the Inputs or Baseline sheet and the indices, forecasts, verdict and
charts all recalculate.

It is **not** the validation benchmark. A workbook the tool generated
cannot be an independent check on the tool. The benchmark is built
separately, by hand, in [`../benchmark/`](../benchmark/), and this export
is validated against it like everything else.
