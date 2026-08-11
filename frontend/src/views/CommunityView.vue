<template>
  <div class="community-page">
    <h1>상품 평가 게시판</h1>
    <!-- <button @click="refreshReviews" class="refresh-button">새로고침</button> -->

    <!-- 의견 작성 폼 -->
    <div v-if="isLoggedIn" class="opinion-form">
      <!-- <h2>{{ isEditing ? '상품 평가 수정' : '상품 평가 작성' }}</h2> -->

      <!-- 상품 유형 선택 -->
      <div class="product-type">
        <label>상품 유형:</label>
        <select v-model="reviewForm.productType" class="product-select" :disabled="isEditing">
          <option value="deposit">예금</option>
          <option value="saving">적금</option>
        </select>
      </div>

      <!-- 상품 선택 -->
      <div class="product-select-container">
        <label>상품 선택:</label>
        <select v-model="reviewForm.productName" class="product-select" :disabled="isEditing">
          <option disabled value="">상품을 선택하세요</option>
          <option
            v-for="product in getProductList(reviewForm.productType)"
            :key="product.fin_prdt_cd"
            :value="product.fin_prdt_nm"
          >
            {{ product.fin_prdt_nm }}
          </option>
        </select>
      </div>

      <input
        v-model="reviewForm.title"
        class="input-title"
        type="text"
        placeholder="제목을 입력하세요"
      />
      <textarea
        v-model="reviewForm.content"
        class="textarea-content"
        placeholder="상품에 대한 의견을 작성하세요"
      ></textarea>

      <!-- 별점 선택 -->
      <div class="rating-container">
        <label>별점:</label>
        <div class="stars">
          <span
            v-for="star in 5"
            :key="star"
            class="star"
            :class="{ filled: star <= reviewForm.rating }"
            @click="reviewForm.rating = star"
          >
            ★
          </span>
        </div>
      </div>
      <br>
      <div class="form-buttons">
        <button class="submit-button" @click="handleSubmit">
          {{ isEditing ? '수정하기' : '작성하기' }}
        </button>
        <button v-if="isEditing" class="cancel-button" @click="cancelEdit">
          취소
        </button>
      </div>
    </div>

    <div v-else class="login-message">
    <div class="popup-overlay">
      <div class="popup-content">
        <p class="message-text">리뷰를 작성하려면 로그인이 필요합니다.</p>
        <router-link to="/login" class="login-button">로그인하기</router-link>
      </div>
    </div>
  </div>

    <!-- 게시물 목록 -->
    <div class="opinion-list">
      <h2>사용자 평가</h2>
      <div
        v-for="review in communityStore.reviews"
        :key="review.id"
        class="opinion-card"
      >
        <div class="review-header">
          <h3>{{ review.title }}</h3>
          <div class="review-meta">
            <span class="author">작성자: {{ review.username }}</span><span> / </span>
            <span class="date">{{ formatDate(review.created_at) }}</span>
            <span v-if="review.updated_at !== review.created_at" class="edited">(수정됨)</span>
          </div>
        </div>

        <p class="product-info">
          {{ review.product_type === "deposit" ? "예금" : "적금" }} - {{ review.product_name }}
        </p>
        <p class="content">{{ review.content }}</p>
        
        <div class="rating-like-container">
          <p class="rating">
            <span v-for="star in 5" :key="star" class="star" 
                  :class="{ filled: star <= review.rating }">★</span>
          </p>
          <button 
            v-if="isLoggedIn"
            class="like-button" 
            :class="{ liked: review.is_liked }"
            @click="handleLike(review.id)"
          >
            ♥ {{ review.like_count }}
          </button>
        </div>

        <!-- 리뷰 수정/삭제 버튼 -->
        <div v-if="review.is_owner" class="review-actions">
          <button class="edit-button" @click="startEdit(review)">수정</button>
          <button class="delete-button" @click="handleDelete(review.id)">삭제</button>
        </div>

        <!-- 댓글 섹션 -->
        <div class="comment-section">
          <button class="comment-toggle" @click="toggleComments(review)">
            댓글 {{ review.comments.length }}개
          </button>

          <div v-if="review.showComments" class="comments-container">
            <div v-for="comment in review.comments" :key="comment.id" class="comment">
              <div class="comment-content">
                <span class="comment-author">{{ comment.username }}</span>
                <p>{{ comment.content }}</p>
              </div>
              <div v-if="comment.is_owner" class="comment-actions">
                <button @click="editComment(review.id, comment)"><u>수정</u></button><span> / </span>
                <button @click="deleteComment(review.id, comment.id)"><u>삭제</u></button>
              </div>
            </div>

            <!-- 댓글 작성 폼 -->
            <div v-if="isLoggedIn" class="comment-form">
              <input
                v-model="commentForms[review.id]"
                class="input-comment"
                type="text"
                placeholder="댓글을 입력하세요"
                @keyup.enter="addComment(review.id)"
              />
              <button @click="addComment(review.id)">댓글 작성</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useProductStore } from '../stores/product'
import { useCommunityStore } from '../stores/community'
import { useUserStore } from '../stores/users'
import { storeToRefs } from 'pinia'

const productStore = useProductStore()
const communityStore = useCommunityStore()
const userStore = useUserStore()

// 상태 관리
const isLoggedIn = computed(() => userStore.isLogin)
const isEditing = ref(false)
const editingReviewId = ref(null)
const commentForms = ref({})

// 리뷰 폼 초기 상태
const initialReviewForm = {
  productType: 'deposit',
  productName: '',
  title: '',
  content: '',
  rating: 0
}

const reviewForm = ref({ ...initialReviewForm })

