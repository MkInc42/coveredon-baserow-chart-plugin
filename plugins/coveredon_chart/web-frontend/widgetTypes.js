import { WidgetType } from '@baserow/modules/dashboard/widgetTypes'
import PipelineChart from './components/PipelineChart.vue'
import PipelineChartSettings from './components/PipelineChartSettings.vue'

/**
 * PipelineChartWidgetType - a license-free bar/line chart widget for
 * Baserow dashboards (mirrors premium ChartWidgetType without premium
 * imports, license gating, or per-series config complexity).
 *
 * Variations:
 *   - BAR  -> default_series_chart_type='BAR'
 *   - LINE -> default_series_chart_type='LINE'
 *
 * The backend auto-creates a grouped-aggregate (or aggregate-rows) data
 * source when the widget is first created, so settings only need a
 * chart-type dropdown.
 */
export class PipelineChartWidgetType extends WidgetType {
  static getType() {
    return 'pipeline_chart'
  }

  get name() {
    return 'Pipeline Chart'
  }

  get component() {
    return PipelineChart
  }

  get settingsComponent() {
    return PipelineChartSettings
  }

  get variations() {
    return [
      {
        name: 'Bar',
        type: this,
        params: {
          default_series_chart_type: 'BAR',
        },
      },
      {
        name: 'Line',
        type: this,
        params: {
          default_series_chart_type: 'LINE',
        },
      },
    ]
  }

  /**
   * Returns true until the data source has loaded data into the store.
   * Core dashboard store populates `data[dataSourceId]` after dispatch.
   */
  isLoading(widget, data) {
    const dataSourceId = widget.data_source_id
    if (data[dataSourceId] && Object.keys(data[dataSourceId]).length !== 0) {
      return false
    }
    return true
  }
}