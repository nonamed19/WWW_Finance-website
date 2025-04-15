import axios from "axios";
import { ref } from "vue";

const API_URL = "http://127.0.0.1:8000";

export const useNewsStore = () => {
  const newsData = ref([]); // 전체 뉴스 데이터
  const limitedNews = ref([]); // 홈에서 표시할 최신 뉴스 요약
  const loading = ref(false); // 로딩 상태
  const error = ref(null); // 에러 상태

  // 뉴스 데이터 로드
  const fetchNewsData = async () => {
    console.log("뉴스 데이터 로드 시작...");
    loading.value = true;
    error.value = null;

    try {
      const response = await axios({
        method: "get",
        url: `${API_URL}/economics/news-get-data/`,
      });

      if (response.data && Array.isArray(response.data)) {
        console.log("뉴스 데이터 로드 성공:", response.data);
        newsData.value = response.data; // 전체 데이터 저장
        limitedNews.value = response.data.slice(0, 3); // 최신 뉴스 3개만 저장
      } else {
        console.warn("API 응답 데이터가 예상치와 다릅니다:", response.data);
        newsData.value = [];
        limitedNews.value = [];
      }
    } catch (err) {
      console.error("뉴스 데이터 가져오기 실패:", err);
      error.value = "뉴스 데이터를 가져오는 데 실패했습니다.";
      newsData.value = [];
      limitedNews.value = [];
    } finally {
      loading.value = false;
      console.log("뉴스 데이터 로드 완료");
    }
  };

  return {
    newsData,
    limitedNews,
    loading,
    error,
    fetchNewsData,
  };
};
