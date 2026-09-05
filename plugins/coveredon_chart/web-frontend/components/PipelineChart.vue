<template>
  <div
    class="dashboard-pipeline-chart-widget"
    :class="{
      'dashboard-pipeline-chart-widget--with-header-description': widget.description,
    }"
  >
    <template v-if="!loading">
      <div class="widget__header widget__header--no-border">
        <div class="widget__header-main">
          <div class="widget__header-title-wrapper">
            <div class="widget__header-title">{{ widget.title }}</div>
            <span
              v-if="dataSourceMisconfigured"
              class="badge badge--red"
            >{{ $t('widget.fixConfiguration') }}</span>
          </div>
          <div
            v-if="widget.description"
            class="widget__header-description"
          >{{ widget.description }}</div>
        </div>
        <WidgetContextMenu
          v-if="isEditMode"
          :widget="widget"
          :dashboard="dashboard"
          @delete-widget="$emit('delete-widget', $event)"
        />
      </div>
      <div
        class="widget__content dashboard-pipeline-chart-widget__chart"
        :class="{
          'dashboard-pipeline-chart-widget__chart--misconfigured': dataSourceMisconfigured,
        }"
      >
        <Bar
          v-if="chartData.datasets.length > 0"
          ref="chartRef"
          :options="chartOptions"
          :data="chartData"
          class="chart"
        />
        <div v-else class="chart__no-data">
          <span class="chart__no-data-dashed-line" />
          <span class="chart__no-data-dashed-line" />
          <span class="chart__no-data-dashed-line" />
          <span class="chart__no-data-dashed-line" />
          <span class="chart__no-data-dashed-line" />
          <span class="chart__no-data-plain-line" />
        </div>
      </div>
    </template>
    <div v-else class="dashboard-pipeline-chart-widget__loading loading-spinner" />
  </div>
</template>

<script>
import WidgetContextMenu from '@baserow/modules/dashboard/components/widget/WidgetContextMenu'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarElement,
  LineElement,
  PointElement,
  BarController,
  LineController,
  CategoryScale,
  LinearScale,
  Filler,
  Legend,
  Title,
  Tooltip,
} from 'chart.js'

// Register only the Chart.js components we need (BAR and LINE support).
ChartJS.register(
  BarElement,
  LineElement,
  PointElement,
  BarController,
  LineController,
  CategoryScale,
  LinearScale,
  Filler,
  Legend,
  Title,
  Tooltip,
)

const DEFAULT_COLOR = '#5190ef'
const CHART_COLORS = [
  '#5190ef',
  '#e66464',
  '#63b87c',
  '#f0ad4e',
  '#9b59b6',
  '#1abc9c',
  '#e67e22',
  '#2c3e50',
  '#c0392b',
  '#16a085',
]

