"""Initial migration for the coveredon_chart plugin.

Creates the PipelineChartWidget model extending Widget with
data_source FK, JSONField series_config, and default_series_chart_type.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("dashboard", "0001_initial"),  # Base dashboard migration (Widget table)
        # The Widget model comes from baserow.contrib.dashboard.widgets.models
        # which is part of the core "dashboard" app.
        ("dashboard", "0002_dashboard_widgets"),  # Widget model creation
    ]

    operations = [
        migrations.CreateModel(
            name="PipelineChartWidget",
            fields=[
                (
                    "widget_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=models.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="dashboard.widget",
                    ),
                ),
                (
                    "data_source",
                    models.ForeignKey(
                        on_delete=models.deletion.PROTECT,
                        to="dashboard.dashboarddatasource",
                        help_text="Data source for fetching the chart result.",
                    ),
                ),
                (
                    "series_config",
                    models.JSONField(
                        default=list,
                        blank=True,
                        help_text=(
                            "Chart series configuration as a JSON list."
                            " Each object contains series_id and"
                            " series_chart_type fields."
                        ),
                    ),
                ),
                (
                    "default_series_chart_type",
                    models.CharField(
                        max_length=4,
                        choices=[("BAR", "Bar"), ("LINE", "Line")],
                        default="BAR",
                        help_text="Default chart type (BAR or LINE).",
                    ),
                ),
            ],
            options={
                "ordering": ("order", "id"),
            },
            bases=("dashboard.widget",),
        ),
    ]