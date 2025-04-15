<template>
  <div class="compare-page">
    <h1>금융 상품 비교</h1>

    <!-- 검색 필드 -->
    <div class="search-container">
      <input
        v-model="searchTerm"
        class="search-input"
        type="text"
        placeholder="은행명 또는 상품명을 검색하세요..."
      />
    </div>

    <!-- 상품 탭 -->
    <div class="product-tab">
      <button
        :class="{ active: activeTab === 'deposit' }"
        @click="changeTab('deposit')"
      >
        예금
      </button>
      <button
        :class="{ active: activeTab === 'saving' }"
        @click="changeTab('saving')"
      >
        적금
      </button>
    </div>

    <!-- 선택된 상품 수 표시 -->
    <div class="selection-info">
      선택된 상품: {{ selectedProducts.length }} / {{ productStructure.maxSelection }}
    </div>

    <!-- 상품 목록 -->
    <div class="product-list">
      <div
        v-for="product in paginatedProducts"
        :key="product.fin_prdt_cd"
        class="product-card"
        @click="toggleSelection(product)"
        :class="{ selected: selectedProducts.includes(product) }"
      >
        <h5>{{ product.kor_co_nm }}</h5>
        <p>{{ product.fin_prdt_nm }}</p>
        <!-- <p>최고금리: {{ getMaxInterestRate(product) }}%</p> -->
      </div>
    </div>

    <!-- 페이지네이션 -->
    <div class="pagination">
      <button :disabled="currentPage === 1" @click="prevPage">이전</button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button :disabled="currentPage === totalPages" @click="nextPage">다음</button>
    </div>

    <!-- 비교 버튼 -->
    <button
      class="compare-button"
      :disabled="selectedProducts.length < 2"
      @click="showChart"
    >
      선택 상품 비교하기
    </button>

    <!-- 차트 -->
    <BarChart
      v-if="showingChart"
      :labels="labels"
      :datasets="chartDatasets"
      :title="chartTitle"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useProductStore } from "../stores/product";
import BarChart from "@/components/BarChart.vue";

// 상품 데이터 구조체 정의
const productStructure = {
  deposits: ref([]),
  savings: ref([]),
  selectedProducts: ref([]),
  maxSelection: 3
};

// Store 및 기본 상태 관리
const productStore = useProductStore();
const selectedProducts = ref([]);
const searchTerm = ref("");
const activeTab = ref("deposit");
const showingChart = ref(false);
const labels = ref([]);
const chartDatasets = ref([]);
const chartTitle = computed(() => 
  `${activeTab.value === 'deposit' ? '예금' : '적금'} 상품 금리 비교`
);

// 페이지네이션 관련
const currentPage = ref(1);
const itemsPerPage = 6;

// 최대 금리 계산 함수
const getMaxInterestRate = (product) => {
  if (!product.deposit_options || !product.deposit_options.length) return 0;
  return Math.max(...product.deposit_options.map(opt => Number(opt.intr_rate2))).toFixed(2);
};

// 필터링된 상품 목록
const filteredProducts = computed(() => {
  const products = activeTab.value === "deposit" ? 
    productStructure.deposits.value : 
    productStructure.savings.value;
  
  return products.filter(product => 
    product.fin_prdt_nm.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    product.kor_co_nm.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

// 페이지네이션된 상품 목록
const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredProducts.value.slice(start, start + itemsPerPage);
});

const totalPages = computed(() => 
  Math.ceil(filteredProducts.value.length / itemsPerPage)
);

// 페이지 이동 함수
const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};

// 탭 변경 함수
const changeTab = (tab) => {
  activeTab.value = tab;
  currentPage.value = 1;
  selectedProducts.value = [];
  showingChart.value = false;
};

// 상품 선택 토글 함수
const toggleSelection = (product) => {
  const index = selectedProducts.value.indexOf(product);
  if (index === -1) {
    if (selectedProducts.value.length >= productStructure.maxSelection) {
      alert(`최대 ${productStructure.maxSelection}개의 상품만 선택할 수 있습니다.`);
      return;
    }
    selectedProducts.value.push(product);
  } else {
    selectedProducts.value.splice(index, 1);
  }
};

