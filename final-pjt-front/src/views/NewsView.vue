<template>
  <div class="news-page">
    <h1>경제 뉴스</h1>
    <div v-if="loading" class="loading">뉴스 데이터를 불러오는 중...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-else>
      <ul class="news-list">
        <li v-for="news in newsData" :key="news.id" class="news-item">
          <h3>{{ news.title }}</h3>
          <p>{{ news.description }}</p>
          <div class="news-meta">
            <span>{{ formatDate(news.pub_date) }}</span>
            <div class="news-links">
              <a :href="news.originallink" target="_blank" rel="noopener noreferrer">
                원문 보기
              </a>
              <a :href="news.link" target="_blank" rel="noopener noreferrer">
                네이버 뉴스
              </a>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useNewsStore } from "@/stores/news";

const { newsData, fetchNewsData, loading, error } = useNewsStore();

const formatDate = (dateString) => {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      weekday: 'long'
    }).format(date);
  } catch (error) {
    return dateString;
  }
};

onMounted(() => {
  fetchNewsData();
});
</script>


<style scoped>
/* 뉴스 페이지 전체 컨테이너 */
.news-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  background-color: #ffffff; /* 흰색 배경 */
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 부드러운 그림자 */
}

/* 페이지 제목 */
h1 {
  font-size: 28px;
  color: #0a3158; /* 기준 파란색 */
  text-align: center;
  margin-bottom: 20px;
  text-shadow: 1px 1px 2px rgba(16, 137, 255, 0.2); /* 부드러운 텍스트 그림자 */
}

/* 뉴스 리스트 */
.news-list {
  list-style: none;
  padding: 0;
}

/* 뉴스 카드 */
.news-item {
  padding: 20px;
  border: 1px solid #d0e6ff; /* 옅은 파란색 */
  border-radius: 12px;
  margin-bottom: 16px;
  background: linear-gradient(to bottom, #ffffff, #f8faff); /* 흰색에서 옅은 파란색 그라데이션 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

/* 뉴스 카드 Hover 효과 */
.news-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

/* 뉴스 제목 */
.news-item h3 {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
  text-shadow: 1px 1px 2px rgba(51, 51, 51, 0.2); /* 제목 강조 */
}

/* 뉴스 설명 */
.news-item p {
  font-size: 16px;
  color: #555;
  margin-bottom: 10px;
  line-height: 1.5;
}

/* 뉴스 메타 정보 */
.news-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #666;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #d0e6ff; /* 옅은 파란색 구분선 */
}

/* 링크 스타일 */
.news-links {
  display: flex;
  gap: 15px;
}

.news-links a {
  color: #ffffff; /* 링크 텍스트 흰색 */
  text-decoration: none;
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 6px;
  background-color: #1089FF; /* 파란색 버튼 */
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.news-links a:hover {
  background-color: #0D74CC; /* 짙은 파란색 */
  transform: scale(1.05);
  text-decoration: none;
}

/* 로딩 메시지 */
.loading {
  text-align: center;
  font-size: 18px;
  color: #666;
  margin: 50px 0;
}

/* 에러 메시지 */
.error {
  text-align: center;
  font-size: 18px;
  color: #FF4D4F; /* 강렬한 빨간색 */
  margin: 50px 0;
}
</style>
