# coveredon-chart-plugin

Pipeline chart widget plugin for **Baserow 2.3.3**.

## What it does

Adds a `pipeline_chart` dashboard widget type that displays
BAR / LINE chart data from Baserow tables. Registered as both
a Baserow plugin and a dashboard widget type.

## No license gate

Unlike Baserow Premium's `ChartWidget`, this plugin has **no license
check** — any Baserow user can create pipeline chart widgets.

## Structure

```
plugins/coveredon_chart/backend/
├── setup.py                          # Package metadata
└── src/coveredon_chart/
    ├── __init__.py
    ├── apps.py                       # AppConfig + registry wiring
    ├── models.py                     # PipelineChartWidget model
    ├── plugins.py                    # Plugin registration
    ├── widget_types.py               # PipelineChartWidgetType
    └── migrations/
        ├── __init__.py
        └── 0001_initial.py           # Create PipelineChartWidget
```

## Key design decisions

- **JSONField for series_config** — Instead of a separate
  `ChartSeriesConfig` FK model (as in premium), series config is
  stored as a JSON list. This removes the license gate dependency
  on premium's model infrastructure and simplifies management.

- **Grouped-aggregate data source** — `prepare_value_for_db` creates
  a `LocalBaserowGroupedAggregateRowsUserServiceType` data source
  automatically (falls back to `AggregateRowsUserServiceType` if
  premium is not importable).

- **No API endpoints** — The existing dashboard API auto-dispatches
  to widget types via the registry. No custom API wiring needed.

## Installation

Place this plugin in Baserow's plugin directory and add
`coveredon_chart` to `INSTALLED_APPS` in the Baserow settings.
Run `./baserow migrate` to apply the migration.