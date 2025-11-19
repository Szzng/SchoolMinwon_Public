import apiClient from './api'
import type { ComplaintItem, Comment } from '@/stores/complaint'

/**
 * 민원 API 서비스
 */

export interface CreateComplaintPayload {
  title: string
  content: string
  categories: string[]
  children_ids?: string[]
  website?: string
}

export interface UpdateComplaintPayload {
  title?: string
  content?: string
  categories?: string[]
}

export interface StatusChangePayload {
  action: string
}

export interface AIResponsePayload {
  content: string
}

export interface CommentPayload {
  complaint_id: string
  content: string
}

// ==================== Complaint CRUD ====================

/**
 * 민원 목록 조회
 */
export async function getComplaints() {
  const response = await apiClient.get('/complaints/')
  return response.data
}

/**
 * 내 민원 목록 조회
 */
export async function getMyComplaints() {
  const response = await apiClient.get('/complaints/my_complaints/')
  return response.data
}

/**
 * 대기 중인 민원 (교직원용)
 */
export async function getPendingComplaints() {
  const response = await apiClient.get('/complaints/pending_complaints/')
  return response.data
}

/**
 * 민원 상세 조회
 */
export async function getComplaintDetail(id: string) {
  const response = await apiClient.get(`/complaints/${id}/`)
  return response.data
}

/**
 * 민원 생성
 */
export async function createComplaint(payload: CreateComplaintPayload) {
  const response = await apiClient.post('/complaints/', payload)
  return response.data
}

/**
 * 민원 수정
 */
export async function updateComplaint(id: string, payload: UpdateComplaintPayload) {
  const response = await apiClient.patch(`/complaints/${id}/`, payload)
  return response.data
}

/**
 * 민원 삭제
 */
export async function deleteComplaint(id: string) {
  await apiClient.delete(`/complaints/${id}/`)
}

// ==================== Status Management ====================

/**
 * 민원 상태 변경
 */
export async function changeComplaintStatus(id: string, action: string) {
  const response = await apiClient.post(`/complaints/${id}/change_status/`, { action })
  return response.data
}

/**
 * 교무실 댓글 AI 리뷰 요청
 */
export async function reviewComplaintReply(id: string, draftContent: string) {
  const response = await apiClient.post(`/complaints/${id}/review_complaint_reply/`, {
    draft_content: draftContent,
  })
  return response.data
}

// ==================== Comments ====================

/**
 * 댓글 추가
 */
export async function addComment(complaintId: string, content: string) {
  const response = await apiClient.post('/comments/add_to_complaint/', {
    complaint_id: complaintId,
    content,
  })
  return response.data
}

/**
 * 댓글 삭제
 */
export async function deleteComment(id: string) {
  await apiClient.delete(`/comments/${id}/`)
}

// ==================== Attachments ====================

/**
 * 첨부파일 업로드 (FormData 방식)
 * 백엔드에서 파일을 받으려면 multipart/form-data 필요
 */
export async function uploadAttachment(complaintId: string, file: File) {
  const formData = new FormData()
  formData.append('complaint_id', complaintId)
  formData.append('file', file)
  formData.append('original_name', file.name)
  formData.append('size', file.size.toString())
  formData.append('mime_type', file.type)

  const response = await apiClient.post('/attachments/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

/**
 * 첨부파일 삭제
 */
export async function deleteAttachment(id: string) {
  await apiClient.delete(`/attachments/${id}/`)
}

// ==================== Error Handling ====================

/**
 * API 에러 처리 헬퍼
 */
export function getErrorMessage(error: any): string {
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }

  if (error.response?.data?.non_field_errors?.[0]) {
    return error.response.data.non_field_errors[0]
  }

  // 필드별 에러 메시지
  const errorData = error.response?.data
  if (typeof errorData === 'object') {
    const errors = Object.entries(errorData)
      .map(([key, messages]: [string, any]) => {
        if (Array.isArray(messages)) {
          return messages.join(', ')
        }
        return messages
      })
      .join('; ')

    if (errors) {
      return errors
    }
  }

  return error.message || 'An error occurred'
}
