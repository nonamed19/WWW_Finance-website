<template>
  <div class="home-page">
    <!-- 캐러샐 섹션 -->
    <div class="carousel-container">
      <Carousel />
    </div>

    <!-- 날짜, 세계 증시, 금융 뉴스 -->
    <div class="info-box">
      <p class="date">{{ currentDate }}</p>
      <!-- 세계 증시 -->
      <div class="stock-market">
        <h3>세계 증시</h3>
        <ul class="stock-list">
          <li v-for="(stock, index) in stockData" :key="index">
            <span>{{ stock.name }}:</span>
            <span>{{ stock.price || "N/A" }}</span>
            <span :class="['change-icon', stock.direction]">
              <template v-if="stock.direction === 'up'">▲ {{ stock.change }}</template>
              <template v-else-if="stock.direction === 'down'">▼ {{ stock.change }}</template>
              <template v-else>시장 닫힘</template>
            </span>
          </li>
        </ul>
      </div>

      <!-- 구분선 -->
      <div class="divider"></div>

      <!-- 금융 뉴스 -->
      <div class="financial-news">
        <h3>금융 뉴스</h3>
        <ul class="news-list">
          <li v-for="(news, index) in limitedNews" :key="index" class="news-item">
            <h4 v-html="news.title"></h4>
            <p>{{ truncateText(news.description, 15) }}</p>
          </li>
        </ul>
        <button class="news-button" @click="goToPage('news')">더 많은 뉴스 보기</button>
      </div>
    </div>

    <!-- 지도 섹션 -->
    <div class="map-box">
      <Mapcopy />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios"; 
import { useRouter } from "vue-router";
import Carousel from "@/components/Carousel.vue";
import Mapcopy from "@/components/Mapcopy.vue";

import { useNewsStore } from "@/stores/news";

const { limitedNews, fetchNewsData } = useNewsStore();

const router = useRouter();

const currentDate = ref(""); // 초기화된 ref 선언
const stockData = ref([
  { name: "Loading...", price: "-", direction: "up" }
]);

const API_URL = "http://127.0.0.1:8000";

const fetchStockData = async () => {
  try {
    const response = await axios({
      method: "get",
      url: `${API_URL}/markets/indices/`,
    });

    stockData.value = Object.keys(response.data).map((key) => {
      const item = response.data[key];
      return {
        name: key,
        price: item.current_price
          ? item.current_price.toLocaleString("en-US", { minimumFractionDigits: 2 })
          : "-", // 값이 없으면 "-" 표시
        direction: item.percentage_change > 0 ? "up" : "down",
        change: item.percentage_change
          ? `${item.percentage_change.toFixed(2)}%`
          : "-", // 값이 없으면 "-" 표시
        status: item.status || "unknown", // 데이터 상태 (sample 또는 real)
      };
    });
  } catch (err) {
    console.error("증시 데이터를 가져오는 중 오류 발생:", err);
    console.log("대체 데이터가 표시됩니다: 모든 지수");
    // 샘플 데이터 표시
    stockData.value = [
      { name: "S&P 500", price: "4,500.23", direction: "up", change: "0.85%" },
      { name: "Nasdaq", price: "15,000.45", direction: "down", change: "-0.32%" },
      { name: "Dow Jones", price: "35,200.00", direction: "up", change: "1.20%" },
      { name: "Kospi", price: "2,500.00", direction: "down", change: "-0.50%" },
    ];
    
  }
};


// 날짜 포맷 함수
const formatDate = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}.${month}.${day}`;
};

// 텍스트 자르기 함수
const truncateText = (text, maxLength) => {
  if (!text) return "";
  return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
};

// 라우팅 함수
const goToPage = (page) => {
  router.push(`/${page}`);
};

// 컴포넌트 마운트 시 실행
onMounted(() => {
  currentDate.value = formatDate(new Date()); // 날짜 초기화
  fetchStockData();
  fetchNewsData();
});
</script>

<style scoped>
/* 메인 컨테이너 */
.home-page {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background-color: #FFFFFF; /* 흰색 배경 */
}

/* 캐러샐 섹션 */
.carousel-container {
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
}

/* 날짜, 증시, 금융 뉴스 박스 */
.info-box {
  background-color: #eceef1; /* 옅은 파란색 배경 */
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* 살짝 줄인 그림자 */
  display: flex;
  flex-direction: column;
  gap: 16px;
  border-left: 4px solid #6CA6CD; /* 강조 선 추가 */
}

.date {
  font-size: 18px;
  font-weight: bold;
  color: #191a1b; /* 파란색 텍스트 */
}

/* 구분선 */
.divider {
  height: 1px;
  background-color: #BFD7F2; /* 연한 파란색 구분선 */
  margin: 20px 0; /* 위아래 여백 */
}

/* 증시 리스트 */
.stock-list {
  list-style: none;
  padding: 0;
}

.stock-list li {
  display: flex;
  align-items: center;
  gap: 10px;
}

.change-icon {
  font-size: 14px;
  font-weight: bold;
}

.change-icon.up {
  color: #3A774E; /* 초록색 */
}

.change-icon.down {
  color: #D9534F; /* 빨간색 */
}

/* 뉴스 리스트 */
.news-list {
  list-style: none;
  padding: 0;
}

.news-item h4 {
  font-size: 16px;
  font-weight: bold;
  color: #000000; /* 뉴스 제목 파란색 */
}

.news-item p {
  font-size: 14px;
  color: #4D4D4D; /* 본문 기본 텍스트 */
}

.news-button {
  margin-top: 10px;
  padding: 12px;
  font-size: 14px;
  background-color: #1089FF; /* 파란색 버튼 */
  color: #FFFFFF; /* 흰색 텍스트 */
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.news-button:hover {
  background-color: #274B8F; /* Hover 시 짙은 파란색 */
}

/* 지도 박스 */
.map-box {
  background-color: #F2F6FC; /* 옅은 파란색 배경 */
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #6CA6CD; /* 강조 선 추가 */
}
</style>
