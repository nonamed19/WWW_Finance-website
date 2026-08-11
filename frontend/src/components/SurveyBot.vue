<template>
  <div class="survey-container">
    <div v-if="!userStore.isLogin">
      <div class="overlay"></div>
      <div class="login-popup">
        <h2>로그인이 필요합니다</h2>
        <p>추천 목록과 설문조사를 이용하려면 로그인 또는 회원가입이 필요합니다.</p>
        <button @click="goToLogin">로그인</button>
        <button @click="goToSignup">회원가입</button>
      </div>
    </div>
    <div v-else>
      <div v-if="!surveyCompleted" class="survey-bot">
        <div class="survey-header">
          <h2>맞춤 금융 상품 추천을 위한 설문조사</h2>
          <p>{{ currentSection.title }}</p>
        </div>

        <div class="survey-progress">
          <div class="progress-bar">
            <div :style="{ width: `${progressPercentage}%` }" class="progress-fill"></div>
          </div>
          <span>{{ currentQuestionIndex + 1 }} / {{ totalQuestions }}</span>
        </div>

        <div class="survey-content">
          <div class="question-container">
            <h3>{{ currentQuestion.text }}</h3>
            <div class="options-container">
              <button
                v-for="option in currentQuestion.options"
                :key="option.value"
                :class="['option-button', { selected: selectedOption === option.value }]"
                @click="selectOption(option.value)"
              >
                {{ option.label }}
              </button>
            </div>
          </div>

          <div class="navigation-buttons">
            <button
              v-if="currentQuestionIndex > 0"
              @click="previousQuestion"
              class="nav-button"
            >
              이전
            </button>
            <button
              v-if="currentQuestionIndex < totalQuestions - 1"
              @click="nextQuestion"
              class="nav-button"
              :disabled="!selectedOption"
            >
              다음
            </button>
            <button
              v-else
              @click="submitSurvey"
              class="submit-button"
              :disabled="!selectedOption"
            >
              제출하기
            </button>
          </div>
        </div>
      </div>

      <div v-else class="survey-completion">
        <h2>설문이 완료되었습니다!</h2>
        <p>맞춤형 금융 상품 추천 결과를 확인하시겠습니까?</p>
        <button @click="goToRecommendations" class="recommendation-button">
          추천 결과 보기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/users'
import axios from 'axios'

const userStore = useUserStore()
const router = useRouter()

// 상태 관리
const currentQuestionIndex = ref(0)
const selectedOption = ref(null)
const surveyResponses = ref({})
const surveyCompleted = ref(false)

