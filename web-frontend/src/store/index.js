import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    dataOverview: [],
    currentData: null,
    analysisResults: null
  },
  mutations: {
    setDataOverview(state, overview) {
      state.dataOverview = overview
    },
    setCurrentData(state, data) {
      state.currentData = data
    },
    setAnalysisResults(state, results) {
      state.analysisResults = results
    }
  },
  actions: {
    async fetchDataOverview({ commit }) {
      try {
        const response = await fetch('http://localhost:8003/api/data/overview')
        const data = await response.json()
        if (data.success) {
          commit('setDataOverview', data.data)
        }
      } catch (error) {
        console.error('Error fetching data overview:', error)
      }
    },
    async fetchBarData({ commit }, { symbol, exchange, interval, startDate, endDate }) {
      try {
        const url = `http://localhost:8003/api/data/bars?symbol=${symbol}&exchange=${exchange}&interval=${interval}&start_date=${startDate}${endDate ? `&end_date=${endDate}` : ''}`
        const response = await fetch(url)
        const data = await response.json()
        if (data.success) {
          commit('setCurrentData', data.data)
        }
        return data
      } catch (error) {
        console.error('Error fetching bar data:', error)
        return { success: false, message: error.message }
      }
    },
    async calculateIndicators({ commit }, payload) {
      try {
        const response = await fetch('http://localhost:8003/api/analysis/indicators', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })
        const data = await response.json()
        if (data.success) {
          commit('setAnalysisResults', data.data)
        }
        return data
      } catch (error) {
        console.error('Error calculating indicators:', error)
        return { success: false, message: error.message }
      }
    },
    async runBacktest({ commit }, payload) {
      try {
        const response = await fetch('http://localhost:8003/api/analysis/backtest', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })
        const data = await response.json()
        if (data.success) {
          commit('setAnalysisResults', data.data)
        }
        return data
      } catch (error) {
        console.error('Error running backtest:', error)
        return { success: false, message: error.message }
      }
    }
  },
  modules: {
  }
})
