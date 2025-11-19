import { defineStore } from 'pinia'

export interface AIReviewResult {
  complaintId: string
  content: string
  originalContent: string  // 리뷰 대상이었던 댓글 원문
  timestamp: string
}

/**
 * AI Review Store
 * AI 리뷰 결과를 localStorage에 저장하여 페이지 새로고침 후에도 유지합니다.
 */
export const useAIReviewStore = defineStore('aiReview', {
  state: () => ({
    reviews: new Map<string, AIReviewResult>(),
  }),

  getters: {
    /**
     * 특정 민원의 AI 리뷰 결과 조회
     */
    getReviewByComplaintId: (state) => (complaintId: string) => {
      return state.reviews.get(complaintId) || null
    },

    /**
     * 모든 AI 리뷰 결과 조회
     */
    getAllReviews: (state) => {
      return Array.from(state.reviews.values())
    },
  },

  actions: {
    /**
     * localStorage에서 리뷰 데이터 로드
     */
    loadFromStorage() {
      try {
        const stored = localStorage.getItem('aiReviews_v1')
        if (stored) {
          const data = JSON.parse(stored) as Array<[string, AIReviewResult]>
          this.reviews = new Map(data)
          console.log('AI reviews loaded from localStorage:', this.reviews.size)
        }
      } catch (error) {
        console.error('Failed to load AI reviews from localStorage:', error)
        this.reviews.clear()
      }
    },

    /**
     * localStorage에 리뷰 데이터 저장
     */
    saveToStorage() {
      try {
        const data = Array.from(this.reviews.entries())
        localStorage.setItem('aiReviews_v1', JSON.stringify(data))
        console.log('AI reviews saved to localStorage')
      } catch (error) {
        console.error('Failed to save AI reviews to localStorage:', error)
      }
    },

    /**
     * AI 리뷰 결과 추가/업데이트
     */
    setReview(complaintId: string, content: string, originalContent: string, timestamp: string) {
      this.reviews.set(complaintId, {
        complaintId,
        content,
        originalContent,
        timestamp,
      })
      this.saveToStorage()
      console.log(`AI review saved for complaint ${complaintId}`)
    },

    /**
     * 특정 민원의 AI 리뷰 결과 삭제
     */
    deleteReview(complaintId: string) {
      this.reviews.delete(complaintId)
      this.saveToStorage()
      console.log(`AI review deleted for complaint ${complaintId}`)
    },

    /**
     * 모든 AI 리뷰 결과 삭제
     */
    clearAll() {
      this.reviews.clear()
      localStorage.removeItem('aiReviews_v1')
      console.log('All AI reviews cleared')
    },
  },
})
