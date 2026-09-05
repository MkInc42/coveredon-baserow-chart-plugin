<template>
  <div class="pipeline-chart-settings">
    <AggregateRowsDataSourceForm
      v-if="dataSource"
      ref="dataSourceForm"
      :dashboard="dashboard"
      :widget="widget"
      :data-source="dataSource"
      :default-values="dataSource"
      :store-prefix="storePrefix"
      @values-changed="onDataSourceValuesChanged"
    />
    <div class="pipeline-chart-settings__chart-type">
      <label class="control-label">
        Chart Type
      </label>
      <select
        class="pipeline-chart-settings__chart-type-select"
        :value="chartTypeValue"
        @change="onChartTypeChanged($event.target.value)"
      >
        <option value="BAR">Bar</option>
        <option value="LINE">Line</option>
      </select>
    </div>
  </div>
</template>

<script>
import AggregateRowsDataSourceForm from '@baserow/modules/dashboard/components/data_source/AggregateRowsDataSourceForm'
import error from '@baserow/modules/core/mixins/error'
import { notifyIf } from '@baserow/modules/core/utils/error'

export default {
  name: 'PipelineChartSettings',
  components: { AggregateRowsDataSourceForm },
  mixins: [error],
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
  },
  data() {
    return {
      loading: false,
    }
  },
  computed: {
    dataSource() {
      return this.$store.getters[
        `${this.storePrefix}dashboardApplication/getDataSourceById`
      ](this.widget.data_source_id)
    },
    integration() {
      return this.$store.getters[
        `${this.storePrefix}dashboardApplication/getIntegrationById`
      ](this.dataSource?.integration_id)
    },
    chartTypeValue() {
      return this.widget.default_series_chart_type || 'BAR'
    },
  },
  methods: {
    async onDataSourceValuesChanged(changedDataSourceValues) {
      if (this.$refs.dataSourceForm.isFormValid()) {
        try {
          await this.$store.dispatch(
            `${this.storePrefix}dashboardApplication/updateDataSource`,
            {
              dataSourceId: this.dataSource.id,
              values: changedDataSourceValues,
            },
          )
        } catch (error) {
          this.$refs.dataSourceForm.reset()
          this.$refs.dataSourceForm.touch()
          notifyIf(error, 'dashboard')
        }
      }
    },

    async onChartTypeChanged(value) {
      const originalValues = JSON.parse(JSON.stringify(this.widget))
      const values = JSON.parse(JSON.stringify(this.widget))
      values.default_series_chart_type = value
      try {
        await this.$store.dispatch(
          `${this.storePrefix}dashboardApplication/updateWidget`,
          {
            widgetId: this.widget.id,
            values,
            originalValues,
          },
        )
      } catch (error) {
        notifyIf(error, 'dashboard')
      }
    },
  },
}
</script>

<style>
.pipeline-chart-settings__chart-type {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.pipeline-chart-settings__chart-type .control-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #555;
}

.pipeline-chart-settings__chart-type-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  background: #fff;
  font-size: 14px;
  color: #333;
  cursor: pointer;
}

.pipeline-chart-settings__chart-type-select:focus {
  border-color: #5190ef;
  outline: none;
  box-shadow: 0 0 0 2px rgba(81, 144, 239, 0.2);
}
</style>