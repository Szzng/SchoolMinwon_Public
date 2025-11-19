import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/services/api'

export interface Child {
  id: number
  name: string
  grade: number
  classroom: number
}

export interface User {
  id: string
  username: string
  email: string
  real_name: string
  user_type: 'PARENT' | 'TEACHER' | 'ADMIN'
  phone: string
  school_name: string
  children?: Child[]
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isTeacher = computed(() => user.value?.user_type === 'TEACHER')
  const isAdmin = computed(() => user.value?.user_type === 'ADMIN')
  const isParent = computed(() => user.value?.user_type === 'PARENT')

  // Actions
  /**
   * 로그인
   */
  async function login(username: string, password: string) {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post('/auth/token/', {
        username,
        password,
      })

      const { access, refresh, user: userData } = response.data

      accessToken.value = access
      refreshToken.value = refresh
      user.value = userData

      // localStorage에 저장
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user', JSON.stringify(userData))

      // apiClient 기본 헤더 업데이트
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`

      return user.value
    } catch (err: any) {
      error.value = err.response?.data?.detail || '로그인에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 회원가입
   */
  async function register(
    username: string,
    email: string,
    password: string,
    passwordConfirm: string,
    userType: 'PARENT' | 'TEACHER' | 'ADMIN',
    realName: string,
    phone: string,
    schoolName: string,
    children?: Array<{ name: string; grade: number; classroom: number }>
  ) {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post('/auth/users/register/', {
        username,
        email,
        password,
        password_confirm: passwordConfirm,
        user_type: userType,
        real_name: realName,
        phone,
        school_name: schoolName,
        children: children || [],
      })

      const { access, refresh, user: userData } = response.data

      accessToken.value = access
      refreshToken.value = refresh
      user.value = userData

      // localStorage에 저장
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user', JSON.stringify(userData))

      // apiClient 기본 헤더 업데이트
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`

      return user.value
    } catch (err: any) {
      error.value =
        err.response?.data?.detail || err.response?.data?.username?.[0] || '회원가입에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 토큰 갱신
   */
  async function refreshAccessToken() {
    if (!refreshToken.value) {
      logout()
      return
    }

    try {
      const response = await apiClient.post('/auth/token/refresh/', {
        refresh: refreshToken.value,
      })

      const { access } = response.data

      accessToken.value = access

      // localStorage에 저장
      localStorage.setItem('access_token', access)

      // apiClient 기본 헤더 업데이트
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`

      return access
    } catch (err) {
      logout()
      throw err
    }
  }

  /**
   * 현재 사용자 정보 조회
   */
  async function fetchMe() {
    if (!accessToken.value) {
      return null
    }

    try {
      const response = await apiClient.get('/auth/users/me/')
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      return user.value
    } catch (err) {
      console.error('Failed to fetch user info:', err)
      logout()
      return null
    }
  }

  /**
   * 프로필 업데이트
   */
  async function updateProfile(data: Partial<User>) {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.put('/auth/users/update_profile/', data)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      return user.value
    } catch (err: any) {
      error.value = '프로필 업데이트에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 로그아웃
   */
  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    error.value = null

    // localStorage 정리
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')

    // apiClient 헤더 제거
    delete apiClient.defaults.headers.common['Authorization']
  }

  /**
   * 초기화: localStorage에서 토큰과 사용자 정보 복원
   */
  function initialize() {
    const savedAccessToken = localStorage.getItem('access_token')
    const savedRefreshToken = localStorage.getItem('refresh_token')
    const savedUser = localStorage.getItem('user')

    if (savedAccessToken) {
      accessToken.value = savedAccessToken
      refreshToken.value = savedRefreshToken
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${savedAccessToken}`
    }

    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (err) {
        console.error('Failed to parse saved user:', err)
        localStorage.removeItem('user')
      }
    }
  }

  /**
   * 토큰 접근자
   */
  function setAccessToken(token: string) {
    accessToken.value = token
    localStorage.setItem('access_token', token)
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,

    // Computed
    isAuthenticated,
    isTeacher,
    isAdmin,
    isParent,

    // Actions
    login,
    register,
    logout,
    initialize,
    fetchMe,
    updateProfile,
    refreshAccessToken,
    setAccessToken,
  }
})
