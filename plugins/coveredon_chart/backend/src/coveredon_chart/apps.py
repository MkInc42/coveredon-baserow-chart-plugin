"""Django AppConfig for the coveredon_chart plugin.

Registers the PipelineChartWidgetType in both the widget type registry
and the global plugin registry so Baserow discovers and loads the
chart widget type on startup.
"""
from baserow.core.registries import plugin_registry
from django.apps import AppConfig


class CoveredonChartConfig(AppConfig):
    """AppConfig for the coveredon_chart Baserow plugin.

    The ready() method is called by Django after all apps are loaded,
    which is the earliest safe point to register widget types and
    plugin instances in Baserow's registries.
    """
    name = "coveredon_chart"

    def ready(self):
        """Register widget type and plugin during Baserow startup.

        Both registrations are required:
          - widget_type_registry: so the dashboard API knows about the
            pipeline_chart widget type and can serve/create it.
          - plugin_registry: so Baserow lists this plugin in its
            plugin admin and lifecycle management.
        """
        from .widget_types import PipelineChartWidgetType
        from .plugins import CoveredonChartPlugin
        from baserow.contrib.dashboard.widgets.registries import (
            widget_type_registry,
        )

        widget_type_registry.register(PipelineChartWidgetType())
        plugin_registry.register(CoveredonChartPlugin())