// 설문 데이터 정의
const surveyStructure = {
  basicInfo: {
    title: '기본 정보',
    questions: [
      {
        id: 'age_group',
        text: '연령대를 선택해주세요.',
        options: [
          { value: '20대', label: '20대' },
          { value: '30대', label: '30대' },
          { value: '40대', label: '40대' },
          { value: '50대', label: '50대' },
          { value: '60대 이상', label: '60대 이상' } // 학습 데이터에 맞게 수정
        ]
      },
      {
        id: 'income_source',
        text: '현재 주요 소득원은 무엇인가요?',
        options: [
          { value: '직장', label: '직장' },
          { value: '자영업', label: '자영업' },
          { value: '프리랜서', label: '프리랜서' },
          { value: '기타', label: '기타' }
        ]
      },
      {
        id: 'asset_size',
        text: '자산 규모를 선택해주세요.',
        options: [
          { value: '1000만원 이하', label: '1000만원 이하' }, // 학습 데이터에 맞게 수정
          { value: '1000만원 ~ 5000만원', label: '1000만원 ~ 5000만원' },
          { value: '5000만원 이상', label: '5000만원 이상' }
        ]
      }
    ]
  },
  financialGoals: {
    title: '금융 목표',
    questions: [
      {
        id: 'financial_purpose',
        text: '금융 상품을 이용하는 주요 목적은 무엇인가요?',
        options: [
          { value: '단기 수익', label: '단기 수익' }, // 학습 데이터에 맞게 수정
          { value: '장기 자산 관리', label: '장기 자산 관리' },
          { value: '리스크 회피', label: '리스크 회피' },
          { value: '재산 증식', label: '재산 증식' }
        ]
      },
      {
        id: 'important_factor',
        text: '금융 상품에서 가장 중요하게 생각하는 요소는 무엇인가요?',
        options: [
          { value: '이율', label: '이율' },
          { value: '안정성', label: '안정성' },
          { value: '유동성', label: '유동성' },
          { value: '브랜드 신뢰도', label: '브랜드 신뢰도' }
        ]
      },
      {
        id: "recent_investment",
        text: "최근 투자 경험이 있나요?",
        options: [
          { value: true, label: "예" },
          { value: false, label: "아니오" }
        ]
      },
    ]
  },
  financialExperience: {
    title: '금융 이용 경험',
    questions: [
      {
        id: 'financial_products',
        text: '이용한 적이 있는 금융 상품은 무엇인가요?',
        options: [
          { value: '예금', label: '예금' },
          { value: '적금', label: '적금' },
          { value: '펀드', label: '펀드' },
          { value: '주식', label: '주식' },
          { value: '없음', label: '없음' }
        ]
      },
      {
        id: 'preferred_bank',
        text: '주로 사용하는 은행은 어디인가요?',
        options: [
          { value: '국민은행', label: '국민은행' },
          { value: '신한은행', label: '신한은행' },
          { value: '우리은행', label: '우리은행' },
          { value: '하나은행', label: '하나은행' },
          { value: '기타', label: '기타' }
        ]
      }
    ]
  }
}

// Computed Properties
const currentSection = computed(() => {
  const sections = Object.values(surveyStructure)
  let questionCount = 0

  for (const section of sections) {
    questionCount += section.questions.length
    if (currentQuestionIndex.value < questionCount) {
      return section
    }
  }
  return sections[0]
})

const currentQuestion = computed(() => {
  const sections = Object.values(surveyStructure)
  let questionIndex = currentQuestionIndex.value

  for (const section of sections) {
    if (questionIndex < section.questions.length) {
      return section.questions[questionIndex]
    }
    questionIndex -= section.questions.length
  }
})

const totalQuestions = computed(() => {
  return Object.values(surveyStructure).reduce(
    (acc, section) => acc + section.questions.length,
    0
  )
})

const progressPercentage = computed(() => {
  return (currentQuestionIndex.value / totalQuestions.value) * 100
})

// Methods
const selectOption = (option) => {
  selectedOption.value = option
  surveyResponses.value[currentQuestion.value.id] = option
}

const nextQuestion = () => {
  if (selectedOption.value) {
    currentQuestionIndex.value++
    selectedOption.value =
      surveyResponses.value[currentQuestion.value?.id] || null
  }
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    selectedOption.value =
      surveyResponses.value[currentQuestion.value.id] || null
  }
}

const submitSurvey = async (surveyData) => {
  axios({
  method: "post",
  url: `${import.meta.env.VITE_API_URL}/surveys/submit-survey/`,
  data: {
    age_group: surveyResponses.value.age_group, // 설문 응답 데이터 매핑
    income_source: surveyResponses.value.income_source,
    asset_size: surveyResponses.value.asset_size,
    financial_purpose: surveyResponses.value.financial_purpose,
    important_factor: surveyResponses.value.important_factor,
    recent_investment: surveyResponses.value.recent_investment,
    financial_products: surveyResponses.value.financial_products,
    preferred_bank: surveyResponses.value.preferred_bank,
  },
  headers: {
    Authorization: `Token ${localStorage.getItem("token")}`,
    "Content-Type": "application/json", // JSON 형식 지정
  },
})
  .then(() => {
    alert("설문이 성공적으로 저장되었습니다.");
    userStore.surveyCompleted = true;
    localStorage.setItem("surveyCompleted", "true");

      // 추천 페이지로 이동
    router.push("/recommendation");
  })
  .catch((error) => {
    console.error("설문 제출 실패:", error);
    alert("설문 데이터를 저장하는 중 문제가 발생했습니다. 다시 시도해주세요.");
  });
};


