<template>
  <div v-if="userStore.isLogin" class="update-page">
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

    <div v-if="loading" class="loading">
      데이터를 불러오는 중...
    </div>
    <form v-else @submit.prevent="handleSubmit" class="update-form">
      <!-- 프로필 이미지 섹션 -->
      <div class="profile-image-section">
        <div class="current-image">
          <template v-if="previewImage || userStore.userInfo?.profile_image">
            <img 
              :src="previewImage || userStore.userInfo.profile_image"
              :alt="userStore.userInfo?.username"
              @error="handleImageError"
            />
          </template>
          <div v-else class="no-image">
            <span>{{ getInitials(userStore.userInfo?.name || userStore.userInfo?.username) }}</span>
          </div>
        </div>
        <div class="image-upload">
          <label for="profile-image" class="upload-label">
            프로필 이미지 변경
          </label>
          <input
            type="file"
            id="profile-image"
            accept="image/*"
            @change="handleImageChange"
            class="file-input"
          />
        </div>
        <p class="image-help-text" v-if="selectedFile">
          선택된 파일: {{ selectedFile.name }}
        </p>
      </div>

      <!-- 기본 정보 섹션 -->
      <div class="form-section">
        <h3>기본 정보</h3>
        <div class="form-group">
          <label for="name">닉네임</label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            class="form-input"
            placeholder="닉네임을 입력하세요"
          />
        </div>
        <div class="form-group">
          <label for="age">나이</label>
          <input
            id="age"
            v-model.number="formData.age"
            type="number"
            class="form-input"
            placeholder="나이를 입력하세요"
          />
        </div>
      </div>

      <!-- 자산 정보 섹션 -->
      <div class="form-section">
        <h3>자산 정보</h3>
        <div class="form-group">
          <label for="money">현재 자산</label>
          <input
            id="money"
            v-model.number="formData.money"
            type="number"
            class="form-input"
            placeholder="현재 자산을 입력하세요"
          />
        </div>
        <div class="form-group">
          <label for="salary">연봉</label>
          <input
            id="salary"
            v-model.number="formData.salary"
            type="number"
            class="form-input"
            placeholder="연봉을 입력하세요"
          />
        </div>
      </div>

      <!-- 예금 희망 정보 섹션 -->
      <div class="form-section">
        <h3>예금 희망 정보</h3>
        <div class="form-group">
          <label for="desire_amount_deposit">예금 희망 금액</label>
          <input
            id="desire_amount_deposit"
            v-model.number="formData.desire_amount_deposit"
            type="number"
            class="form-input"
            placeholder="예금 희망 금액을 입력하세요"
          />
        </div>
        <div class="form-group">
          <label for="deposit_period">예금 희망 기간 (월)</label>
          <input
            id="deposit_period"
            v-model.number="formData.deposit_period"
            type="number"
            class="form-input"
            placeholder="예금 희망 기간을 입력하세요"
          />
        </div>
      </div>

      <!-- 적금 희망 정보 섹션 -->
      <div class="form-section">
        <h3>적금 희망 정보</h3>
        <div class="form-group">
          <label for="desire_amount_saving">월 적금 희망 금액</label>
          <input
            id="desire_amount_saving"
            v-model.number="formData.desire_amount_saving"
            type="number"
            class="form-input"
            placeholder="월 적금 희망 금액을 입력하세요"
          />
        </div>
        <div class="form-group">
          <label for="saving_period">적금 희망 기간 (월)</label>
          <input
            id="saving_period"
            v-model.number="formData.saving_period"
            type="number"
            class="form-input"
            placeholder="적금 희망 기간을 입력하세요"
          />
        </div>
      </div>

      <!-- 버튼 그룹 -->
      <div class="button-group">
        <button type="button" class="cancel-button" @click="handleCancel">
          취소
        </button>
        <button type="submit" class="submit-button" :disabled="loading">
          {{ loading ? '업데이트 중...' : '정보 수정' }}
        </button>
      </div>
    </form>
  </div>
  <div v-else class="loading-container">
    <div class="loading-message">
      <p>로그인이 필요한 서비스입니다</p>
      <RouterLink :to="{ name: 'login' }" class="login-link">로그인 하기</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useUserStore } from '@/stores/users';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();
const loading = ref(false);
const previewImage = ref(null);
const selectedFile = ref(null);

onMounted(() => {
  checkAuth();
  loadUserData();
});

const checkAuth = () => {
  if (!userStore.isLogin) {
    router.push({
      name: 'login',
      query: { redirect: router.currentRoute.value.fullPath }
    });
  }
};

watch(() => userStore.isLogin, (newValue) => {
  if (!newValue) {
    checkAuth();
  }
});

