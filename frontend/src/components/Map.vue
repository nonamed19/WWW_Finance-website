<template>
  <div class="map-component">
    <div class="controls">
      <label>
        도/광역시:
        <select v-model="selectedProvince" @change="updateCities">
          <option disabled value="">도/광역시 선택</option>
          <option v-for="info in mapStore.infos" :key="info.id" :value="info.prov">
            {{ info.prov }}
          </option>
        </select>
      </label>

      <label>
        도시:
        <select v-model="selectedCity" :disabled="!selectedProvince">
          <option disabled value="">도시 선택</option>
          <option v-for="city in availableCities" :key="city" :value="city">
            {{ city }}
          </option>
        </select>
      </label>

      <label>
        은행:
        <select v-model="selectedBank">
          <option disabled value="">은행 선택</option>
          <option v-for="bank in mapStore.banks" :key="bank" :value="bank">
            {{ bank }}
          </option>
        </select>
      </label>

      <button class="search-btn" @click="searchOnMap">검색</button>
    </div>

    <div id="mapContainer" class="map"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useMapStore } from "@/stores/map";
import { loadKakaoMap } from "@/stores/map";

// Kakao 지도 객체와 관련된 상태
const map = ref<any>(null);
const markers = ref<any[]>([]);
const infowindow = ref<any>(null);

// Pinia 상태
const mapStore = useMapStore();
const selectedProvince = ref("");
const selectedCity = ref("");
const selectedBank = ref("");

// 선택한 도/광역시에 따른 도시 목록 계산
const availableCities = computed(() => {
  const selectedInfo = mapStore.infos.find((info) => info.prov === selectedProvince.value);
  return selectedInfo ? selectedInfo.city : [];
});

// 지도 초기화
const initializeMap = async () => {
  try {
    const kakao = await loadKakaoMap();
    kakao.maps.load(() => {
      const mapContainer = document.getElementById("mapContainer");
      const mapOption = {
        center: new kakao.maps.LatLng(37.566826, 126.9786567), // 서울 중심
        level: 3,
      };

      map.value = new kakao.maps.Map(mapContainer, mapOption);
      infowindow.value = new kakao.maps.InfoWindow({ zIndex: 1 });
    });
  } catch (error) {
    console.error("지도 초기화 실패:", error);
  }
};

// 검색 기능
const searchOnMap = () => {
  if (!selectedProvince.value || !selectedCity.value || !selectedBank.value) {
    alert("모든 항목을 선택해주세요.");
    return;
  }

  const keyword = `${selectedProvince.value} ${selectedCity.value} ${selectedBank.value}`;
  performSearch(keyword);
};

// Kakao Places API로 장소 검색
const performSearch = (keyword: string) => {
  const kakao = (window as any).kakao;
  const ps = new kakao.maps.services.Places();

  ps.keywordSearch(keyword, (data, status) => {
    if (status === kakao.maps.services.Status.OK) {
      displayMarkers(data);

      // 첫 번째 결과를 중심으로 지도 이동
      if (data.length > 0) {
        const firstPlace = data[0];
        map.value.setCenter(new kakao.maps.LatLng(firstPlace.y, firstPlace.x));
      }
    } else {
      alert("검색 결과가 없습니다.");
    }
  });
};

// 마커 표시
const displayMarkers = (places: any[]) => {
  const kakao = (window as any).kakao;

  // 기존 마커 제거
  markers.value.forEach((marker) => marker.setMap(null));
  markers.value = [];

  places.forEach((place) => {
    const marker = new kakao.maps.Marker({
      map: map.value,
      position: new kakao.maps.LatLng(place.y, place.x),
    });

    kakao.maps.event.addListener(marker, "click", () => {
    infowindow.value.setContent(`
      <div style="font-size:14px; font-family:Arial, sans-serif; color:#333; line-height:1.6;">
        <div style="padding:15px; background-color:#ffffff; border:1px solid #d0e6ff; border-radius:10px; box-shadow:0 4px 8px rgba(0, 0, 0, 0.1); max-width:300px;">
          <strong style="font-size:16px; font-weight:bold; color:#1089FF; margin-bottom:8px; display:block;">
            ${place.place_name}
          </strong>
          <div style="margin-bottom:10px;">
            <span><strong>도로명 주소:</strong> ${place.road_address_name || "정보 없음"}</span><br>
            <span><strong>지번 주소:</strong> ${place.address_name || "정보 없음"}</span><br>
          </div>
          <div style="margin-bottom:8px;">
            <strong>전화번호:</strong> ${place.phone || "정보 없음"}
          </div>
          <div>
            <a href="${place.place_url}" target="_blank" style="color:#0d74cc; text-decoration:none; font-weight:bold; transition:color 0.3s ease;">
              자세히 보기
            </a>
          </div>
        </div>
      </div>
    `);
      infowindow.value.open(map.value, marker);
    });

    markers.value.push(marker);
  });
};

// 도시 목록 초기화
const updateCities = () => {
  selectedCity.value = "";
};

// 컴포넌트 마운트 시 지도 초기화
onMounted(() => {
  initializeMap();
});
</script>

<style scoped>
.map-component {
  max-width: 700px; /* 컨테이너 너비 확장 */
  margin: 20px auto;
  margin-top: 0px;
  font-family: "Arial", sans-serif;
  background: #ffffff; /* 흰색 배경 */
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 컨트롤 박스 */
.controls {
  display: flex;
  flex-wrap: wrap; /* 반응형 배치 */
  gap: 20px;
  margin-bottom: 20px;
  justify-content: space-between; /* 버튼 및 드롭다운 정렬 */
}

.controls label {
  display: flex;
  flex-direction: column;
  font-size: 14px;
  color: #333;
  flex: 1 1 calc(33% - 20px); /* 각 컨트롤은 1/3 너비 */
  min-width: 120px; /* 최소 너비 */
}

.controls select {
  padding: 10px;
  font-size: 14px;
  border: 1px solid #d0e6ff; /* 옅은 파란색 테두리 */
  border-radius: 8px;
  background-color: #f8faff; /* 옅은 파란색 배경 */
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1); /* 안쪽 그림자 */
  transition: border-color 0.3s ease;
}

.controls select:focus {
  border-color: #1089FF; /* 기준 파란색 포커스 */
  outline: none;
}

.search-btn {
  background: linear-gradient(135deg, #1089FF, #0D74CC); /* 파란색 그라데이션 */
  color: white;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  flex: 1 1 100%; /* 버튼은 한 줄 전체 */
  transition: transform 0.3s, box-shadow 0.3s;
}

.search-btn:hover {
  background: linear-gradient(135deg, #0D74CC, #085AA1);
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* 지도 컨테이너 */
.map {
  width: 100%;
  height: 400px;
  border: 2px solid #d0e6ff; /* 옅은 파란색 테두리 */
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  background: url('/path/to/placeholder-image.png') center center no-repeat;
  background-size: cover; /* 기본 이미지 커버 */
  overflow: hidden;
  position: relative;
}

.map:after {
  content: "로딩 중..."; /* 지도 로딩 시 표시 */
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #666;
  font-size: 1.2rem;
  text-align: center;
}
</style>
