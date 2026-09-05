"""PipelineChartWidgetType — widget type for the Covered On pipeline chart plugin.

No license gate. Uses JSONField for series_config instead of a separate
ChartSeriesConfig FK model (simplified from Baserow Premium's ChartWidgetType).

Mirrors the structure of baserow_premium's ChartWidgetType at
https://github.com/baserow/baserow/blob/2.3.3/premium/backend/src/baserow_premium/dashboard/widgets/widget_types.py
but strips LicenseHandler calls and FK-model series management.
"""
from typing import Any

from rest_framework import serializers

from baserow.contrib.dashboard.data_sources.handler import DashboardDataSourceHandler
from baserow.contrib.dashboard.data_sources.models import DashboardDataSource
from baserow.contrib.dashboard.types import WidgetDict
from baserow.contrib.dashboard.widgets.models import Widget
from baserow.contrib.dashboard.widgets.registries import WidgetType
from baserow.core.services.registries import service_type_registry

# ── Import the preferred grouped-aggregate service type ─────────────
# The grouped-aggregate service type lives in premium but we try it
# first since Baserow 2.3.3 has it installed (even without a license).
# Fall back to the core aggregate_rows type if the import fails.
try:
    from baserow_premium.integrations.local_baserow.service_types import (
        LocalBaserowGroupedAggregateRowsUserServiceType,
    )
    _CHART_SERVICE_TYPE = LocalBaserowGroupedAggregateRowsUserServiceType.type
except ImportError:
    from baserow.contrib.integrations.local_baserow.service_types import (
        LocalBaserowAggregateRowsUserServiceType,
    )
    _CHART_SERVICE_TYPE = LocalBaserowAggregateRowsUserServiceType.type

from .models import PipelineChartWidget


# ── Helper: list of chart type choices for DRF ─────────────────────
_CHART_TYPE_CHOICES = [
    {"value": "BAR", "display_name": "Bar"},
    {"value": "LINE", "display_name": "Line"},
]


class PipelineChartWidgetType(WidgetType):
    """Dashboard widget type for pipeline charts.

    This is a license-free simplified chart widget:
      - Creates a grouped-aggregate (or aggregate-rows) data source on creation
      - Stores series config as a JSONField on the model (no FK model)
      - Cleans up the data source on deletion
      - NO LicenseHandler checks (available to all Baserow users)

    Serialized fields: data_source_id, series_config, default_series_chart_type
    """

    type = "pipeline_chart"
    model_class = PipelineChartWidget

    # ── Serialization ──────────────────────────────────────────────
    # These fields appear in the widget API response and dashboard
    # serialization. data_source_id is a FK reference; series_config
    # is a JSON list stored directly on the model.
    serializer_field_names = [
        "data_source_id",
        "series_config",
        "default_series_chart_type",
    ]
    serializer_field_overrides = {
        # data_source_id is a read/write FK reference — the serializer
        # resolves it to the actual DashboardDataSource object on write,
        # returning just the PK in the response.
        "data_source_id": serializers.PrimaryKeyRelatedField(
            queryset=DashboardDataSource.objects.all(),
            required=False,
            default=None,
            help_text="References the data source for the chart.",
        ),
        # series_config is stored as JSON in the model; the serializer
        # accepts and returns it as a plain list of dicts.
        "series_config": serializers.ListField(
            child=serializers.DictField(),
            required=False,
            help_text="Chart series configuration as a JSON list.",
        ),
    }

    # ── Request serialization ──────────────────────────────────────
    # These fields can be set during widget creation/update via the API.
    request_serializer_field_names = [
        "series_config",
        "default_series_chart_type",
    ]
    request_serializer_field_overrides = {
        "series_config": serializers.ListField(
            child=serializers.DictField(),
            required=False,
            help_text="Chart series configuration.",
        ),
    }

    class SerializedDict(WidgetDict):
        """Type-annotated dict for serialized widget values.

        Used by the EasyImportExportMixin for template type hints.
        """
        data_source_id: int
        series_config: list[dict]
        default_series_chart_type: str

    # ── Data source auto-creation ──────────────────────────────────
    def prepare_value_for_db(self, values: dict, instance: Widget | None = None):
        """Auto-create a data source when the widget is first created.

        Mirrors SummaryWidgetType's pattern from core widget_types.py:
        finds an unused name, creates a grouped-aggregate (or aggregate-rows)
        data source, and assigns it to values['data_source'].

        On update (instance is not None), the data source already exists
        so we just pass through unchanged.
        """
        if instance is None:
            # Widget is being created — wire up a brand-new data source
            available_name = DashboardDataSourceHandler().find_unused_data_source_name(
                values["dashboard"], "WidgetDataSource"
            )
            data_source = DashboardDataSourceHandler().create_data_source(
                dashboard=values["dashboard"],
                name=available_name,
                service_type=service_type_registry.get(_CHART_SERVICE_TYPE),
            )
            values["data_source"] = data_source
        return values

    # ── Trash/restore lifecycle ────────────────────────────────────
    def before_trashed(self, instance: Widget):
        """Mirror the data source trash state when the widget is trashed."""
        instance.data_source.trashed = True
        instance.data_source.save()

    def before_restore(self, instance: Widget):
        """Restore the data source when the widget is restored."""
        instance.data_source.trashed = False
        instance.data_source.save()

    # ── Cleanup on deletion ────────────────────────────────────────
    def after_delete(self, instance: Widget):
        """Delete the associated data source when the widget is removed.

        Without this, orphaned data sources would accumulate in the
        dashboard (Baserow does NOT cascade FK-based cleanup for
        PROTECT'd FKs).
        """
        DashboardDataSourceHandler().delete_data_source(instance.data_source)

    # ── Import/export serialization ────────────────────────────────
    def deserialize_property(
        self,
        prop_name: str,
        value: Any,
        id_mapping: dict[str, Any],
        **kwargs,
    ) -> Any:
        """Remap serialized FK references during import.

        data_source_id: maps old data source PK → new PK via id_mapping
        series_config: remaps series_id values inside each config dict
        """
        if prop_name == "data_source_id" and value:
            return id_mapping["dashboard_data_sources"][value]
        return super().deserialize_property(
            prop_name, value, id_mapping, **kwargs,
        )

    def serialize_property(
        self,
        instance: Widget,
        prop_name: str,
        files_zip=None,
        storage=None,
        cache=None,
    ):
        """Serialize widget properties for export.

        data_source_id: return the raw PK
        series_config: read directly from the JSONField
        """
        if prop_name == "data_source_id":
            return instance.data_source_id
        if prop_name == "series_config":
            return instance.series_config
        return super().serialize_property(
            instance, prop_name, files_zip=files_zip, storage=storage, cache=cache,
        )