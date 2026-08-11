<template>
  <div>
    <div v-if="hasData" class="chart-container">
      <canvas id="bar-chart"></canvas>
    </div>
    <p v-else class="no-data-message">표시할 데이터가 없습니다.</p>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import Chart from "chart.js/auto";

const props = defineProps({
  labels: {
    type: Array,
    default: () => [],
  },
  datasets: {
    type: Array,
    default: () => [],
  },
  title: {
    type: String,
    default: "금리 비교 차트",
  },
});

const chartInstance = ref(null);

const hasData = computed(() => 
  props.labels.length > 0 && props.datasets.some(dataset => dataset.data.length > 0)
);

// debounce 함수
const debounce = (fn, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
};

const renderChart = () => {
  const canvas = document.getElementById("bar-chart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  if (chartInstance.value) {
    chartInstance.value.destroy();
  }

  // 데이터셋의 색상을 연한 연두색과 연보라색으로 설정
  const modifiedDatasets = props.datasets.map((dataset, index) => ({
    ...dataset,
    backgroundColor: index % 2 === 0 ? "rgba(50, 205, 50, 0.8)" : "rgba(186, 85, 211, 0.8)", // 더 밝고 강한 연두색, 연보라색
    borderColor: index % 2 === 0 ? "rgba(144, 238, 144, 1)" : "rgba(221, 160, 221, 1)", // 테두리 색상
    borderWidth: 1,
  }));

  chartInstance.value = new Chart(ctx, {
    type: "bar",
    data: {
      labels: props.labels,
      datasets: modifiedDatasets, // 수정된 색상 적용
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: props.title,
          font: { size: 16, weight: 'bold' }
        },
        tooltip: {
          callbacks: {
            label: (context) => `${context.dataset.label}: ${context.raw}%`
          }
        },
        legend: {
          display: true,
          position: "top",
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: '금리 (%)'
          },
          ticks: {
            callback: (value) => `${value}%`
          }
        },
        x: {
          ticks: {
            font: {
              size: 12
            }
          }
        }
      }
    }
  });
};


// 데이터 변경 감지
watch([() => props.labels, () => props.datasets], renderChart, { deep: true });

// 차트 생성 및 리사이즈 이벤트 처리
onMounted(() => {
  if (hasData.value) {
    renderChart();
    window.addEventListener('resize', debounce(renderChart, 250));
  }
});

// 컴포넌트 제거 시 이벤트 리스너 정리
onBeforeUnmount(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy();
  }
  window.removeEventListener('resize', debounce(renderChart, 250));
});
</script>
<style scoped>
.chart-container {
  max-width: 100%;
  height: 400px;
  margin: 20px auto;
  padding: 16px;
  background: #ffffff;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.no-data-message {
  text-align: center;
  color: #999;
  font-size: 16px;
  margin-top: 20px;
}
</style>
