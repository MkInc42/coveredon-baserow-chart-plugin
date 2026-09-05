"""Covered On chart plugin — registers the plugin with Baserow.

Minimal Plugin subclass that declares a type string used for
identification in the plugin registry. This plugin does not provide
any API endpoints (the pipeline_chart widget type is fully served
by the existing dashboard API via widget_type_registry).
"""
from baserow.core.registries import Plugin


class CoveredonChartPlugin(Plugin):
    """Plugin registration for coveredon_chart.

    The type string 'coveredon_chart' appears in Baserow's plugin admin
    and is used to identify this plugin in the plugin_registry.
    No API URL registration needed — the widget type is auto-served
    by the dashboard API via the WidgetType registry.
    """

    type = "coveredon_chart"