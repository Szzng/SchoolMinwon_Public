import { defineStore } from 'pinia'
import {
  getComplaints,
  getComplaintDetail,
  createComplaint as apiCreateComplaint,
  updateComplaint as apiUpdateComplaint,
  deleteComplaint as apiDeleteComplaint,
  changeComplaintStatus as apiChangeStatus,
  addComment as apiAddComment,
  deleteComment as apiDeleteComment,
  reviewComplaintReply as apiReviewComplaintReply,
  getErrorMessage,
} from '@/services/complaintApi'

export type ComplaintStatus =
  | 'AI응답대기'
  | 'AI응답완료'
  | '1차완료'
  | '2차검토요청'
  | '교무실처리중'
  | '답변완료'
  | '종료됨'

export interface Comment {
  id: string
  complaint: string
  author: number
  author_name: string
  author_type: 'user' | 'staff' | 'ai'
  author_type_display: string
  content: string
  created_at: string
}

export interface Student {
  id: number
  name: string
  grade: number
  classroom: number
}

export type ComplaintCategory =
  | '교육과정'
  | '급식'
  | '시설'
  | '학생지도'
  | '행정'
  | '안전'
  | '학교폭력'
  | '체벌/인권'
  | '학용품비'
  | '방과후활동'
  | '특수교육'
  | '학부모소통'
  | '기숙사'
  | '교사태도'
  | '시험/평가'
  | '진로/진학'
  | '기타'

export interface Attachment {
  id: string
  original_name: string
  size: number
  mime_type: string
  file: string
  created_at: string
}

export interface AIRiskDetect {
  sentiment: 'very_negative' | 'negative' | 'neutral' | 'positive'
  toxicity_score: number
  reasons: string[]
  category: string
  needs_human_review: boolean
  notes_for_staff: string
  generatedAt?: string
}

export interface ComplaintItem {
  id: string
  title: string
  content: string
  author: number
  author_name: string
  children: Student[]
  categories: ComplaintCategory[]
  status: ComplaintStatus
  status_display: string
  history: { at: string; status: ComplaintStatus; note?: string }[]
  ai_response?: {
    content: string
    generatedAt: string
  }
  ai_risk_detect?: AIRiskDetect
  comments: Comment[]
  attachments: Attachment[]
  closed_by?: 'user' | 'staff'
  closed_at?: string
  created_at: string
  updated_at: string
}

