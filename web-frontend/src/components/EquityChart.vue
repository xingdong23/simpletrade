<template>
  <div>
    <div ref="chartDivRef" style="width: 100%; height: 400px;"></div>
    <div v-if="!props.equityCurve || props.equityCurve.length === 0" class="text-grey text-center q-pa-md">
      资金曲线数据不可用。
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick, defineProps } from 'vue';

const props = defineProps({
  equityCurve: {
    type: Array,
    default: () => []
  }
});

const chartDivRef = ref(null);
let Plotly = null; 

const drawChart = async () => {
  if (!props.equityCurve || props.equityCurve.length === 0) {
    if (Plotly && chartDivRef.value) {
      try {
        Plotly.purge(chartDivRef.value);
      } catch (e) {
        console.error('Error purging chart:', e);
      }
    }
    return;
  }

  if (!Plotly) {
    try {
      Plotly = await import('plotly.js-dist-min');
    } catch (e) {
      console.error('Failed to load Plotly:', e);
      return;
    }
  }

  await nextTick(); 

  if (!chartDivRef.value) {
    console.error('Chart div not available');
    return;
  }

  const dates = props.equityCurve.map(point => point.datetime);
  const equity = props.equityCurve.map(point => point.equity);

  const trace = {
    x: dates,
    y: equity,
    mode: 'lines',
    type: 'scatter',
    name: '资金曲线',
    line: { color: '#1f77b4' }
  };

  const layout = {
    title: '账户资金随时间变化',
    xaxis: {
      title: '日期',
      type: 'date',
      tickformat: '%Y-%m-%d',
    },
    yaxis: {
      title: '资金 (元)',
      autorange: true,
      type: 'linear'
    },
    margin: { l: 60, r: 30, b: 50, t: 50, pad: 4 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
  };

  const config = {
    responsive: true,
    displaylogo: false,
  };

  try {
    Plotly.newPlot(chartDivRef.value, [trace], layout, config);
  } catch (e) {
    console.error('Error drawing Plotly chart:', e);
  }
};

watch(() => props.equityCurve, (newData, oldData) => {
  if (JSON.stringify(newData) !== JSON.stringify(oldData)) {
    drawChart();
  }
}, { deep: true });

onMounted(async () => {
  try {
    const plotlyModule = await import('plotly.js-dist-min');
    Plotly = plotlyModule.default || plotlyModule; 

    if (Plotly) {
      await nextTick(); 
      drawChart(); 
    } else {
      console.error('Plotly library failed to load.');
    }
  } catch (error) {
    console.error('Error loading or initializing Plotly:', error);
  }
});
</script>

<style scoped>
/* Add any component-specific styles here */
</style>
