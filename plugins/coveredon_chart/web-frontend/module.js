import { defineNuxtModule, addPlugin, createResolver } from 'nuxt/kit'

/**
 * CoveredOn Chart Plugin — Nuxt module.
 * Registers the Nuxt plugin that wires PipelineChartWidgetType into
 * the dashboardWidget registry.
 */
export default defineNuxtModule({
  meta: {
    name: '@coveredon/coveredon-chart-plugin',
    configKey: 'coveredonChart',
  },
  setup(options, nuxt) {
    const { resolve } = createResolver(import.meta.url)
    addPlugin(resolve('./plugin.js'))
  },
})