// 데이터 로드
onMounted(async () => {
  if (!productStore.deposits.length) {
    await productStore.saveDeposits()
    await productStore.fetchDeposits()
  }
  if (!productStore.savings.length) {
    await productStore.saveSavings()
    await productStore.fetchSavings()
  }
  await communityStore.fetchReviews()
})

// 메소드
const refreshReviews = async () => {
  await communityStore.fetchReviews()
}

const getProductList = (type) => {
  return type === 'deposit' ? productStore.deposits : productStore.savings
}

const handleSubmit = async () => {
  try {
    if (!validateForm()) return

    const reviewData = {
      product_type: reviewForm.value.productType,
      product_name: reviewForm.value.productName,
      title: reviewForm.value.title,
      content: reviewForm.value.content,
      rating: reviewForm.value.rating
    }

    if (isEditing.value) {
      await communityStore.updateReview(editingReviewId.value, reviewData)
    } else {
      await communityStore.createReview(reviewData)
    }

    resetForm()
  } catch (error) {
    console.error('리뷰 제출 실패:', error)
    alert('리뷰 제출에 실패했습니다.')
  }
}

const validateForm = () => {
  if (!reviewForm.value.productName ||
      !reviewForm.value.title ||
      !reviewForm.value.content ||
      !reviewForm.value.rating) {
    alert('모든 필드를 입력해주세요.')
    return false
  }
  return true
}

const resetForm = () => {
  reviewForm.value = { ...initialReviewForm }
  isEditing.value = false
  editingReviewId.value = null
}

const startEdit = (review) => {
  isEditing.value = true
  editingReviewId.value = review.id
  reviewForm.value = {
    productType: review.product_type,
    productName: review.product_name,
    title: review.title,
    content: review.content,
    rating: review.rating
  }
}

const cancelEdit = () => {
  resetForm()
}

const handleDelete = async (reviewId) => {
  if (!confirm('정말 삭제하시겠습니까?')) return
  try {
    await communityStore.deleteReview(reviewId)
  } catch (error) {
    console.error('리뷰 삭제 실패:', error)
    alert('리뷰 삭제에 실패했습니다.')
  }
}

const handleLike = async (reviewId) => {
  try {
    await communityStore.toggleLike(reviewId)
  } catch (error) {
    console.error('좋아요 처리 실패:', error)
  }
}

const toggleComments = (review) => {
  review.showComments = !review.showComments
}

const addComment = async (reviewId) => {
  const content = commentForms.value[reviewId]?.trim()
  if (!content) return

  try {
    await communityStore.addComment(reviewId, content)
    commentForms.value[reviewId] = ''
  } catch (error) {
    console.error('댓글 작성 실패:', error)
    alert('댓글 작성에 실패했습니다.')
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.community-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 16px;
  background: #ffffff; /* 흰색 배경 */
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 부드러운 그림자 */
}

h1 {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  color: #1368bd; /* 신뢰감 있는 파란색 */
  margin-bottom: 20px;
}

.refresh-button {
  margin-bottom: 20px;
  padding: 8px 16px;
  background: #1089ff; /* 기준 파란색 */
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.refresh-button:hover {
  background: #0d74cc; /* 더 짙은 파란색 */
}

.opinion-form {
  margin-bottom: 24px;
  padding: 16px;
  background: #f9faff; /* 연한 파란색 */
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.input-title,
.textarea-content,
.input-comment,
.product-select {
  width: 100%;
  margin-bottom: 12px;
  padding: 12px;
  border: 1px solid #d0e6ff; /* 연한 파란 테두리 */
  border-radius: 8px;
  font-size: 14px;
  background: #ffffff;
}

.stars {
  display: flex;
  gap: 4px;
  font-size: 24px;
  cursor: pointer;
}

.star {
  color: #ccc; /* 기본 별 색상 */
  transition: color 0.3s ease;
}

.star.filled {
  color: #ffd700; /* 별점이 활성화된 경우 금색 */
}

.submit-button {
  padding: 10px 16px;
  background: #1089ff; /* 기준 파란색 */
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.submit-button:hover {
  background: #0d74cc; /* 더 짙은 파란색 */
}

.cancel-button {
  padding: 10px 16px;
  background: #f5f5f5; /* 회색 */
  color: #666;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.cancel-button:hover {
  background: #e0e0e0; /* 약간 더 짙은 회색 */
}

.opinion-card {
  background: #ffffff;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.review-meta {
  font-size: 0.9em;
  color: #666;
}

.rating-like-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
}

.like-button {
  padding: 6px 12px;
  border: 1px solid #ff4081;
  background: #ffffff;
  color: #ff4081;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s ease, color 0.3s ease;
}

.like-button.liked {
  background: #ff4081; /* 하트 버튼 활성화 시 색상 */
  color: white;
}

.edit-button {
  background: #4caf50; /* 녹색 */
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.edit-button:hover {
  background: #43a047; /* 짙은 녹색 */
}

.delete-button {
  background: #f44336; /* 빨간색 */
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.delete-button:hover {
  background: #e53935; /* 짙은 빨간색 */
}

.comment-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.comment {
  padding: 10px;
  margin: 5px 0;
  background: #f5f5f5;
  border-radius: 8px;
}

.comment-author {
  font-weight: bold;
  margin-right: 10px;
}

.comment-form {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.input-comment {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5); /* 반투명 배경 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-content {
  background-color: #ffffff; /* 흰색 배경 */
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 그림자 */
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.message-text {
  font-size: 1.2rem;
  color: #333333;
  margin-bottom: 1.5rem;
}

.login-button {
  display: inline-block;
  padding: 0.8rem 2rem;
  background-color: #1089ff; /* 파란색 */
  color: white;
  border: none;
  border-radius: 8px;
  text-decoration: none;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.login-button:hover {
  background-color: #0d74cc; /* 더 짙은 파란색 */
}
</style>