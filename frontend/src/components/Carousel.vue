<template>
  <v-carousel cycle hide-delimiters show-arrows="hover" height="400">
    <!-- 첫 번째 캐러셀 아이템 -->
    <v-carousel-item>
      <div class="caro-item-container">
        <!-- 텍스트 -->
        <div class="caro-item-text right-align">
          <p><span class="color">환율 정보</span>를 바로 확인하세요!</p>
          <div class="title">
            <p>최신 <span class="color">환율 정보</span></p>
            <p>지금 확인하기</p>
          </div>
          <v-btn
            block
            rounded="xl"
            size="x-large"
            color="#1089FF"
            class="caro-item-btn"
            @click="slides[0].action"
          >
            환율 보기<span class="arrow">↗</span>
          </v-btn>
        </div>
        <!-- 이미지 -->
        <img src="@/assets/DolorMan.png" class="caro-item-img left-img" alt="환율 정보" />
      </div>
    </v-carousel-item>

    <!-- 두 번째 캐러셀 아이템 -->
    <v-carousel-item>
      <div class="caro-item-container">
        <!-- 이미지 -->
        <img src="@/assets/EvaluateMan.jpg" class="caro-item-img right-img" alt="평가 게시판" />
        <!-- 텍스트 -->
        <div class="caro-item-text left-align">
          <p>상품 <span class="color">리뷰</span>를 확인해보세요!</p>
          <div class="title">
            <span> 
                
            </span>
            <span> 
                
            </span>
            <p>각 상품에 대한</p>
            <span class="color">사용자 리뷰</span>
          </div>
          <v-btn
            block
            rounded="xl"
            size="x-large"
            color="#1089FF"
            class="caro-item-btn"
            @click="slides[1].action"
          >
            게시판 구경하기<span class="arrow">↗</span>
          </v-btn>
        </div>
      </div>
    </v-carousel-item>

    <!-- 세 번째 캐러셀 아이템 -->
    <v-carousel-item>
      <div class="caro-item-container">
        <!-- 텍스트 -->
        <div class="caro-item-text right-align">
          <p><span class="color">예 ∙ 적금 금리</span>를 쉽게 비교하고</p>
          <div class="title">
            <p>당신에게 딱 맞는</p>
            <p><span class="color">금융 상품 추천</span></p>
          </div>
          <v-btn
            block
            rounded="xl"
            size="x-large"
            color="#1089FF"
            class="caro-item-btn"
            @click="slides[2].action"
          >
            추천받기<span class="arrow">↗</span>
          </v-btn>
        </div>
        <!-- 이미지 -->
        <img src="@/assets/OptionMan.jpg" class="caro-item-img left-img" alt="금융 상품 추천" />
      </div>
    </v-carousel-item>
  </v-carousel>
</template>

<script setup>
import { useRouter } from "vue-router";

// 라우터 설정
const router = useRouter();

// 슬라이드 데이터
const slides = [
  {
    image: "@/assets/DolorMan.png",
    title: "환율 정보 바로가기",
    description: "최신 환율 정보를 확인하세요!",
    buttonText: "환율 보기",
    action: () => {
      router.push("/exchange");
    },
  },
  {
    image: "@/assets/EvaluateMan.jpg",
    title: "평가 게시판 구경하기",
    description: "금융 상품에 대한 사용자 리뷰를 확인해보세요!",
    buttonText: "게시판 구경하기",
    action: () => {
      router.push("/community");
    },
  },
  {
    image: "@/assets/OptionMan.jpg",
    title: "상품 추천 받기",
    description: "당신에게 딱 맞는 금융 상품을 추천해드립니다!",
    buttonText: "추천받기",
    action: () => {
      router.push("/recommendation");
    },
  },
];
</script>

<style scoped>
/* 캐러셀 컨테이너 */
.caro-item-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 97%;
  padding: 20px;
  margin-top: 7px;
  margin-bottom: 7px;
  position: relative;
  background: white; /* 카드 배경 */
  box-shadow: 0 4px 15px rgb(104, 103, 103), /* 아래쪽 그림자 */
              0 -4px 15px rgba(0, 0, 0, 0.3), /* 위쪽 그림자 */
              -4px 0 15px rgba(0, 0, 0, 0.2), /* 왼쪽 그림자 */
              4px 0 15px rgba(0, 0, 0, 0.2); /* 오른쪽 그림자 */
}

/* 캐러셀 이미지 스타일 */
.caro-item-img {
  position: relative;
  max-width: 45%;
  height: auto;
  opacity: 0.7; /* 투명도 조절 */
  transition: opacity 0.3s ease, transform 0.3s ease;
  pointer-events: none; /* 이미지와의 상호작용 제거 */
}

.left-img {
  margin-right: 20px;
}

.right-img {
  margin-left: 20px;
}

/* 텍스트 컨테이너 */
.caro-item-text {
  position: relative;
  max-width: 70%;
  color: #333333;
}

.left-align {
  text-align: left;
}

.right-align {
  text-align: right;
}

.title {
  font-size: 24px;
  font-weight: 700;
  margin: 20px 0;
}

.color {
  color: #1089FF;
  font-weight: bold;
}

.caro-item-btn {
  margin-top: 20px;
}
</style>
