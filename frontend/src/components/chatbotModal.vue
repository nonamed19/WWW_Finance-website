<template>
    <div v-if="chatbotStore.isOpen" class="chat-modal">
      <div class="chat-modal-content">
        <header>
          <h2>챗봇 상담</h2>
          <button class="close-btn" @click="chatbotStore.closeModal">X</button>
        </header>
        <div class="chat-body" ref="messagesContainer">
          <!-- 메시지 목록 -->
          <div class="messages">
            <div
              v-for="(message, index) in chatbotStore.messages"
              :key="index"
              :class="['message-container', message.role]"
            >
              <!-- 챗봇 메시지 -->
              <div
                v-if="message.role === 'assistant'"
                class="message-bubble assistant-message"
              >
                <div class="chatbot-icon">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 0 24"
                    fill="currentColor"
                    class="icon"
                  >
                    <circle cx="12" cy="12" r="10" fill="#b2d8a5" />
                    <circle cx="9" cy="10" r="1.5" fill="#6d6a5d" />
                    <circle cx="15" cy="10" r="1.5" fill="#6d6a5d" />
                    <path
                      d="M9 15h6a1 1 0 0 1 0 2H9a1 1 0 1 1 0-2z"
                      fill="#6d6a5d"
                    />
                  </svg>
                </div>
                <p>{{ message.content }}</p>
              </div>
  
              <!-- 사용자 메시지 -->
              <div
                v-else
                class="message-bubble user-message"
              >
                <p>{{ message.content }}</p>
              </div>
            </div>
          </div>
        </div>
        <!-- 입력 필드 -->
        <div class="input-container">
          <textarea
            v-model="newMessage"
            placeholder="메시지를 입력하세요..."
            @keyup.enter="handleSendMessage"
          ></textarea>
          <button @click="handleSendMessage">전송</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch, nextTick } from "vue";
  import { useChatbotStore } from "@/stores/chatbot";
  
  const chatbotStore = useChatbotStore();
  const newMessage = ref("");
  const messagesContainer = ref(null);
  
  // 메시지 전송 후 동작
  const handleSendMessage = async () => {
    if (newMessage.value.trim()) {
      chatbotStore.sendMessage(newMessage.value);
      newMessage.value = "";
      await nextTick();
      scrollToBottom();
    }
  };
  
  // 자동 스크롤 함수
  const scrollToBottom = () => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  };
  
  // 메시지 변경 감지 (새로운 메시지가 추가될 때 스크롤 아래로 이동)
  watch(
    () => chatbotStore.messages,
    async () => {
      await nextTick();
      scrollToBottom();
    },
    { deep: true }
  );
  
  // 초기화 시 마지막 메시지로 스크롤
  onMounted(() => {
    scrollToBottom();
  });
  </script>
  
  <style scoped>
  .chat-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5); /* 어두운 반투명 배경 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.chat-modal-content {
  width: 400px;
  max-height: 600px;
  background: #ffffff; /* 흰색 */
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); /* 외부 그림자 */
}

header {
  background: #1089ff; /* 기준 파란색 */
  color: white;
  padding: 10px;
  font-size: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
}

.chat-body {
  flex: 1;
  padding: 10px;
  background: #f0f9ff; /* 연한 파란색 */
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-top: 1px solid #ddd; /* 상단 경계 */
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 메시지 스타일 */
.message-container {
  display: flex;
  align-items: flex-start;
}

.message-container.user {
  justify-content: flex-end; /* 사용자 메시지는 오른쪽 */
}

.message-container.assistant {
  justify-content: flex-start; /* 챗봇 메시지는 왼쪽 */
}

.message-bubble {
  max-width: 70%;
  padding: 10px;
  border-radius: 12px;
  word-wrap: break-word;
  text-align: left;
}

.assistant-message {
  background: #e3f2fd; /* 연한 파란색 */
  color: #333;
  margin-right: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-message {
  background: #1089ff; /* 기준 파란색 */
  color: white;
  margin-left: auto;
}

/* 챗봇 아이콘 */
.chatbot-icon {
  margin-right: 8px;
}

.chatbot-icon .icon {
  width: 30px;
  height: 30px;
}

/* 입력 필드 영역 */
.input-container {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px;
  background: #f0f9ff; /* 연한 파란색 */
}

textarea {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: none;
  background: #ffffff; /* 흰색 */
}

button {
  background: #1089ff; /* 기준 파란색 */
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background: #0d74cc; /* 짙은 파란색 */
}

</style>
  