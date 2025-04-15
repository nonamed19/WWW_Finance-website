<template>
  <v-card class="container">
    <h1>Login to <span class="color">www</span></h1>

    <v-form @submit.prevent="logIn" @keypress.enter="logIn">
      <v-text-field
        variant="outlined"
        color="#1089ff"
        label="아이디"
        v-model="username"
      ></v-text-field>
      <v-text-field
        variant="outlined"
        color="#1089ff"
        :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
        :type="show ? 'text' : 'password'"
        label="비밀번호"
        v-model="password"
        @click:append="show = !show"
      ></v-text-field>
      <div v-if="errorMessage" class="warning text-red">
        <p>{{ errorMessage }}</p>
      </div>
      <v-btn block variant="flat" color="#1089ff" @click.prevent="logIn">
        Log in
      </v-btn>
    </v-form>

    <div class="redirect-link">
      <router-link :to="{ name: 'signup', query: { redirect: route.query.redirect } }">
        계정이 없으신가요? <span>회원가입</span>
      </router-link>
    </div>
  </v-card>
</template>


<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/stores/users';
import { useRouter, useRoute } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();

const show = ref(false);
const username = ref('');
const password = ref('');
const isRight = ref(true);

const errorMessage = ref('');

const logIn = async () => {
  try {
    const payload = { username: username.value, password: password.value };
    const isLoggedIn = await userStore.logIn(payload);

    if (isLoggedIn) {
      // 로그인 성공 후 리디렉트
      const redirectPath = route.query.redirect || '/survey';
      router.push({ name: 'Survey' });
    } else {
      // 로그인 실패 시
      errorMessage.value = '로그인에 실패했습니다. 아이디와 비밀번호를 확인하세요.';
    }
  } catch (error) {
    console.error('Login Error:', error);
    errorMessage.value = '서버에 문제가 발생했습니다. 나중에 다시 시도하세요.';
  }
};

</script>

<style scoped>
.container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 1.5rem;
  background-color: #ffffff; /* 흰색 배경 */
  border-radius: 12px;
  border: 1px solid #e0e0e0; /* 연한 회색 경계 */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 부드러운 그림자 */
  text-align: center;
}

h1 {
  font-size: 1.5rem;
  color: #1089ff; /* 파란색 */
  margin-bottom: 1.5rem;
}

h1 .color {
  color: #1368bd; /* 강조 색상 */
  font-weight: bold;
}

v-form {
  display: flex;
  flex-direction: column;
  gap: 1rem; /* 칸 사이 간격 */
}

v-text-field {
  font-size: 1rem;
  border-radius: 8px;
  background-color: #f8f8f8; /* 밝은 회색 배경 */
}

.warning {
  color: #b00020; /* 경고 메시지 빨간색 */
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.redirect-link {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.redirect-link span {
  text-decoration: underline;
  color: #1089ff; /* 파란색 강조 */
  font-weight: bold;
  cursor: pointer;
}

.redirect-link span:hover {
  color: #0d74cc; /* 호버 상태 파란색 */
}

v-btn {
  background-color: #1089ff; /* 기본 파란색 버튼 */
  color: white;
  font-size: 1rem;
  border-radius: 8px;
  padding: 0.8rem;
  transition: background-color 0.3s ease;
}

v-btn:hover {
  background-color: #0d74cc; /* 호버 상태 */
}

v-btn:disabled {
  background-color: #cccccc; /* 비활성화 상태 */
  cursor: not-allowed;
}
</style>
