<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useUserStore } from '@/stores/users';
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/accounts/user_info/";
const userFields = ref(null);
const userStore = useUserStore();

// 금액 포맷팅 함수
const formatCurrency = (value) => {
  if (value === null || value === undefined) return '미입력';
  return new Intl.NumberFormat('ko-KR', { 
    style: 'currency', 
    currency: 'KRW',
    maximumFractionDigits: 0 
  }).format(value);
};

// 기간 포맷팅 함수
const formatPeriod = (months) => {
  if (!months) return '미입력';
  return `${months}개월`;
};

// 사용자 정보 가져오기
const fetchUserFields = async () => {
  await userStore.getUserInfo();
  if (userStore.userInfo) {
    userFields.value = { ...userStore.userInfo };
  }
};

// 프로필 이미지 URL을 동적으로 계산
const profileImageUrl = computed(() => {
  if (userStore.userInfo?.profile_image) {
    return userStore.userInfo.profile_image;
  }
  return null;
});

// 사용자 정보가 변경될 때마다 userFields 업데이트
watch(() => userStore.userInfo, (newUserInfo) => {
  if (newUserInfo) {
    userFields.value = { ...newUserInfo };
  }
}, { deep: true });

// 이미지 로드 실패 시 기본 이미지로 대체
const handleImageError = (e) => {
  e.target.src = '/default-profile.png';
};

// 이니셜 가져오기 함수
const getInitials = (name) => {
  if (!name) return '?';
  return name.charAt(0).toUpperCase();
};

onMounted(() => {
  fetchUserFields();
});
</script>

<template>
  <div class="profile-container">
    <!-- 프로필 헤더 -->
    <div class="profile-header" v-if="userFields">
      <div class="profile-image">
        <template v-if="profileImageUrl">
          <img 
            :src="profileImageUrl"
            :alt="`${userFields.name || userFields.username}의 프로필`"
            @error="handleImageError"
          />
        </template>
        <div v-else class="no-image">
          <span>{{ getInitials(userFields.name || userFields.username) }}</span>
        </div>
      </div>
      <h1 class="profile-title">{{ userFields.name || userFields.username }}님의 프로필</h1>
    </div>

    <!-- 사용자 정보 -->
    <div v-if="userFields" class="info-sections">
      <!-- 기본 정보 -->
      <section class="info-section">
        <h2>기본 정보</h2>
        <div class="info-content">
          <div class="info-item">
            <span class="label">아이디</span>
            <span class="value">{{ userFields.username }}</span>
          </div>
          <div class="info-item">
            <span class="label">이메일</span>
            <span class="value">{{ userFields.email }}</span>
          </div>
          <div class="info-item">
            <span class="label">닉네임</span>
            <span class="value">{{ userFields.name || '미입력' }}</span>
          </div>
          <div class="info-item">
            <span class="label">나이</span>
            <span class="value">{{ userFields.age ? `${userFields.age}세` : '미입력' }}</span>
          </div>
        </div>
      </section>

      <!-- 자산 정보 -->
      <section class="info-section">
        <h2>자산 정보</h2>
        <div class="info-content">
          <div class="info-item">
            <span class="label">현재 자산</span>
            <span class="value">{{ formatCurrency(userFields.money) }}</span>
          </div>
          <div class="info-item">
            <span class="label">연봉</span>
            <span class="value">{{ formatCurrency(userFields.salary) }}</span>
          </div>
        </div>
      </section>

      <!-- 금융 상품 희망 정보 -->
      <section class="info-section">
        <h2>예금 희망 정보</h2>
        <div class="info-content">
          <div class="info-item">
            <span class="label">희망 금액</span>
            <span class="value">{{ formatCurrency(userFields.desire_amount_deposit) }}</span>
          </div>
          <div class="info-item">
            <span class="label">희망 기간</span>
            <span class="value">{{ formatPeriod(userFields.deposit_period) }}</span>
          </div>
        </div>
      </section>

      <section class="info-section">
        <h2>적금 희망 정보</h2>
        <div class="info-content">
          <div class="info-item">
            <span class="label">월 희망 금액</span>
            <span class="value">{{ formatCurrency(userFields.desire_amount_saving) }}</span>
          </div>
          <div class="info-item">
            <span class="label">희망 기간</span>
            <span class="value">{{ formatPeriod(userFields.saving_period) }}</span>
          </div>
        </div>
      </section>
    </div>

    <!-- 로딩 상태 -->
    <div v-else class="loading">
      사용자 정보를 불러오는 중입니다...
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  max-width: 800px;
  /* margin: 0 auto; */
  padding: 20px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.profile-image {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #f5f5f5;
}

.profile-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.info-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.info-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.info-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.label {
  font-size: 14px;
  color: #666;
}

.value {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

@media (max-width: 600px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }

  .info-content {
    grid-template-columns: 1fr;
  }
}

.profile-image {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #1089ff;
  background-color: #f5f5f5;
}

.profile-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8feff;
  color: #1089ff;
  font-size: 2rem;
  font-weight: bold;
}
</style>