const goToRecommendations = () => {
  router.push('/recommendation')
}

const goToLogin = () => {
  if (router.currentRoute.value.name !== 'login') {
    router.push({ name: 'login', query: { redirect: '/survey' } });
  }
};

const goToSignup = () => {
  if (router.currentRoute.value.name !== 'signup') {
    router.push({ name: 'signup', query: { redirect: '/survey' } });
  }
};
</script>


<style scoped>
.survey-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #ffffff;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

/* Login Popup Overlay */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

/* Login Popup */
.login-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #ffffff; /* 흰색 배경 */
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 400px;
  padding: 1.5rem;
  text-align: center;
  z-index: 1001;
}

.login-popup h2 {
  font-size: 1.5rem;
  color: #1368bd; /* 파란색 */
  font-weight: bold;
  margin-bottom: 1rem;
}

.login-popup p {
  font-size: 1rem;
  color: #333333;
  margin-bottom: 1.5rem;
}

.login-popup button {
  width: 100%;
  padding: 0.8rem;
  font-size: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-bottom: 0.8rem;
  color: white;
}

/* Primary Button (로그인) */
.login-popup button:nth-of-type(1) {
  background-color: #1089ff; /* 파란색 */
}

.login-popup button:nth-of-type(1):hover {
  background-color: #0d74cc; /* 더 짙은 파란색 */
}

/* Secondary Button (회원가입) */
.login-popup button:nth-of-type(2) {
  background-color: #1089ff; /* 노란색 */
}

.login-popup button:nth-of-type(2):hover {
  background-color: #0d74cc; /* 더 짙은 노란색 */
}

/* Progress Bar */
.survey-progress {
  margin-bottom: 2rem;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background-color: #f0f0f0;
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #1089ff;
  transition: width 0.3s ease;
}

/* Survey Header */
.survey-header h2 {
  font-size: 1.8rem;
  color: #1368bd;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.survey-header p {
  font-size: 1rem;
  color: #666;
}

/* Survey Content */
.survey-content {
  padding: 1.5rem;
  border-radius: 12px;
  background-color: #f9f9f9;
}

.question-container h3 {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1rem;
}

.options-container {
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}

.option-button {
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background-color: #ffffff;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #333;
}

.option-button:hover {
  border-color: #1089ff;
  background-color: #f0f8ff;
}

.option-button.selected {
  border-color: #1089ff;
  background-color: #e6f4ff;
  color: #1368bd;
  font-weight: bold;
}

/* Navigation Buttons */
.navigation-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
}

.nav-button {
  padding: 0.8rem 2rem;
  border: 2px solid #1089ff;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  background-color: white;
  color: #1089ff;
  transition: all 0.3s ease;
}

.nav-button:hover {
  background-color: #bdddfe;
}

.nav-button:disabled {
  border-color: #cccccc;
  background-color: #ffcccc;
  color: #666666;
  cursor: not-allowed;
}

/* Submit Button */
.submit-button {
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  background-color: #1089ff;
  color: white;
}

.submit-button:hover {
  background-color: #0d74cc;
}

.submit-button:disabled {
  background-color: #ffffff;
  color: #1089ff;
  cursor: not-allowed;
}

/* Survey Completion */
.survey-completion {
  text-align: center;
}

.survey-completion h2 {
  font-size: 1.8rem;
  color: #1368bd;
  font-weight: bold;
  margin-bottom: 1rem;
}

.survey-completion p {
  font-size: 1rem;
  color: #333;
  margin-bottom: 1.5rem;
}

.recommendation-button {
  padding: 1rem 2rem;
  background-color: #1089ff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.recommendation-button:hover {
  background-color: #0d74cc;
}

.recommendation-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
