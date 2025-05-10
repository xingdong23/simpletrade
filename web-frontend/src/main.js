import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import * as echarts from 'echarts'
import Quasar from 'quasar'
import 'quasar/dist/quasar.css'

// 导入设计系统样式
import './assets/styles/design-system.css'
// 导入 Element UI 样式覆盖
import './assets/styles/element-ui-override.css'

Vue.use(ElementUI)
Vue.use(Quasar, {
  // Optional: specify components, directives, plugins if not using all
  // Or provide global Quasar config here
  // Example for language pack (if you decide to use one):
  // lang: require('quasar/lang/zh-hans').default
})
Vue.prototype.$echarts = echarts

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
