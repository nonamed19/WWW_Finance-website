<template>
  <div v-if="userStore.isLogin" class="container">
    <header class="d-flex align-center mb-7">
      <RouterLink
        :to="{ name: 'myPage', params: { username: userStore.userInfo?.username }}"
        exact-active-class="active"
      >
        회원 정보 관리
      </RouterLink>
      <p>|</p>
      <div class="button-container">
      <RouterLink
        :to="{ name: 'userUpdate' }"
        class="edit-button"
      >
        회원 정보 수정
      </RouterLink>
      
      <button class="delete-button" @click="handleDeleteAccount">
        회원 탈퇴
      </button>
      </div>
    </header>

    <!-- MyPage 컴포넌트 -->
    <MyPage />

    <!-- 가입한 금융 상품 리스트 -->
    <section class="subscriptions">
      <h2>내가 가입한 금융 상품</h2>
      <ul v-if="subscriptions.length > 0">
        <li v-for="subscription in subscriptions" :key="subscription.id">
          {{ subscription.product_name }}z
          <button @click="cancelSubscription(subscription)">구독 취소</button>
        </li>
      </ul>
      <p v-else>가입한 금융 상품이 없습니다.</p>
    </section>
  </div>

  <div v-else class="loading-container">
    <div class="loading-message">
      <p>로그인이 필요한 서비스입니다</p>
      <RouterLink :to="{ name: 'login' }" class="login-link">로그인 하기</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useProductStore } from "@/stores/product";
import { useUserStore } from "@/stores/users";
import { useRouter } from "vue-router";
import MyPage from "@/components/MyPage.vue";

const userStore = useUserStore();
const productStore = useProductStore();
const router = useRouter();

const subscriptions = ref([]);

// Fetch 구독 리스트 및 프로필 정보
onMounted(async () => {
  if (userStore.isLogin) {
    await productStore.fetchSubscriptions();
    subscriptions.value = productStore.subscriptions;
  }
});

// 구독 취소 처리
const cancelSubscription = async (subscription) => {
  const response = await productStore.toggleSubscription(subscription);
  alert(response.message);
  subscriptions.value = productStore.subscriptions; // 갱신
};

// 회원 탈퇴 처리
const handleDeleteAccount = async () => {
  if (confirm("정말로 회원 탈퇴를 진행하시겠습니까? 이 작업은 되돌릴 수 없습니다.")) {
    try {
      await userStore.deleteAccount();
      alert("회원 탈퇴가 완료되었습니다.");
      router.push({ name: "Main" });
    } catch (error) {
      console.error("회원 탈퇴 실패:", error);
      alert("회원 탈퇴 중 문제가 발생했습니다. 다시 시도해주세요.");
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 큰 카드 스타일 추가 */
}

.subscriptions {
  margin-top: 2rem;
}

.subscriptions h2 {
  margin-bottom: 1rem;
}

button {
  margin-left: 1rem;
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #c0392b;
}

/* 회원 탈퇴 버튼 (텍스트 + 밑줄) */
.delete-button {
  border: none;
  background: none;
  margin-left: 70%;
  color: #e74c3c; /* 빨간색 */
  text-decoration: underline;
  white-space: nowrap;
  font-size: 14px;
  cursor: pointer;
}


.delete-button:hover {
  background-color: #a93226;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50vh;
}

.loading-message {
  text-align: center;
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading-message p {
  color: #666;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.login-link {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  background-color: #e4c089;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.login-link:hover {
  background-color: #d8b679;
}

header {
  gap: 10px;
  font-size: 17px;
}

header a {
  font-weight: 600;
  font-size: 20px;
  letter-spacing: -1px;
  color: #222;
  text-decoration: none;
  transition: font-size 0.2s ease, color 0.2s ease;
  white-space: nowrap; /* 텍스트 줄 바꿈 방지 */
}

header a:hover {
  font-size: 22px;
  color: #1089ff;
}

a.active {
  color: #5c5c4e;
}

/* 금융 상품 섹션 */
.subscriptions {
  width: 90%;
  margin-top: 2rem;
  background-color: #f9f9f9; /* 연한 회색 배경 */
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  justify-content: center;
  margin-left: 5%;
}

.subscriptions h2 {
  margin-bottom: 1rem;
  color: #333;
  font-size: 20px;
  font-weight: bold;
}

/* 금융 상품 리스트 */
.subscriptions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.subscriptions li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #ffffff; /* 흰색 배경 */
  border: 1px solid #ddd; /* 연한 회색 경계선 */
  border-radius: 8px;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* 부드러운 그림자 */
}

.subscriptions li:last-child {
  margin-bottom: 0;
}

.subscriptions li:hover {
  /* border-color: #1089ff; 파란색 테두리 강조 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 강조된 그림자 */
}

/* 구독 취소 버튼 */
.subscriptions button {
  padding: 10px 20px;
  border: none;
  border-radius: 15px;
  background-color: #3e6330; /* 파란색 */
  color: white;
  font-size: 12px;
  white-space: nowrap; /* 텍스트 줄 바꿈 방지 */
  text-align: center; /* 텍스트 중앙 정렬 */
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.subscriptions button:hover {
  background-color: #145150; /* 짙은 파란색 */
}

/* 빈 리스트 메시지 */
.subscriptions p {
  text-align: center;
  color: #666;
  font-size: 16px;
  margin: 0;
}
</style>
