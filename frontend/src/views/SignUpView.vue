<script setup>
import { computed, ref } from 'vue';
import { useUserStore } from '@/stores/users';
import { useVuelidate } from '@vuelidate/core';
import { email, required, minLength, maxLength, alphaNum, sameAs, helpers } from '@vuelidate/validators';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();

const checkList = ['service', 'info'];
const selected = ref([]);
const show1 = ref(false);
const show2 = ref(false);

const isAgreeAll = computed({
  get() {
    return checkList.length === selected.value.length;
  },
  set(e) {
    selected.value = e ? checkList : [];
  },
});

const errorAgree = ref('ㅤ');

const initialState = {
  username: '',
  name: '',
  email: '',
  password1: '',
  password2: '',
};

const state = ref({
  ...initialState,
});

const rules = {
  username: {
    required: helpers.withMessage('아이디를 입력해주세요.', required),
    alphaNum: helpers.withMessage('영어 대소문자와 숫자만 입력가능합니다.', alphaNum),
    minLength: helpers.withMessage('5자 이상 입력해야합니다.', minLength(5)),
    maxLength: helpers.withMessage('20자 이하로 입력해야합니다.', maxLength(20)),
  },
  name: {
    required: helpers.withMessage('닉네임을 입력해주세요.', required),
    maxLength: helpers.withMessage('20자 이하로 입력해야합니다.', maxLength(20)),
  },
  email: {
    required: helpers.withMessage('이메일을 입력해주세요.', required),
    email: helpers.withMessage('이메일 주소가 정확한지 확인해 주세요.', email),
    maxLength: helpers.withMessage('100자 이하로 입력해야합니다.', maxLength(100)),
  },
  password1: { 
    required: helpers.withMessage('비밀번호를 입력해주세요.', required),
    minLength: helpers.withMessage('8~16자의 영문 대/소문자, 숫자, 특수문자를 사용해 주세요. 특수문자는 *!@#$%^&만 사용가능합니다.', minLength(8)),
    maxLength: helpers.withMessage('8~16자의 영문 대/소문자, 숫자, 특수문자를 사용해 주세요. 특수문자는 *!@#$%^&만 사용가능합니다.', maxLength(16)),
    containspasswordrequirement: helpers.withMessage(
      () => `8~16자의 영문 대/소문자, 숫자, 특수문자를 사용해 주세요. 특수문자는 *!@#$%^&만 사용가능합니다.`, 
      (value) => /(?=.*[a-z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])/.test(value)
    )
  },
  password2: { 
    required: helpers.withMessage('비밀번호 확인은 필수 사항입니다.', required),
    sameAsPassword: helpers.withMessage('비밀번호가 일치하지 않습니다.',
      sameAs(computed(() => state.value.password1))
    )
  }
};

const v$ = useVuelidate(rules, state);

const clearForm = () => {
  v$.value.$reset();
  Object.assign(state.value, initialState);
};

const signUp = async () => {
  v$.value.$validate();

  if (selected.value.length !== checkList.length) {
    errorAgree.value = '약관에 동의하셔야 합니다.';
    return;
  }

  if (v$.value.$invalid) {
    return;
  }

  try {
    const payload = {
      username: state.value.username,
      name: state.value.name,
      email: state.value.email,
      password1: state.value.password1,
      password2: state.value.password2,
    };

    await userStore.signUp(payload);
    alert('회원가입이 완료되었습니다!');
    clearForm();
  } catch (error) {
    alert('회원가입 중 문제가 발생했습니다. 다시 시도해 주세요.');
  }
};
</script>

