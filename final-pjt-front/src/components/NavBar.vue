<template>
  <div class="navbar-container">
    <!-- 상단 네비게이션 -->
    <div class="navbar-top">
      <div class="navbar-logo img" @click="goToPage('Main')">
        <img src="@/assets/mainlogo.png" alt="mainlogo">
      </div>
      <div class="navbar-user-actions">
        <template v-if="isLoggedIn">
          <span class="action-link" @click="logout">로그아웃</span>
        </template>
        <template v-else>
          <span class="action-link" @click="goToPage('login')">로그인</span>
          <span class="action-link" @click="goToPage('signup')">회원가입</span>
        </template>
        <RouterLink
          to="/mypage"
          exact-active-class="active"
          class="custom-link"
        >
          <v-icon class="custom-icon" color="black">mdi-account</v-icon>
        </RouterLink>
      </div>
    </div>



    <!-- 하단 네비게이션 -->
    <div class="bottom-navbar">
      <!-- 메뉴 버튼 -->
      <button class="bottom-btn" @click="openPopup">
        <v-icon>mdi-menu</v-icon>
      </button>

      <!-- 뒤로 가기 버튼 -->
      <button class="bottom-btn" @click="router.back">
        <v-icon>mdi-arrow-left</v-icon>
      </button>
    </div>
      <!-- 챗봇 버튼 -->
    <button class="chatbot-button" @click="chatbotStore.openModal">
      <v-icon>mdi-robot</v-icon>
    </button>

  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/users";
import { useChatbotStore } from "@/stores/chatbot";

const chatbotStore = useChatbotStore();

const openChatbot = () => {
  chatbotStore.openModal();
};

const userStore = useUserStore();
const router = useRouter();
const chatbotModal = ref(null);

const isLoggedIn = computed(() => userStore.isLogin);

const logout = () => {
  userStore.logOut();
};

const goToPage = (page) => {
  router.push(`/${page}`);
};

const openPopup = () => {
  router.push({ name: "PopupMenu" });
};

</script>

<style>
/* 전체 컨테이너 */
.navbar-container {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  background-color: #FFFFFF; /* 흰색 배경 */
  color: #4D4D4D; /* 텍스트 기본 검은색 */
  z-index: 1000;
}

/* 상단 네비게이션 */
.navbar-top {
  max-width: 600px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: #FFFFFF; /* 흰색 배경 */
  border-bottom: 1px solid #E0E0E0; /* 연한 회색 구분선 */
}

.navbar-logo img {
  height: 32px; /* 로고 높이를 22px에 맞춤 */
  object-fit: contain; /* 로고 비율 유지 */
  cursor: pointer; /* 클릭 가능 */
  justify-content: baseline;
}
.navbar-user-actions {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.action-link {
  font-size: 14px; /* 글씨 크기 축소 */
  font-weight: bold; /* 두껍게 설정 */
  color: #4D4D4D; /* 기본 텍스트 색 */
  cursor: pointer;
}

.action-link:hover {
  color: #3366CC; /* Hover 시 파란색 */
}

/* 하단 네비게이션 옵션 */
.navbar-options {
  position: sticky;
  top: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px; /* 옵션 간 간격 */
  padding: 15px 0;
  background-color: #FFFFFF; /* 흰색 배경 */
  border-top: 1px solid #E0E0E0; /* 연한 회색 구분선 */
  border-bottom: 1px solid #E0E0E0; /* 연한 회색 구분선 */
  z-index: 999; /* Sticky 네비게이션 위로 */
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

/* 하단 네비게이션 버튼 */
.bottom-navbar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 600px;
  background-color: #F2F2F2; /* 밝은 흰색 */
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  padding: 10px 0;
  box-shadow: 0px -2px 5px rgba(0, 0, 0, 0.1); /* 살짝 강조 */
  z-index: 1002;
  }

.bottom-btn {
  background-color: transparent;
  color: #4D4D4D; /* 기본 텍스트 */
  border: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
}

.bottom-btn:hover {
  text-decoration: underline;
  color: #3366CC; /* Hover 시 파란색 */
}

/* 챗봇 버튼 */
.chatbot-button {
  position: fixed; /* 네비게이션 바와 독립적으로 고정 */
  bottom: 5px; /* 화면 하단 기준 위치 */
  left: 50%; /* 화면 중앙에 위치 */
  transform: translateX(-50%); /* X축 중앙 정렬 */
  background-color: #3366CC; /* 파란색 버튼 */
  color: #FFFFFF; /* 텍스트 흰색 */
  border: none;
  border-radius: 50%;
  width: 64px;
  height: 64px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3); /* 버튼 그림자 */
  cursor: pointer;
  z-index: 1003;
}

.chatbot-button:hover {
  background-color: #274B8F; /* Hover 시 짙은 파란색 */
}
</style>
