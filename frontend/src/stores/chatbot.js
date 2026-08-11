// stores/chatbot.js
import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const useChatbotStore = defineStore("chatbot", () => {
  const isOpen = ref(false);
  const messages = ref([]);
  const conversationId = ref(null);

  // 모달 열기
  const openModal = function () {
    isOpen.value = true;
    loadChatHistory(); // 대화 내역 로드
    if (messages.value.length === 0) {
      messages.value.push({
        id: Date.now(),
        role: "assistant",
        content: "안녕하세요! 무엇을 도와드릴까요?",
      });
    }
  };

  // 모달 닫기
  const closeModal = function () {
    isOpen.value = false;
  };

  // 메시지 전송
  const sendMessage = function (message) {
    if (!message.trim()) return;

    // 사용자 메시지 추가
    messages.value.push({ id: Date.now(), role: "user", content: message });

    // AI 응답 요청
    axios({
      method: "post",
      url: `${API_URL}/chats/chat-message/`,
      data: {
        conversation_id: conversationId.value,
        message,
      },
      headers: {
        Authorization: `Token ${localStorage.getItem("token")}`,
      },
    })
      .then((response) => {
        conversationId.value = response.data.conversation_id;
        messages.value.push({
          id: Date.now() + 1,
          role: "assistant",
          content: response.data.message,
        });
      })
      .catch((error) => {
        console.error("메시지 전송 실패:", error);
        messages.value.push({
          id: Date.now() + 2,
          role: "assistant",
          content: "죄송합니다. 문제가 발생했습니다. 다시 시도해주세요.",
        });
      });
  };

  // 대화 내역 로드
  const loadChatHistory = async () => {
    try {
      const response = await axios({
        method: "get",
        url: `${API_URL}/chats/chat-history/`,
        headers: {
          Authorization: `Token ${localStorage.getItem("token")}`,
        },
      });
  
      if (response.data.length > 0) {
        const lastConversation = response.data[0];
        conversationId.value = lastConversation.id;
        messages.value = lastConversation.messages;
      } else {
        // 대화 내역이 없을 경우 새로운 대화 시작
        conversationId.value = null;
        messages.value = [];
        console.log("대화 내역이 없습니다. 새로운 대화를 시작합니다.");
      }
    } catch (err) {
      console.error("대화 내역 불러오기 실패:", err);
      // 새로운 대화 시작
      conversationId.value = null;
      messages.value = [];
    }
  };
  

  return {
    isOpen,
    messages,
    openModal,
    closeModal,
    sendMessage,
    loadChatHistory,
  };
});
