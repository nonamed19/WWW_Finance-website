<template>
    <div class="loading-screen">
      <img src="@/assets/logo.jpg" alt="App Logo" class="logo" />
    </div>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router';
  import { onMounted } from 'vue';
  
  const router = useRouter();
  
  // 로고를 일정 시간 표시한 후 메인 페이지로 이동
  onMounted(() => {
    setTimeout(() => {
      router.push('/Main'); // '/main'으로 전환
    }, 2500); // 4초 동안 로고 표시
  });
  </script>
  
  <style scoped>
  .loading-screen {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh; /* 전체 화면 */
    max-width: 600px;
    background-color: #ffffff; /* 배경색 */
    margin: 0;
    padding: 0;
    overflow: hidden; /* 스크롤 제거 */
  }
  
  .logo {
    width: 1000px;
    height: auto;
    animation: fadeIn 1.5s; /* 페이드 인 효과 */
    display: flex;
    justify-content: center;
  }
  
  /* 애니메이션 */
  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
  </style>
  