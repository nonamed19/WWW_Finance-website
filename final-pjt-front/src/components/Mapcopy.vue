<template>
  <div class="map-container">
    <!-- 지도 -->
    <div id="map" class="map"></div>
    <!-- 근처 은행 찾기 버튼 -->
    <button class="find-bank-button" @click="goToNearBank">
      근처 은행 찾기
    </button>
  </div>
</template>


<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { loadKakaoMap } from "@/stores/map";

const router = useRouter(); // Vue Router 사용

const map = ref(null); // 지도 객체

const initializeMap = async () => {
  try {
    const kakao = await loadKakaoMap();

    // Kakao 지도 API 로드
    kakao.maps.load(() => {
      const mapContainer = document.getElementById("map");
      const mapOption = {
        center: new kakao.maps.LatLng(37.5665, 126.9780), // 서울 중심
        level: 3, // 확대 수준
      };

      map.value = new kakao.maps.Map(mapContainer, mapOption);
    });
  } catch (error) {
    console.error("지도 초기화 실패:", error);
  }
};

const goToNearBank = () => {
  router.push("/nearBank"); // /nearBank 페이지로 이동
};

const findNearbyBanks = () => {
  console.log("근처 은행 찾기 버튼 클릭");
};

onMounted(() => {
  initializeMap();
});
</script>



<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 400px;
  border-radius: 12px;
  overflow: hidden;
  background-color: #f0f0f0;
}

.map {
  width: 100%;
  height: 100%;
  border-radius: 12px;
}

/* 근처 은행 찾기 버튼 */
.find-bank-button {
  position: absolute;
  bottom: 16px;
  right: 16px;
  padding: 12px 20px;
  font-size: 14px;
  background-color: #3366CC;
  color: white;
  border: none;
  border-radius: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: background-color 0.3s;
  z-index: 1000; /* 맵 위로 버튼을 올림 */
}

.find-bank-button:hover {
  background-color: #274B8F;
}

</style>
