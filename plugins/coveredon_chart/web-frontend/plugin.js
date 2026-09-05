import { PipelineChartWidgetType } from './widgetTypes'

/**
 * CoveredOn Chart Plugin — Nuxt plugin registration.
 * Registers the pipeline chart widget type in the dashboardWidget
 * registry namespace. Depends on core (registry) and dashboard
 * (dashboardWidget namespace).
 */
export default defineNuxtPlugin({
  name: 'coveredon-chart',
  dependsOn: ['core', 'dashboard'],
  setup(nuxtApp) {
    const { $registry } = nuxtApp
    const context = { app: nuxtApp }

    $registry.register(
      'dashboardWidget',
      new PipelineChartWidgetType(context)
    )
  },
})