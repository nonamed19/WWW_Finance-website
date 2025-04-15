import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000'

export const useCommunityStore = defineStore('community', () => {
  const reviews = ref([])
  const error = ref(null)

  const fetchReviews = async () => {
    try {
      const response = await axios.get(`${API_URL}/bankings/reviews/`, {
        // headers: { Authorization: `Token ${localStorage.getItem('token')}` }
      })
      reviews.value = response.data
    } catch (err) {
      error.value = err.response?.data || '리뷰를 불러오는데 실패했습니다.'
    }
  }

  const createReview = async (reviewData) => {
    try {
      const response = await axios.post(`${API_URL}/bankings/reviews/`, reviewData, {
        headers: { Authorization: `Token ${localStorage.getItem('token')}` }
      })
      reviews.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data || '리뷰 작성에 실패했습니다.'
      throw err
    }
  }

  const updateReview = async (reviewId, reviewData) => {
    try {
      const response = await axios.put(`${API_URL}/bankings/reviews/${reviewId}/`, reviewData, {
        headers: { Authorization: `Token ${localStorage.getItem('token')}` }
      })
      const index = reviews.value.findIndex(r => r.id === reviewId)
      if (index !== -1) {
        reviews.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data || '리뷰 수정에 실패했습니다.'
      throw err
    }
  }

  const deleteReview = async (reviewId) => {
    try {
      await axios.delete(`${API_URL}/bankings/reviews/${reviewId}/`, {
        headers: { Authorization: `Token ${localStorage.getItem('token')}` }
      })
      reviews.value = reviews.value.filter(r => r.id !== reviewId)
    } catch (err) {
      error.value = err.response?.data || '리뷰 삭제에 실패했습니다.'
      throw err
    }
  }

  const toggleLike = async (reviewId) => {
    try {
      const response = await axios.post(`${API_URL}/bankings/reviews/${reviewId}/like/`, {}, {
        headers: { Authorization: `Token ${localStorage.getItem('token')}` }
      })
      const review = reviews.value.find(r => r.id === reviewId)
      if (review) {
        review.is_liked = !review.is_liked
        review.like_count = response.data.likes_count
      }
    } catch (err) {
      error.value = err.response?.data || '좋아요 처리에 실패했습니다.'
      throw err
    }
  }

  const addComment = async (reviewId, content) => {
    try {
      const response = await axios.post(`${API_URL}/bankings/reviews/${reviewId}/comments/`, 
        { content },
        { headers: { Authorization: `Token ${localStorage.getItem('token')}` }}
      )
      const review = reviews.value.find(r => r.id === reviewId)
      if (review) {
        review.comments.push(response.data)
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data || '댓글 작성에 실패했습니다.'
      throw err
    }
  }

  return {
    reviews,
    error,
    fetchReviews,
    createReview,
    updateReview,
    deleteReview,
    toggleLike,
    addComment
  }
})