// 차트 표시 함수
const showChart = () => {
  if (selectedProducts.value.length < 2) {
    alert('최소 2개 이상의 상품을 선택해주세요.');
    return;
  }

  let validProducts;
  if (activeTab.value === 'deposit') {
    // 예금 상품인 경우
    validProducts = selectedProducts.value.filter(
      product => product.deposit_options && product.deposit_options.length > 0
    );
  } else {
    // 적금 상품인 경우
    validProducts = selectedProducts.value.filter(
      product => product.saving_options && product.saving_options.length > 0
    );
  }

  if (!validProducts.length) {
    alert('선택된 상품의 금리 정보가 없습니다.');
    return;
  }

  // 기간별 금리 데이터 구성
  const periods = [...new Set(validProducts.flatMap(product => {
    const options = activeTab.value === 'deposit' ? 
      product.deposit_options : 
      product.saving_options;
    return options.map(option => option.save_trm);
  }))].sort((a, b) => Number(a) - Number(b));

  labels.value = periods.map(period => `${period}개월`);
  
  chartDatasets.value = validProducts.map((product, index) => {
    const options = activeTab.value === 'deposit' ? 
      product.deposit_options : 
      product.saving_options;
      
    return {
      label: `${product.kor_co_nm} - ${product.fin_prdt_nm}`,
      data: periods.map(period => {
        const option = options.find(opt => opt.save_trm === period);
        return option ? Number(option.intr_rate2) : 0;
      }),
      backgroundColor: `hsla(${index * 360 / validProducts.length}, 70%, 50%, 0.8)`,
      borderColor: `hsla(${index * 360 / validProducts.length}, 70%, 40%, 1)`,
      borderWidth: 1
    };
  });

  showingChart.value = true;
};

// 초기 데이터 로드
onMounted(async () => {
  await productStore.saveDeposits();
  await productStore.saveSavings();
  await productStore.fetchDeposits();
  await productStore.fetchSavings();
  productStructure.deposits.value = productStore.deposits;
  productStructure.savings.value = productStore.savings;
});
</script>

<style scoped>
.h1 {
  text-align: center;
}
/* 페이지 스타일 */
.compare-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 16px;
  background-color: #f8faff; /* 옅은 파란색 */
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 검색창 스타일 */
.search-container {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border: 2px solid #d0e6ff; /* 옅은 파란색 */
  border-radius: 8px;
  background-color: #ffffff; /* 흰색 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 탭 스타일 */
.product-tab {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.product-tab button {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  border-radius: 8px;
  background-color: #d6eaff; /* 옅은 파란색 */
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.product-tab button.active {
  background-color: #1089FF; /* 기준 파란색 */
  color: #ffffff;
  font-weight: bold;
}

.product-tab button:hover {
  background-color: #0d74cc; /* 짙은 파란색 */
}

/* 상품 카드 스타일 */
.product-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 2열 그리드 */
  gap: 10px;
}

.product-card {
  background-color: #ffffff; /* 흰색 */
  border: 1px solid #d0e6ff; /* 옅은 파란색 */
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s, background-color 0.3s;
}

.product-card.selected {
  background-color: #1089FF; /* 기준 파란색 */
  border-color: #0d74cc; /* 짙은 파란색 */
  color: #ffffff; /* 흰색 텍스트 */
  transform: scale(1.00);
}

/* 페이지네이션 */
.pagination {
  display: flex;
  justify-content: space-between;
  margin: 20px 0;
}

.pagination button {
  padding: 10px 20px;
  font-size: 14px;
  border: none;
  border-radius: 8px;
  background-color: #1089FF; /* 기준 파란색 */
  color: white;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.pagination button:disabled {
  background-color: #d0e6ff; /* 비활성화된 상태의 옅은 파란색 */
  color: #aaa;
  cursor: not-allowed;
}

/* 비교 버튼 */
.compare-button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border: none;
  border-radius: 8px;
  background-color: #1089FF; /* 기준 파란색 */
  color: white;
  margin-top: 20px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.compare-button:disabled {
  background-color: #d0e6ff; /* 비활성화된 상태의 옅은 파란색 */
  color: #aaa;
  cursor: not-allowed;
}
</style>