// 프로필 이미지 URL 계산
const profileImageUrl = computed(() => {
  if (userStore.userInfo?.profile_image) {
    return `${import.meta.env.VITE_APP_API_URL}${userStore.userInfo.profile_image}`;
  }
  return '/default-profile.png';
});

// 이미지 로드 실패 시 처리
const handleImageError = (e) => {
  e.target.src = '/default-profile.png';
};

// 이미지 파일 선택 처리
const handleImageChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    // 파일 크기 체크 (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('파일 크기는 5MB를 초과할 수 없습니다.');
      event.target.value = '';
      return;
    }
    
    // 이미지 파일 타입 체크
    if (!file.type.startsWith('image/')) {
      alert('이미지 파일만 업로드 가능합니다.');
      event.target.value = '';
      return;
    }

    selectedFile.value = file;
    previewImage.value = URL.createObjectURL(file);
  }
};

// 폼 데이터 초기화
const formData = ref({
  name: '',
  age: null,
  money: null,
  salary: null,
  desire_amount_deposit: null,
  deposit_period: null,
  desire_amount_saving: null,
  saving_period: null,
});

// 초기 데이터 로드
const loadUserData = () => {
  if (userStore.userInfo) {
    formData.value = {
      name: userStore.userInfo.name || '',
      age: userStore.userInfo.age || null,
      money: userStore.userInfo.money || null,
      salary: userStore.userInfo.salary || null,
      desire_amount_deposit: userStore.userInfo.desire_amount_deposit || null,
      deposit_period: userStore.userInfo.deposit_period || null,
      desire_amount_saving: userStore.userInfo.desire_amount_saving || null,
      saving_period: userStore.userInfo.saving_period || null,
    };
  }
};

// 폼 제출 처리
const handleSubmit = async () => {
  loading.value = true;
  try {
    const formDataToSend = new FormData();
    
    if (selectedFile.value) {
      formDataToSend.append('profile_image', selectedFile.value);
    }

    Object.keys(formData.value).forEach(key => {
      if (formData.value[key] !== null && formData.value[key] !== '') {
        formDataToSend.append(key, formData.value[key]);
      }
    });

    await userStore.updateUserInfo(formDataToSend);
    await userStore.getUserInfo();
    // alert('회원 정보가 성공적으로 수정되었습니다.');
    router.push({ 
      name: 'myPage', 
      params: { username: userStore.userInfo.username } 
    });
  } catch (error) {
    console.error('Update error:', error);
    alert('회원 정보 수정에 실패했습니다.');
  } finally {
    loading.value = false;
  }
};

// 취소 처리
const handleCancel = () => {
  if (previewImage.value) {
    URL.revokeObjectURL(previewImage.value);
  }
  previewImage.value = null;
  selectedFile.value = null;
  router.back();
};

// 이니셜 가져오기 함수
const getInitials = (name) => {
  if (!name) return '?';
  return name.charAt(0).toUpperCase();
};

// 컴포넌트 언마운트 시 미리보기 URL 정리
onBeforeUnmount(() => {
  if (previewImage.value) {
    URL.revokeObjectURL(previewImage.value);
  }
});
</script>

<style scoped>
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
  white-space: nowrap;
}

header a:hover {
  font-size: 22px;
  color: #1089ff;
}

/* 회원 탈퇴 버튼 */
.delete-button {
  border: none;
  background: none;
  margin-left: 70%;
  white-space: nowrap;
  color: #e74c3c; /* 빨간색 */
  text-decoration: underline;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.delete-button:hover {
  color: #c0392b; /* 더 짙은 빨간색 */
}

.update-page {
  max-width: 800px;
  margin: 2rem auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.update-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.form-group {
  margin-bottom: 15px;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.submit-button, .cancel-button {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-button {
  background-color: #1089ff;
  color: white;
}

.submit-button:hover {
  background-color: #0d74cc;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
}

.cancel-button:hover {
  background-color: #5a6268;
}

/* 프로필 이미지 관련 스타일 */
.profile-image-section {
  text-align: center;
  margin-bottom: 24px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.current-image {
  width: 150px;
  height: 150px;
  margin: 0 auto 16px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #1089ff;
  background-color: #f5f5f5;
}

.current-image img {
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
  background-color: #ffffff;
  color: #1089ff;
  font-size: 2rem;
  font-weight: bold;
}

.image-upload {
  margin: 16px 0;
}

.upload-label {
  display: inline-block;
  padding: 8px 16px;
  background-color: #1089ff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.upload-label:hover {
  background-color: #0d74cc;
}

.file-input {
  display: none;
}

.image-help-text {
  margin-top: 8px;
  font-size: 14px;
  color: #666;
}

</style>