export default {
  name: 'PipelineChart',
  components: { WidgetContextMenu, Bar },
  emits: ['delete-widget'],
  props: {
    dashboard: {
      type: Object,
      required: true,
    },
    widget: {
      type: Object,
      required: true,
    },
    storePrefix: {
      type: String,
      required: false,
      default: '',
    },
    loading: {
      type: Boolean,
      required: false,
      default: false,
    },
    editMode: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      chartData: { labels: [], datasets: [] },
      chartOptions: this.buildDefaultOptions(),
      dataSourceData: null,
      fetchLoading: false,
    }
  },
  computed: {
    dataSource() {
      return this.$store.getters[
        `${this.storePrefix}dashboardApplication/getDataSourceById`
      ](this.widget.data_source_id)
    },
    dataForDataSource() {
      return this.$store.getters[
        `${this.storePrefix}dashboardApplication/getDataForDataSource`
      ](this.dataSource?.id)
    },
    isEditMode() {
      return this.$store.getters[
        `${this.storePrefix}dashboardApplication/isEditMode`
      ]
    },
    dataSourceMisconfigured() {
      const data = this.dataForDataSource
      if (data) {
        return !!data._error
      }
      return false
    },
    chartType() {
      return (this.widget.default_series_chart_type || 'BAR').toLowerCase()
    },
  },
  watch: {
    'widget.data_source_id': {
      immediate: true,
      handler() {
        this.fetchChartData()
      },
    },
  },
  methods: {
    buildDefaultOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            align: 'start',
            position: 'bottom',
            labels: {
              usePointStyle: true,
              boxWidth: 14,
              pointStyle: 'circle',
              padding: 20,
            },
          },
          tooltip: {
            backgroundColor: '#202128',
            padding: 10,
            bodyFont: { size: 12 },
            titleFont: { size: 12 },
          },
        },
        elements: {
          bar: {
            borderRadius: {
              topLeft: 4,
              topRight: 4,
              bottomLeft: 0,
              bottomRight: 0,
            },
            borderWidth: 1,
          },
          line: {
            tension: 0.3,
            borderWidth: 2,
            pointRadius: 3,
            pointHoverRadius: 5,
            fill: false,
          },
        },
      }
    },

    async fetchChartData() {
      const dataSourceId = this.widget.data_source_id
      if (!dataSourceId) {
        this.chartData = { labels: [], datasets: [] }
        return
      }

      // Try the store first — the core dashboard may have already
      // dispatched the data source.
      const storeData = this.dataForDataSource
      if (storeData && !storeData._error) {
        this.dataSourceData = storeData
        this.buildChartData()
        return
      }

      // Fallback: manually dispatch via API.
      this.fetchLoading = true
      try {
        const { data } = await this.$client.post(
          `dashboard/data-sources/${dataSourceId}/dispatch/`,
        )
        this.dataSourceData = data
        this.buildChartData()
      } catch (e) {
        this.dataSourceData = null
        this.chartData = { labels: [], datasets: [] }
      } finally {
        this.fetchLoading = false
      }
    },

    buildChartData() {
      if (!this.dataSource || !this.dataSourceData) {
        this.chartData = { labels: [], datasets: [] }
        return
      }

      const result = this.dataSourceData.result
      if (!result) {
        this.chartData = { labels: [], datasets: [] }
        return
      }

      // Determine if the result is grouped (array) or ungrouped (object).
      if (Array.isArray(result)) {
        this.buildGroupedChartData(result)
      } else {
        this.buildUngroupedChartData(result)
      }
    },

    buildGroupedChartData(rows) {
      const dataSource = this.dataSource
      const aggGroupBys = dataSource.aggregation_group_bys || []
      const aggSeries = dataSource.aggregation_series || []

      if (!aggSeries.length) {
        this.chartData = { labels: rows.map(() => ''), datasets: [] }
        return
      }

      // Build labels from the first group-by field (or row index).
      const groupByFieldId =
        aggGroupBys.length > 0 ? aggGroupBys[0].field_id : null
      const labels = rows.map((row) => {
        if (groupByFieldId) {
          const val = row[`field_${groupByFieldId}`]
          return val !== undefined && val !== null ? String(val) : ''
        }
        return ''
      })

      // Build datasets from aggregation series.
      const datasets = aggSeries.map((series, index) => {
        const fieldName = `field_${series.field_id}`
        const aggKey = `${fieldName}_${series.aggregation_type}`
        const label = series.aggregation_type.toUpperCase()
        const color = CHART_COLORS[index % CHART_COLORS.length]
        return {
          type: this.chartType,
          label,
          data: rows.map((row) => row[aggKey] ?? 0),
          backgroundColor: color,
          borderColor: color,
          hoverBackgroundColor: color,
          ...(this.chartType === 'line'
            ? {
                borderColor: color,
                backgroundColor: color + '20',
                pointBackgroundColor: color,
                pointBorderColor: color,
              }
            : {}),
        }
      })

      this.chartData = { labels, datasets }
    },

    buildUngroupedChartData(result) {
      const dataSource = this.dataSource
      const aggSeries = dataSource.aggregation_series || []

      if (!aggSeries.length) {
        this.chartData = { labels: [''], datasets: [] }
        return
      }

      const labels = ['']
      const datasets = aggSeries.map((series, index) => {
        const fieldName = `field_${series.field_id}`
        const aggKey = `${fieldName}_${series.aggregation_type}`
        const label = series.aggregation_type.toUpperCase()
        const color = CHART_COLORS[index % CHART_COLORS.length]
        return {
          type: this.chartType,
          label,
          data: [result[aggKey] ?? 0],
          backgroundColor: color,
          borderColor: color,
          hoverBackgroundColor: color,
        }
      })

      this.chartData = { labels, datasets }
    },
  },
}
</script>

<style>
.dashboard-pipeline-chart-widget {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* ── Inline placeholder for SVG assets (no SVG files needed) ── */
.dashboard-pipeline-chart-widget .chart__no-data {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  align-items: stretch;
  justify-content: center;
  flex: 1;
}

.dashboard-pipeline-chart-widget .chart__no-data-dashed-line {
  display: block;
  height: 12px;
  background: repeating-linear-gradient(
    90deg,
    #e0e0e0 0px,
    #e0e0e0 6px,
    transparent 6px,
    transparent 10px
  );
  border-radius: 2px;
}

.dashboard-pipeline-chart-widget .chart__no-data-plain-line {
  display: block;
  height: 12px;
  background: #e0e0e0;
  border-radius: 2px;
}

.dashboard-pipeline-chart-widget .widget__content {
  flex: 1;
  min-height: 200px;
}

.dashboard-pipeline-chart-widget .chart {
  height: 100% !important;
  width: 100% !important;
}

/* ── Match core SummaryWidget loading style ── */
.dashboard-pipeline-chart-widget__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}
</style>