<template>
  <v-card class="container">
    <v-card-title>Sign up to <span class="color">WWW</span></v-card-title>

    <div class="checkbox">
      <p class="warning" v-text="errorAgree"></p>
      <v-checkbox
        color="#1089FF"
        label="(필수) 서비스 이용약관 동의"
        value="service"
        v-model="selected"
      ></v-checkbox>
      <v-checkbox
        color="#1089FF"
        label="(필수) 개인정보 처리 동의"
        value="info"
        v-model="selected"
      ></v-checkbox>
      <v-checkbox color="#1089FF" v-model="isAgreeAll">
        <template v-slot:label>
          <span class="color">전체 동의</span>
        </template>
      </v-checkbox>
    </div>

    <form @submit.prevent="signUp" @keypress.enter="signUp">
      <v-text-field
        variant="outlined"
        color="#1089FF"
        label="아이디"
        v-model="state.username"
        :error-messages="v$.username.$errors.map((e) => e.$message)"
        @input="v$.username.$touch"
        @blur="v$.username.$touch"
      ></v-text-field>

      <v-text-field
        variant="outlined"
        color="#1089FF"
        label="닉네임"
        v-model="state.name"
        :error-messages="v$.name.$errors.map((e) => e.$message)"
        @input="v$.name.$touch"
        @blur="v$.name.$touch"
      ></v-text-field>

      <v-text-field
        variant="outlined"
        color="#1089FF" 
        label="이메일"
        v-model="state.email"
        :error-messages="v$.email.$errors.map((e) => e.$message)"
        @input="v$.email.$touch"
        @blur="v$.email.$touch"
      ></v-text-field>

      <v-text-field
        variant="outlined"
        color="#1089FF"
        :append-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
        :type="show1 ? 'text' : 'password'"
        label="비밀번호"
        v-model="state.password1"
        @click:append="show1 = !show1"
        :error-messages="v$.password1.$errors.map((e) => e.$message)"
        @input="v$.password1.$touch"
        @blur="v$.password1.$touch"
      ></v-text-field>

      <v-text-field
        variant="outlined"
        color="#1089FF"
        :append-icon="show2 ? 'mdi-eye' : 'mdi-eye-off'"
        :type="show2 ? 'text' : 'password'"
        label="비밀번호 확인"
        v-model="state.password2"
        @click:append="show2 = !show2"
        :error-messages="v$.password2.$errors.map((e) => e.$message)"
        @input="v$.password2.$touch"
        @blur="v$.password2.$touch"
      ></v-text-field>

      <v-btn block variant="flat" color="#1089FF" @click.prevent="signUp">
        Sign up
      </v-btn>
    </form>
    <div class="already-account">
      <router-link :to="{ name: 'login' }">이미 계정이 있습니까? 로그인</router-link>
    </div>
  </v-card>


</template>

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

.v-card-title {
  font-size: 1.5rem;
  color: #1089ff; /* 파란색 */
  font-weight: bold;
  /* margin-bottom: 1rem; */
}

.v-card-title .color {
  color: #1368bd; /* 강조 색상 */
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem; /* 칸 사이 간격 조정 */
}

.v-text-field {
  background-color: #f8f8f8; /* 밝은 회색 배경 */
  border-radius: 8px;
}

.v-btn {
  padding: 0.8rem;
  border-radius: 8px;
  font-size: 1rem;
  background-color: #1089ff; /* 파란색 */
  color: white;
  transition: background-color 0.3s ease;
}

.v-btn:hover {
  background-color: #0d74cc; /* 더 짙은 파란색 */
}

/* .checkbox {
  text-align: start;
  margin-bottom: 0rem;
} */

/* .checkbox .v-checkbox {
  margin: 0; /* 칸 사이 여백 제거 */
  /* padding: 0; /* 간격 최소화 */
/* } */

.warning {
  color: #b00020; /* 경고 빨간색 */
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
}

.v-btn[block] {
  margin-top: 1.5rem;
}

.already-account {
  margin-top: 1.5rem;
  font-size: 0.9rem;
  text-align: center;
}

.already-account a {
  color: #1089ff; /* 파란색 */
  text-decoration: underline;
  cursor: pointer;
  transition: color 0.2s ease;
}

.already-account a:hover {
  color: #0d74cc; /* 더 짙은 파란색 */
}

form + .redirect-link {
  margin-top: 1.5rem; /* 폼과 하단 링크 간 적절한 간격 */
}
</style>
