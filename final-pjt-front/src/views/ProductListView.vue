<template>
  <div class="product-list-container">
    <!-- 탭 구성 -->
    <div class="tabs">
      <button
        class="tab"
        :class="{ active: activeTab === 'deposit' }"
        @click="activeTab = 'deposit'"
      >
        예금
      </button>
      <button
        class="tab"
        :class="{ active: activeTab === 'saving' }"
        @click="activeTab = 'saving'"
      >
        적금
      </button>
    </div>

    <!-- 상품 목록 -->
    <div>
      <div
        v-for="product in paginatedProducts"
        :key="product.fin_prdt_cd"
        class="product-card"
      >
        <div class="product-body">
          <h3 class="product-name">{{ product.fin_prdt_nm }}</h3>
          <p class="product-period">
            가입기간: {{ extractJoinPeriod(product.etc_note) }}
          </p>
        </div>
        <div class="button-group">
        <button class="detail-button" @click="showDetail(product)">
          상세 보기
        </button>
        <button
          class="subscribe-button" 
          :class="{ 'subscribed-yellow': isSubscribed(product) }"
          @click="toggleSubscription(product)"
        >
          {{ isSubscribed(product) ? "구독 취소" : "가입하기" }}
        </button>
      </div>
      </div>
    </div>

    <!-- 페이지네이션 -->
    <div class="pagination">
      <button
        v-for="page in totalPages"
        :key="page"
        :class="{ active: currentPage === page }"
        @click="currentPage = page"
      >
        {{ page }}
      </button>
    </div>

    <!-- 상세 페이지 팝업 -->
    <div v-if="selectedProduct" class="popup-overlay" @click.self="closeDetail">
      <div class="popup-content">
        <h2>{{ selectedProduct.fin_prdt_nm }}</h2>
        <p><strong>상품 형태:</strong> {{ selectedProduct.join_way }}</p>
        <p><strong>가입 조건:</strong> {{ selectedProduct.join_member }}</p>
        <p><strong>특이 사항:</strong> {{ selectedProduct.spcl_cnd }}</p>
        <p><strong>만기 이율:</strong> {{ selectedProduct.mtrt_int }}</p>
        <p><strong>기타 사항:</strong> {{ selectedProduct.etc_note }}</p>
        <button class="close-button" @click="closeDetail">닫기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useProductStore } from "../stores/product";
import { useUserStore } from "../stores/users";

const productStore = useProductStore();
const userStore = useUserStore();

onMounted(async () => {
  await productStore.saveDeposits();
  await productStore.saveSavings();
  await productStore.fetchDeposits();
  await productStore.fetchSavings();
  await productStore.fetchSubscriptions(); // 구독 정보 가져오기
});

const activeTab = ref("deposit");
const currentPage = ref(1);
const itemsPerPage = 10;

const products = computed(() =>
  activeTab.value === "deposit"
    ? productStore.deposits
    : productStore.savings
);

const totalPages = computed(() =>
  Math.ceil(products.value.length / itemsPerPage)
);
const paginatedProducts = computed(() =>
  products.value.slice(
    (currentPage.value - 1) * itemsPerPage,
    currentPage.value * itemsPerPage
  )
);

const selectedProduct = ref(null);
const showDetail = (product) => {
  selectedProduct.value = product;
};

const closeDetail = () => {
  selectedProduct.value = null;
};

const toggleSubscription = async (product) => {
  if (!userStore.isLogin) {
    alert("로그인이 필요합니다.");
    return;
  }

  const response = await productStore.toggleSubscription(product);
  // alert(response.message);
};

const isSubscribed = (product) =>
  productStore.subscriptions.some(
    (subscription) => subscription.product_id === product.fin_prdt_cd
  );

const extractJoinPeriod = (note) => {
  const match = note?.match(/가입기간: (.+?)\n/);
  return match ? match[1] : "정보 없음";
};
</script>

<style scoped>
.product-list-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1000px;
  margin: 0 auto;
}

/* 카드형 레이아웃 */
.product-card {
  display: flex;
  justify-content: space-between; /* 시작 부분과 버튼 부분 분리 */
  align-items: center;
  border: 1px solid #E0E0E0; /* 옅은 회색 경계 */
  border-radius: 12px;
  padding: 16px;
  background-color: #FFFFFF; /* 흰색 배경 */
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 부드러운 그림자 */
}

.product-header {
  font-size: 14px;
  font-weight: bold;
  color: #333333; /* 검은색 텍스트 */
}

.product-body {
  font-size: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: #333333; /* 검은색 텍스트 */
}

.product-name {
  font-weight: bold;
}

.button-group {
  display: flex;
  justify-content: flex-end; /* 오른쪽 정렬 */
  gap: 4px; /* 버튼 간 간격 */
}

.detail-button {
  background-color: #1089FF; /* 기준 파란색 */
  color: #FFFFFF;
  border: none;
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.detail-button:hover {
  background-color: #0D74CC; /* Hover 짙은 파란색 */
}

.subscribe-button {
  background-color: #FFFFFF; /* 흰색 배경 */
  color: #1089FF;
  border: 2px solid #1089FF; /* 파란색 테두리 */
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
}

.subscribe-button:hover {
  background-color: #1089FF;
  color: #FFFFFF;
}

/* 구독 취소 상태 - 노란 계열 */
.subscribe-button.subscribed-yellow {
  background-color: #FFFDE7; /* 연한 노란 배경 */
  color: #FFC107; /* 노란색 텍스트 */
  border: 2px solid #FFC107; /* 노란색 테두리 */
}

.subscribe-button.subscribed-yellow:hover {
  background-color: #FFC107;
  color: #FFFFFF;
}

/* 탭 스타일 */
.tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
  gap: 8px;
}
.tab {
  padding: 10px 20px;
  border: none;
  cursor: pointer;
  font-size: 16px;
  background-color: #F2F2F2;
  border-radius: 8px;
  transition: background-color 0.2s;
}
.tab.active {
  background-color: #1089FF;
  color: #FFFFFF;
}

/* 페이지네이션 스타일 */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 16px;
  gap: 8px;
}
.pagination button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #F2F2F2;
  transition: background-color 0.2s;
}
.pagination button.active {
  background-color: #1089FF;
  color: #FFFFFF;
}

/* 팝업 스타일 */
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.popup-content {
  background-color: #FFFFFF;
  padding: 24px;
  border-radius: 12px;
  max-width: 90%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.popup-content h2 {
  font-size: 20px;
  font-weight: bold;
  color: #2b2d2f; /* 제목 색상 */
  margin-bottom: 16px;
  text-align: center;
}

.popup-content p {
  font-size: 14px;
  color: #333333;
  margin: 4px 0;
  line-height: 1.5;
}
</style>
