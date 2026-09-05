"""PipelineChart widget model for Covered On Baserow chart plugin.

Uses JSONField for series_config instead of a separate FK model
(no license gate — simplified from Baserow Premium's ChartWidget
which uses a ChartSeriesConfig FK model).
"""
from django.db import models

from baserow.contrib.dashboard.widgets.models import Widget


class PipelineChartChartType(models.TextChoices):
    """Chart types supported by the pipeline chart widget."""

    BAR = "BAR", "Bar"
    LINE = "LINE", "Line"


class PipelineChartWidget(Widget):
    """Concrete widget model for pipeline chart display.

    Extends Widget via multi-table inheritance (implicit widget_ptr
    OneToOneField to Widget). Stores series config as a JSON blob
    instead of a separate FK model to avoid the license gate
    complexity of the premium ChartWidget.

    Fields:
        data_source: FK to the DashboardDataSource created automatically
            by prepare_value_for_db. Deleted when the widget is deleted.
        series_config: JSON list of series configurations. Each entry
            contains series_id (int) and series_chart_type (str).
            Stored as JSONField because we don't have the
            ChartSeriesConfig FK model from premium.
        default_series_chart_type: Default chart type applied to any
            series that doesn't specify its own type. Choices: BAR, LINE.
    """

    data_source = models.ForeignKey(
        "dashboard.DashboardDataSource",
        on_delete=models.PROTECT,
        help_text="Data source for fetching the chart result to display.",
    )
    series_config = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Chart series configuration as a JSON list. Each object "
            "contains series_id and series_chart_type fields."
        ),
    )
    default_series_chart_type = models.CharField(
        max_length=4,
        choices=PipelineChartChartType.choices,
        default=PipelineChartChartType.BAR,
        help_text="Default chart type (BAR or LINE).",
    )