export const useComplaintStore = defineStore('complaints', {
  state: () => ({
    items: [] as ComplaintItem[],
    loading: false,
    error: null as string | null,
  }),
  getters: {
    getById: (s) => (id: string) => s.items.find((i) => i.id === id),
  },
  actions: {
    // ==================== 목록 조회 ====================
    async fetchComplaints() {
      this.loading = true
      this.error = null
      try {
        this.items = await getComplaints()
      } catch (error: any) {
        this.error = getErrorMessage(error)
        console.error('Failed to fetch complaints:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // ==================== 상세 조회 ====================
    async fetchComplaintDetail(id: string) {
      this.loading = true
      this.error = null
      try {
        const complaint = await getComplaintDetail(id)
        // 로컬 리스트에서도 업데이트
        const index = this.items.findIndex((i) => i.id === id)
        if (index >= 0) {
          this.items[index] = complaint
        } else {
          this.items.unshift(complaint)
        }
        return complaint
      } catch (error: any) {
        this.error = getErrorMessage(error)
        console.error('Failed to fetch complaint detail:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // ==================== 생성 ====================
    async create(payload: {
      title: string
      content: string
      categories: string[]
      children_ids?: (number | string)[]
      website?: string
    }) {
      this.loading = true
      this.error = null
      try {
        const complaint = await apiCreateComplaint({
          title: payload.title,
          content: payload.content,
          categories: payload.categories,
          children_ids: payload.children_ids?.map((id) => String(id)),
          website: payload.website,
        })
        this.items.unshift(complaint)
        return complaint
      } catch (error: any) {
        this.error = getErrorMessage(error)
        console.error('Failed to create complaint:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // ==================== 수정 ====================
    async update(id: string, payload: { title?: string; content?: string; categories?: string[] }) {
      this.loading = true
      this.error = null
      try {
        const complaint = await apiUpdateComplaint(id, payload)
        const index = this.items.findIndex((i) => i.id === id)
        if (index >= 0) {
          this.items[index] = complaint
        }
        return complaint
      } catch (error: any) {
        this.error = getErrorMessage(error)
        console.error('Failed to update complaint:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // ==================== 삭제 ====================
    async remove(id: string) {
      this.loading = true
      this.error = null
      try {
        await apiDeleteComplaint(id)
        this.items = this.items.filter((i) => i.id !== id)
      } catch (error: any) {
        this.error = getErrorMessage(error)
        console.error('Failed to delete complaint:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // ==================== 상태 변경 ====================
    async changeStatus(id: string, action: string) {
      this.loading = true
      this.error = null
      try {
        const complaint = await apiChangeStatus(id, action)
        const index = this.items.findIndex((i) => i.id === id)
        if (index >= 0) {
          this.items[index] = complaint
        }
        return complaint
      } catch (error: any) {
        this.error = getErrorMessage(error)
        console.error('Failed to change status:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // ==================== 댓글 추가 ====================
    async addComment(complaintId: string, author: { type: 'user' | 'staff' | 'ai'; name: string }, content: string) {
      this.loading = true
      this.error = null
      try {
        console.log('Store: Adding comment to complaint', complaintId, 'with content:', content)
        const comment = await apiAddComment(complaintId, content)
        console.log('Store: Comment added successfully:', comment)

        // 최신 정보로 갱신하기 위해 상세 조회
        console.log('Store: Refreshing complaint detail...')
        const updatedComplaint = await getComplaintDetail(complaintId)

        // 로컬 데이터 업데이트
        const index = this.items.findIndex((i) => i.id === complaintId)
        if (index >= 0) {
          this.items[index] = updatedComplaint
          console.log('Store: Updated complaint item, comments:', updatedComplaint.comments.length)
        } else {
          console.warn('Store: Complaint not found in local items:', complaintId)
          this.items.unshift(updatedComplaint)
        }
        return comment
      } catch (error: any) {
        this.error = getErrorMessage(error)
        console.error('Store: Failed to add comment:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // ==================== 댓글 삭제 ====================
    async removeComment(commentId: string, complaintId: string) {
      this.loading = true
      this.error = null
      try {
        await apiDeleteComment(commentId)
        const complaint = this.items.find((i) => i.id === complaintId)
        if (complaint) {
          complaint.comments = complaint.comments.filter((c) => c.id !== commentId)
        }
      } catch (error: any) {
        this.error = getErrorMessage(error)
        console.error('Failed to delete comment:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // ==================== 1차 완료 ====================
    async markAsResolved(complaintId: string) {
      return this.changeStatus(complaintId, 'first_complete')
    },

    // ==================== 2차 검토 요청 ====================
    async requestSecondReview(complaintId: string) {
      return this.changeStatus(complaintId, 'request_second_review')
    },

    // ==================== 상태 조회 액션들 ====================
    async startStaffReview(complaintId: string) {
      return this.changeStatus(complaintId, 'start_office_processing')
    },

    async updateStaffProcessing(complaintId: string) {
      return this.changeStatus(complaintId, 'start_office_processing')
    },

    async completeResponse(complaintId: string) {
      return this.changeStatus(complaintId, 'response_complete')
    },

    async closeComplaint(complaintId: string, closedBy: 'user' | 'staff') {
      return this.changeStatus(complaintId, closedBy === 'user' ? 'close_by_user' : 'close_by_staff')
    },

    // ==================== AI 리뷰 ====================
    async reviewComplaintReply(complaintId: string, draftContent: string) {
      this.loading = true
      this.error = null
      try {
        console.log('Store: Requesting AI review for complaint', complaintId)
        const response = await apiReviewComplaintReply(complaintId, draftContent)
        console.log('Store: AI review completed:', response)

        // ⚠️ 중요: 백엔드에서 이미 AI 리뷰를 DB에 저장하지 않고 있음
        // response.ai_review에는 임시 AI 리뷰 댓글만 있음
        // 스토어를 업데이트하지 않으므로 1회성 임시 표시만 가능

        return {
          aiReview: response.ai_review || null,
          message: response.message || 'AI review completed'
        }
      } catch (error: any) {
        this.error = getErrorMessage(error)
        console.error('Store: Failed to review complaint reply:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
  },
})
