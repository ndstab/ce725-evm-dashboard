"""EVM engine for the CE725 Earned Value Management dashboard."""

from .dataset import Project, ProjectMeta, load_project, DataValidationError
from .core import (
    PeriodMetrics, metrics_at, metrics_series, planned_value_curve,
    variance_by_wbs, pv_matrix, ev_matrix, ac_matrix,
)
from .earned_schedule import earned_schedule, earned_schedule_series, EarnedScheduleResult
from .forecasting import forecasts, tcpi_to_bac, feasibility_note, Forecast

__all__ = [
    "Project", "ProjectMeta", "load_project", "DataValidationError",
    "PeriodMetrics", "metrics_at", "metrics_series", "planned_value_curve",
    "variance_by_wbs", "pv_matrix", "ev_matrix", "ac_matrix",
    "earned_schedule", "earned_schedule_series", "EarnedScheduleResult",
    "forecasts", "tcpi_to_bac", "feasibility_note", "Forecast",
]
