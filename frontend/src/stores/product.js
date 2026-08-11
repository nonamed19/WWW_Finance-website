import { ref } from "vue";
import { defineStore } from "pinia";
import axios from "axios";

// Django API URL
const API_URL = "http://127.0.0.1:8000";

// Axios 인스턴스 생성
const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Axios 요청 인터셉터 추가 (토큰이 필요한 경우)
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Pinia Store
export const useProductStore = defineStore("product", () => {
  // 상태 관리
  const deposits = ref([]);
  const savings = ref([]);
  const selectedProduct = ref(null);
  const errorMessage = ref("");
  const subscriptions = ref([]); // 사용자가 가입한 상품 목록

  // 에러 핸들러
  const handleError = (err) => {
    const message = err.response?.data || err.message || "알 수 없는 오류";
    errorMessage.value = message;
    console.error(message);
  };

  // 상태 업데이트 헬퍼
  const updateState = (stateRef, data) => {
    stateRef.value = data;
  };

  // 예금 및 적금 데이터 저장
  const saveDeposits = async () => {
    try {
      await axiosInstance.get("/bankings/deposit-fetch-data/");
      console.log("예금 데이터가 서버에 저장되었습니다.");
    } catch (err) {
      handleError(err);
    }
  };

  const saveSavings = async () => {
    try {
      await axiosInstance.get("/bankings/saving-fetch-data/");
      console.log("적금 데이터가 서버에 저장되었습니다.");
    } catch (err) {
      handleError(err);
    }
  };

  // 예금 및 적금 데이터 가져오기
  const fetchDeposits = async () => {
    try {
      const response = await axiosInstance.get("/bankings/deposit-get-products/");
      updateState(deposits, response.data);
    } catch (err) {
      handleError(err);
      updateState(deposits, []);
    }
  };

  const fetchSavings = async () => {
    try {
      const response = await axiosInstance.get("/bankings/saving-get-products/");
      updateState(savings, response.data);
    } catch (err) {
      handleError(err);
      updateState(savings, []);
    }
  };

  // ID로 특정 상품 정보 가져오기
  const fetchProductById = async (id, type) => {
    if (!id || !type) {
      console.error("유효하지 않은 상품 ID 또는 타입:", { id, type });
      selectedProduct.value = null;
      return;
    }

    const endpoint =
      type === "deposit"
        ? `/bankings/deposit-get-products/${id}/`
        : `/bankings/saving-get-products/${id}/`;

    try {
      const response = await axiosInstance.get(endpoint);
      updateState(selectedProduct, response.data);
    } catch (err) {
      handleError(err);
      updateState(selectedProduct, null);
    }
  };

  // 구독 목록 가져오기
  const fetchSubscriptions = async () => {
    try {
      const response = await axiosInstance.get("/subscriptions/my-subscriptions/");
      updateState(subscriptions, response.data);
    } catch (err) {
      handleError(err);
    }
  };

  // 구독/취소 요청
  const toggleSubscription = async (product) => {
    try {
      const response = await axiosInstance.post("/subscriptions/subscribe/", {
        product_id: product.fin_prdt_cd || product.product_id,
        product_name: product.fin_prdt_nm || product.product_name,
      });

      // 구독 목록 갱신
      await fetchSubscriptions();
      return response.data;
    } catch (err) {
      handleError(err);
      alert("요청 처리에 실패했습니다.");
    }
  };

  return {
    deposits,
    savings,
    selectedProduct,
    subscriptions,
    errorMessage,
    saveDeposits,
    saveSavings,
    fetchDeposits,
    fetchSavings,
    fetchProductById,
    fetchSubscriptions,
    toggleSubscription,
  };
});
