<template>
  <v-app>
    <NavBar v-if="!isLoadingScreen" />
    <!-- 네비게이션 바 -->
    <div class="navbar-options" v-if="!isLoadingScreen">
      <span class="nav-link" @click="goToPage('productList')">상품목록</span>
      <span class="separator">|</span>
      <span class="nav-link" @click="goToPage('productcompare')">상품비교</span>
      <span class="separator">|</span>
      <span class="nav-link" @click="goToPage('recommendation')">상품추천</span>
      <span class="separator">|</span>
      <span class="nav-link" @click="goToPage('nearBank')">근처은행</span>
    </div>

    <!-- 콘텐츠 영역 -->
    <div class="centered-content">
      <router-view />
      <div class="content-padding"></div>
    </div>

    <!-- 챗봇 모달 -->
    <chatbotModal v-if="!isLoadingScreen" />

    <!-- 원격 컨트롤 -->
    <Remote v-if="!isLoadingScreen" />
  </v-app>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import NavBar from "./components/NavBar.vue";
import Remote from "./components/Remote.vue";
import chatbotModal from "./components/chatbotModal.vue";

// 상태 관리
const route = useRoute();
const router = useRouter();
const isLoadingScreen = ref(false);

// 특정 경로에서 로딩 화면 여부 설정
watch(
  () => route.name,
  (newRouteName) => {
    isLoadingScreen.value = newRouteName === "LoadingScreen";
  },
  { immediate: true }
);

// 페이지 이동 함수
const goToPage = (page) => {
  router.push(`/${page}`);
};
</script>

<style scoped>
/* 글로벌 스타일 */
html, body {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  max-width: 600px;
  width: 100%;
  height: 100%;
  font-family: 'Francois One', sans-serif; /* 글로벌 폰트 */
}

/* v-app 컨테이너 */
.v-app {
  display: flex;
  flex-direction: column; /* 위에서 아래로 정렬 */
  align-items: center; /* 수평 중앙 정렬 */
  min-height: 100vh; /* 화면 전체 높이 */
  background-color: #f5f5f5; /* 연한 회색 배경 */
  overflow-x: hidden;
}

/* 네비게이션 바 */
.navbar-options {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  position: sticky;
  top: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px; /* 옵션 간 간격 */
  padding: 15px 0;
  background-color: #FFFFFF; /* 흰색 배경 */
  border-bottom: 1px solid #E0E0E0; /* 연한 회색 구분선 */
  z-index: 999;
}

.nav-link {
  font-size: 16px;
  font-weight: bold;
  color: #4D4D4D; /* 검은색 텍스트 */
  cursor: pointer;
  text-decoration: none; /* 밑줄 제거 */
}

.nav-link:hover {
  color: #3366CC; /* Hover 시 파란색 */
}

/* | 기호 스타일 */
.separator {
  color: #BFBFBF; /* 회색 구분선 */
  font-size: 16px;
}

/* 콘텐츠 컨테이너 */
.centered-content {
  width: 100%;
  max-width: 600px;
  margin: 0 auto; /* 가운데 정렬 */
  padding: 16px;
  box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
  background-color: white; /* 흰색 배경 */
  border-radius: 10px; /* 모서리를 둥글게 설정 */
  flex-grow: 1; /* 남는 공간 채우기 */
}

.content-padding {
  height: 100px; /* 추가 여백 높이 */
  background-color: transparent; /* 투명 배경 */
}

@media (max-width: 600px) {
  .centered-content {
    width: 100%;
    max-width: 100%;
    margin: 0;
    border-radius: 0;
  }
}

/* 푸터 */
footer {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background-color: #424530; /* 어두운 색상 */
  color: #FFEFCD; /* 텍스트 밝은 색상 */
  text-align: center;
  line-height: 60px;
  z-index: 10;
}
</style>
