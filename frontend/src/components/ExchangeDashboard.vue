<template>
    <div>
      <h1>환율 대시보드</h1>
  
      <!-- 갱신 버튼 -->
      <button @click="refreshExchangeData" :disabled="loading">
        {{ loading ? "갱신 중..." : "환율 데이터 갱신" }}
      </button>
  
      <!-- 강조 카드 -->
      <div class="highlight-cards">
        <div v-for="card in highlightCards" :key="card.cur_unit" class="highlight-card">
          <h2>{{ card.cur_nm }} ({{ card.cur_unit }})</h2>
          <p>매매기준율: {{ card.deal_bas_r }}</p>
          <p>장부가격: {{ card.bkpr }}</p>
        </div>
      </div>
  
      <!-- 차트 영역 -->
      <div id="exchange-chart"></div>
  
      <!-- 테이블 -->
      <table>
        <thead>
          <tr>
            <th>통화 단위</th>
            <th>통화명</th>
            <th>매매기준율</th>
            <th>장부가격</th>
            <th>전신환 받기</th>
            <th>전신환 보내기</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="exchange in exchanges" :key="exchange.cur_unit">
            <td>{{ exchange.cur_unit }}</td>
            <td>{{ exchange.cur_nm }}</td>
            <td>{{ exchange.deal_bas_r }}</td>
            <td>{{ exchange.bkpr }}</td>
            <td>{{ exchange.ttb }}</td>
            <td>{{ exchange.tts }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script setup>
  import { onMounted, ref, computed } from "vue";
  import { fetchExchangeData, getExchangeData } from "@/utils/exchange";
  
  // 상태 관리
  const exchanges = ref([]);
  const loading = ref(false);
  
  // 주요 통화 강조 카드 데이터 계산
  const highlightCards = computed(() =>
    exchanges.value
      .filter((item) => ["USD", "EUR", "JPY"].includes(item.cur_unit)) // 주요 통화 필터링
      .slice(0, 3) // 최대 3개 표시
  );
  
  // 데이터 로드
  const loadExchangeData = async () => {
  try {
    loading.value = true;
    const response = await getExchangeData(); // API 호출
    const data = response.data; // 응답 데이터

    console.log("API 응답 데이터:", data);

    if (Array.isArray(data) && data.length > 0) {
      exchanges.value = [...data]; // 배열 복사로 반응형 적용
      console.log("저장된 exchanges 데이터:", exchanges.value);
    } else {
      console.warn("API 데이터가 배열이 아니거나 비어 있습니다.");
    }
  } catch (error) {
    console.error("환율 데이터를 가져오는 중 오류 발생:", error);
  } finally {
    loading.value = false;
  }
};

  
  // 데이터 갱신
  const refreshExchangeData = async () => {
    try {
      loading.value = true;
      await fetchExchangeData();
      await loadExchangeData();
    } catch (error) {
      console.error("환율 데이터를 갱신하는 중 오류 발생:", error);
    } finally {
      loading.value = false;
    }
  };
  
  // 차트 렌더링
  const renderChart = (data) => {
    const chartData = data.map((item) => ({
      name: item.cur_nm,
      value: parseFloat(item.deal_bas_r),
    }));
  
    const chart = echarts.init(document.getElementById("exchange-chart"));
    const options = {
      title: { text: "통화별 매매기준율", left: "center" },
      tooltip: {},
      xAxis: {
        type: "category",
        data: chartData.map((item) => item.name),
      },
      yAxis: { type: "value" },
      series: [
        {
          data: chartData.map((item) => item.value),
          type: "bar",
        },
      ],
    };
  
    chart.setOption(options);
  };
  
  onMounted(() => {
    loadExchangeData();
  });
  </script>
  
  <style scoped>
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
  }
  
  th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
  }
  
  th {
    background-color: #f4f4f4;
    font-weight: bold;
  }
  
  button {
    padding: 10px 15px;
    margin-bottom: 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  
  button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .highlight-cards {
    display: flex;
    gap: 10px;
    margin: 20px 0;
  }
  
  .highlight-card {
    flex: 1;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
    text-align: center;
    background-color: #f9f9f9;
  }
  
  .highlight-card h2 {
    margin-bottom: 10px;
    font-size: 18px;
    color: #333;
  }
  
  #exchange-chart {
    width: 100%;
    height: 400px;
    margin: 20px 0;
  }
  </style>
  