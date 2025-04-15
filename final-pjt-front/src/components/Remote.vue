<script setup>
import { ref } from 'vue';

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const toggleChatbot = () => {
  console.log('챗봇 활성화!');
};
</script>

<template>
  <!-- Remote 버튼은 화면의 최상단에 고정 -->
  <div class="remote-wrapper">
    <div class="remote-button" @click="scrollToTop">
      <v-icon>mdi-arrow-up</v-icon>
    </div>
  </div>
</template>

<style scoped>
.remote-wrapper {
  position: fixed; /* 모든 화면에서 고정 */
  right: calc((100vw - 600px) / 2 - 40px); /* 600px 중앙 기준에서 20px 튀어나오도록 설정 */
  bottom: 20px; /* 화면 하단에서 20px 위 */
  display: flex;
  flex-direction: column;
  gap: 15px;
  z-index: 9999; /* 항상 최상단에 표시 */
}

.remote-button {
  background-color: #fff; /* 흰색 박스 */
  color: #000; /* 검은색 아이콘 */
  width: 50px;
  height: 50px;
  border-radius: 50%; /* 버튼을 동그랗게 */
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); /* 약간의 그림자 */
  cursor: pointer;
  transition: transform 0.2s;
}

.remote-button:hover {
  transform: scale(1.1); /* 호버 시 크기 증가 */
}
</style>
