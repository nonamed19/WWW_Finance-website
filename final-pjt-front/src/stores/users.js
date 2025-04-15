import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import axios from 'axios';

export const useUserStore = defineStore('users', () => {
  const API_URL = 'http://127.0.0.1:8000';
  const router = useRouter();
  
  // 상태 관리
  const token = ref(localStorage.getItem('token') || null);
  const userInfo = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  // 계산된 속성
  const isLogin = computed(() => token.value !== null);

  // 사용자 정보 가져오기
  const getUserInfo = async function () {
    if (!token.value) return;
    
    isLoading.value = true;
    error.value = null;
  
    try {
      const response = await axios({
        method: 'get',
        url: `${API_URL}/accounts/user_info/`,
        headers: {
          Authorization: `Token ${token.value}`,
        },
      });
      
      // 응답 데이터를 가공하여 저장
      const userData = response.data.user_info; // email 포함
      userInfo.value = userData;
      localStorage.setItem('userInfo', JSON.stringify(userData));
      
      return userData;
    } catch (err) {
      console.error('사용자 정보 가져오기 실패:', err);
      error.value = err.response?.data || '사용자 정보를 가져오는데 실패했습니다.';
      if (err.response?.status === 401) {
        logOut();
      }
    } finally {
      isLoading.value = false;
    }
};
    
  // 로그인
  const logIn = async function (payload) {
    const { username, password } = payload;
    isLoading.value = true;
    error.value = null;
  
    try {
      const response = await axios({
        method: 'post',
        url: `${API_URL}/accounts/login/`,
        data: { username, password },
      });
  
      token.value = response.data.key;
      localStorage.setItem('token', response.data.key);
  
      await getUserInfo();
  
      // 기존 쿼리 값 사용
      const redirectPath = router.currentRoute.value.query.redirect || '/main';
      router.push(redirectPath);
  
    } catch (err) {
      console.error('로그인 실패:', err);
      error.value = err.response?.data || '로그인에 실패했습니다.';
    } finally {
      isLoading.value = false;
    }
  };
  
  // 로그아웃
  const logOut = async function () {
    if (!token.value) return;

    try {
      await axios({
        method: 'post',
        url: `${API_URL}/accounts/logout/`,
        headers: {
          Authorization: `Token ${token.value}`,
        },
      });
    } catch (err) {
      console.error('로그아웃 실패:', err);
    } finally {
      token.value = null;
      userInfo.value = null;
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      router.push({ name: 'Main' });
    }
  };

  // 회원 탈퇴
  const deleteAccount = async function () {
    if (!token.value) return;
  
    try {
      await axios({
        method: "delete",
        url: `${API_URL}/accounts/user_delete/`,
        headers: {
          Authorization: `Token ${token.value}`,
        },
      });
      // 성공적으로 탈퇴되면 로컬 저장소 초기화
      token.value = null;
      userInfo.value = null;
      localStorage.removeItem("token");
      localStorage.removeItem("userInfo");
    } catch (err) {
      console.error("회원 탈퇴 실패:", err);
      throw new Error("회원 탈퇴 중 문제가 발생했습니다.");
    }
  };  

  // 회원가입
  const signUp = async function (payload) {
    const { username, name, email, password1, password2 } = payload;
    isLoading.value = true;
    error.value = null;

    try {
      await axios({
        method: 'post',
        url: `${API_URL}/accounts/signup/`,
        data: {
          username,
          name,
          email,
          password1,
          password2,
        },
      });
      
      await logIn({ username, password: password1 });
      
    } catch (err) {
      console.error('회원가입 실패:', err);
      error.value = err.response?.data || '회원가입에 실패했습니다.';
    } finally {
      isLoading.value = false;
    }
  };

  const updateUserInfo = async (formData) => {
    if (!token.value) return;

    try {
      const response = await axios.patch(`${API_URL}/accounts/user_update/`, formData, {
        headers: {
          Authorization: `Token ${token.value}`,
          "Content-Type": "multipart/form-data",
        },
      });
      userInfo.value = response.data.updated_data;
      alert("회원 정보가 성공적으로 수정되었습니다.");
    } catch (err) {
      console.error("Failed to update user info:", err);
      alert("회원 정보 수정에 실패했습니다.");
    }
  };
    
  // 컴포넌트 마운트 시 자동 로그인 처리
  onMounted(() => {
    if (token.value) {
      getUserInfo();
    }
  });

  return {
    token,
    userInfo,
    isLogin,
    isLoading,
    error,
    getUserInfo,
    signUp,
    logIn,
    logOut,
    updateUserInfo,
    deleteAccount,
  };
});