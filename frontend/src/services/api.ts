import axios, { type AxiosResponse } from 'axios'
import mockApiService from './mockData'
import type { HomeworkAnalysis } from '@/types/homework'
import type { HomeworkSubmission as HomeworkSubmissionType } from '@/types/homework'
import type {
  Student,
  StudentCreate,
  StudentUpdate,
  StudentStats,
  StudentListResponse,
  SubjectProgress,
  LearningTrend,
  ErrorTrendAnalysis,
  MultiSubjectSummary,
  PaginationParams
} from '@/types/student'
import type {
  ChatRequest,
  ChatResponse,
  GenerateTextRequest,
  GenerateTextResponse
} from '@/types/chat'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK === 'true'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      // Redirect to login if needed
    }
    return Promise.reject(error)
  }
)

// Types for API responses (legacy)
export interface LegacyApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface ErrorAnalysisRequest {
  question_text: string
  student_answer: string
  correct_answer: string
  subject: 'math' | 'physics' | 'english'
}

export interface ErrorAnalysisResponse {
  error_type: string
  error_severity: 'low' | 'medium' | 'high'
  explanation: string
  improvement_suggestions: string[]
  related_concepts: string[]
}

export interface StudentErrorPattern {
  pattern_type: string
  frequency: number
  recent_occurrences: number
  trend: 'increasing' | 'decreasing' | 'stable'
  description: string
}

export interface ImprovementPlan {
  focus_areas: string[]
  recommended_actions: string[]
  difficulty_level: string
  estimated_time_weeks: number
}

export interface KnowledgePoint {
  id: number
  name: string
  subject: string
  mastery_level: number // 0-100
  last_updated: string
}

export interface LegacyHomeworkSubmission {
  id: number
  subject: string
  submitted_at: string
  grade_score?: number
  feedback?: string
  file_name: string
  processing_status: 'pending' | 'completed' | 'failed'
}

// API Service Class
class ApiService {
  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<boolean> {
    if (USE_MOCK_DATA) {
      return mockApiService.healthCheck()
    }

    try {
      const response = await apiClient.get('/health')
      return response.status === 200
    } catch (error) {
      console.error('Health check failed:', error)
      return false
    }
  }

  /**
   * Single question error analysis - Core feature from ErrorPatternService
   */
  async analyzeQuestionError(
    request: ErrorAnalysisRequest
  ): Promise<ErrorAnalysisResponse> {
    if (USE_MOCK_DATA) {
      return mockApiService.analyzeQuestionError()
    }

    try {
      const response: AxiosResponse<ErrorAnalysisResponse> = await apiClient.post(
        '/v1/error-analysis/analyze-question',
        request
      )
      return response.data
    } catch (error) {
      console.error('Error analyzing question:', error)
      // Fallback to mock data on error
      console.warn('Falling back to mock data')
      return mockApiService.analyzeQuestionError()
    }
  }

  /**
   * Get student error patterns for a subject
   */
  async getStudentErrorPatterns(
    studentId: number,
    subject: string,
    timeframeDays: number = 30
  ): Promise<StudentErrorPattern[]> {
    if (USE_MOCK_DATA) {
      return mockApiService.getStudentErrorPatterns()
    }

    try {
      const response: AxiosResponse<StudentErrorPattern[]> = await apiClient.get(
        `/v1/error-analysis/students/${studentId}/patterns/${subject}`,
        {
          params: { timeframe_days: timeframeDays },
        }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching error patterns:', error)
      // Fallback to mock data on error
      console.warn('Falling back to mock data')
      return mockApiService.getStudentErrorPatterns()
    }
  }

  /**
   * Get improvement plan for a student in a specific subject
   */
  async getImprovementPlan(
    studentId: number,
    subject: string
  ): Promise<ImprovementPlan> {
    if (USE_MOCK_DATA) {
      return mockApiService.getImprovementPlan(studentId, subject)
    }

    try {
      const response: AxiosResponse<ImprovementPlan> = await apiClient.get(
        `/v1/error-analysis/students/${studentId}/improvement-plan/${subject}`
      )
      return response.data
    } catch (error) {
      console.error('Error fetching improvement plan:', error)
      // Fallback to mock data on error
      console.warn('Falling back to mock data')
      return mockApiService.getImprovementPlan(studentId, subject)
    }
  }

  /**
   * Get student's knowledge point mastery levels
   */
  async getKnowledgePointMastery(
    studentId: number,
    subject?: string
  ): Promise<KnowledgePoint[]> {
    if (USE_MOCK_DATA) {
      return mockApiService.getKnowledgePointMastery()
    }

    try {
      const params = subject ? { subject } : {}
      const response: AxiosResponse<KnowledgePoint[]> = await apiClient.get(
        `/v1/students/${studentId}/progress/knowledge-points`,
        { params }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching knowledge points:', error)
      // Fallback to mock data on error
      console.warn('Falling back to mock data')
      return mockApiService.getKnowledgePointMastery()
    }
  }

  /**
   * Upload and grade homework - Updated for new frontend
   */
  async gradeHomework(formData: FormData): Promise<HomeworkAnalysis> {
    if (USE_MOCK_DATA) {
      return mockApiService.gradeHomework()
    }

    try {
      const response: AxiosResponse<{ data?: HomeworkAnalysis } & HomeworkAnalysis> = await apiClient.post(
        '/v1/homework/grade',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      return response.data.data || response.data
    } catch (error) {
      console.error('Error grading homework:', error)
      // Fallback to mock data on error
      console.warn('Falling back to mock data')
      return mockApiService.gradeHomework()
    }
  }

  /**
   * Generate homework report
   */
  async generateReport(analysisId: string): Promise<Blob> {
    if (USE_MOCK_DATA) {
      return mockApiService.generateReport(analysisId)
    }

    try {
      const response = await apiClient.get(
        `/v1/homework/${analysisId}/report`,
        {
          responseType: 'blob',
        }
      )
      return response.data
    } catch (error) {
      console.error('Error generating report:', error)
      // Fallback to mock data on error
      console.warn('Falling back to mock data')
      return mockApiService.generateReport(analysisId)
    }
  }

  /**
   * Upload and grade homework (legacy method)
   */
  async uploadHomework(
    file: File,
    subject: string,
    studentId?: number
  ): Promise<LegacyHomeworkSubmission> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('subject', subject)
      if (studentId) {
        formData.append('student_id', studentId.toString())
      }

      const response: AxiosResponse<LegacyHomeworkSubmission> = await apiClient.post(
        '/v1/homework/grade',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      return response.data
    } catch (error) {
      console.error('Error uploading homework:', error)
      throw error
    }
  }

  /**
   * Get homework history for a student
   */
  async getHomeworkHistory(
    studentId: number,
    limit: number = 20,
    offset: number = 0
  ): Promise<HomeworkSubmissionType[]> {
    if (USE_MOCK_DATA) {
      return mockApiService.getHomeworkHistory()
    }

    try {
      const response: AxiosResponse<HomeworkSubmissionType[]> = await apiClient.get(
        `/v1/students/${studentId}/homework`,
        {
          params: { limit, offset },
        }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching homework history:', error)
      // Fallback to mock data on error
      console.warn('Falling back to mock data')
      return mockApiService.getHomeworkHistory()
    }
  }

  /**
   * Get detailed homework submission by ID
   */
  async getHomeworkDetails(homeworkId: number): Promise<HomeworkSubmissionType> {
    if (USE_MOCK_DATA) {
      return mockApiService.getHomeworkDetails(homeworkId)
    }

    try {
      const response: AxiosResponse<HomeworkSubmissionType> = await apiClient.get(
        `/v1/homework/${homeworkId}`
      )
      return response.data
    } catch (error) {
      console.error('Error fetching homework details:', error)
      // Fallback to mock data on error
      console.warn('Falling back to mock data')
      return mockApiService.getHomeworkDetails(homeworkId)
    }
  }

  /**
   * AI Chat - 发送聊天消息
   */
  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    if (USE_MOCK_DATA) {
      return mockApiService.sendChatMessage(request)
    }

    try {
      const response: AxiosResponse<ChatResponse> = await apiClient.post(
        '/v1/ai/chat',
        request
      )
      return response.data
    } catch (error) {
      console.error('Error sending chat message:', error)
      console.warn('Falling back to mock data')
      return mockApiService.sendChatMessage(request)
    }
  }

  /**
   * AI Text Generation - 生成文本内容
   */
  async generateText(request: GenerateTextRequest): Promise<GenerateTextResponse> {
    if (USE_MOCK_DATA) {
      return mockApiService.generateText(request)
    }

    try {
      const response: AxiosResponse<GenerateTextResponse> = await apiClient.post(
        '/v1/ai/generate',
        request
      )
      return response.data
    } catch (error) {
      console.error('Error generating text:', error)
      console.warn('Falling back to mock data')
      return mockApiService.generateText(request)
    }
  }

  /**
   * Student Management - 获取学生列表
   */
  async getStudents(params?: PaginationParams & { search?: string; grade?: string }): Promise<StudentListResponse> {
    if (USE_MOCK_DATA) {
      return mockApiService.getStudents(params)
    }

    try {
      const response: AxiosResponse<StudentListResponse> = await apiClient.get(
        '/v1/students',
        { params }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching students:', error)
      console.warn('Falling back to mock data')
      return mockApiService.getStudents(params)
    }
  }

  /**
   * Student Management - 创建学生
   */
  async createStudent(student: StudentCreate): Promise<Student> {
    if (USE_MOCK_DATA) {
      return mockApiService.createStudent(student)
    }

    try {
      const response: AxiosResponse<Student> = await apiClient.post(
        '/v1/students',
        student
      )
      return response.data
    } catch (error) {
      console.error('Error creating student:', error)
      throw error
    }
  }

  /**
   * Student Management - 更新学生信息
   */
  async updateStudent(id: number, updates: StudentUpdate): Promise<Student> {
    if (USE_MOCK_DATA) {
      return mockApiService.updateStudent(id, updates)
    }

    try {
      const response: AxiosResponse<Student> = await apiClient.put(
        `/v1/students/${id}`,
        updates
      )
      return response.data
    } catch (error) {
      console.error('Error updating student:', error)
      throw error
    }
  }

  /**
   * Student Management - 删除学生
   */
  async deleteStudent(id: number): Promise<void> {
    if (USE_MOCK_DATA) {
      return mockApiService.deleteStudent(id)
    }

    try {
      await apiClient.delete(`/v1/students/${id}`)
    } catch (error) {
      console.error('Error deleting student:', error)
      throw error
    }
  }

  /**
   * Student Management - 获取单个学生详情
   */
  async getStudent(id: number): Promise<Student> {
    if (USE_MOCK_DATA) {
      return mockApiService.getStudent(id)
    }

    try {
      const response: AxiosResponse<Student> = await apiClient.get(
        `/v1/students/${id}`
      )
      return response.data
    } catch (error) {
      console.error('Error fetching student:', error)
      console.warn('Falling back to mock data')
      return mockApiService.getStudent(id)
    }
  }

  /**
   * Student Management - 获取学生统计信息
   */
  async getStudentStats(id: number): Promise<StudentStats> {
    if (USE_MOCK_DATA) {
      return mockApiService.getStudentStats(id)
    }

    try {
      const response: AxiosResponse<StudentStats> = await apiClient.get(
        `/v1/students/${id}/stats`
      )
      return response.data
    } catch (error) {
      console.error('Error fetching student stats:', error)
      console.warn('Falling back to mock data')
      return mockApiService.getStudentStats(id)
    }
  }

  /**
   * Error Trends - 获取错误趋势分析
   */
  async getErrorTrends(
    studentId: number,
    subject: string,
    days: number = 30
  ): Promise<ErrorTrendAnalysis> {
    if (USE_MOCK_DATA) {
      return mockApiService.getErrorTrends(studentId, subject, days)
    }

    try {
      const response: AxiosResponse<ErrorTrendAnalysis> = await apiClient.get(
        `/v1/error-analysis/students/${studentId}/trends/${subject}`,
        { params: { days } }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching error trends:', error)
      console.warn('Falling back to mock data')
      return mockApiService.getErrorTrends(studentId, subject, days)
    }
  }

  /**
   * Multi-Subject Summary - 获取多科目汇总分析
   */
  async getMultiSubjectSummary(
    studentId: number,
    subjects?: string[],
    timeframeDays: number = 30
  ): Promise<MultiSubjectSummary> {
    if (USE_MOCK_DATA) {
      return mockApiService.getMultiSubjectSummary(studentId, subjects, timeframeDays)
    }

    try {
      const params: any = { timeframe_days: timeframeDays }
      if (subjects && subjects.length > 0) {
        params.subjects = subjects
      }

      const response: AxiosResponse<MultiSubjectSummary> = await apiClient.get(
        `/v1/error-analysis/students/${studentId}/summary`,
        { params }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching multi-subject summary:', error)
      console.warn('Falling back to mock data')
      return mockApiService.getMultiSubjectSummary(studentId, subjects, timeframeDays)
    }
  }

  /**
   * Subject Progress - 获取科目学习进度
   */
  async getSubjectProgress(
    studentId: number,
    subject: string,
    timeframeDays: number = 30
  ): Promise<SubjectProgress> {
    if (USE_MOCK_DATA) {
      return mockApiService.getSubjectProgress(studentId, subject, timeframeDays)
    }

    try {
      const response: AxiosResponse<SubjectProgress> = await apiClient.get(
        `/v1/students/${studentId}/progress/${subject}`,
        { params: { timeframe_days: timeframeDays } }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching subject progress:', error)
      console.warn('Falling back to mock data')
      return mockApiService.getSubjectProgress(studentId, subject, timeframeDays)
    }
  }

  /**
   * Learning Trends - 获取学习趋势
   */
  async getLearningTrends(
    studentId: number,
    days: number = 30
  ): Promise<LearningTrend[]> {
    if (USE_MOCK_DATA) {
      return mockApiService.getLearningTrends(studentId, days)
    }

    try {
      const response: AxiosResponse<LearningTrend[]> = await apiClient.get(
        `/v1/students/${studentId}/trends`,
        { params: { days } }
      )
      return response.data
    } catch (error) {
      console.error('Error fetching learning trends:', error)
      console.warn('Falling back to mock data')
      return mockApiService.getLearningTrends(studentId, days)
    }
  }
}

// Export singleton instance
export const apiService = new ApiService()

// Homework service for new frontend
export const homeworkService = {
  gradeHomework: (formData: FormData) => apiService.gradeHomework(formData),
  generateReport: (analysisId: string) => apiService.generateReport(analysisId),
  getHistory: () => apiService.getHomeworkHistory(1), // Default student ID
}

// Chat service for AI interaction
export const chatService = {
  sendMessage: (request: ChatRequest) => apiService.sendChatMessage(request),
  generateText: (request: GenerateTextRequest) => apiService.generateText(request),
}

// Student management service
export const studentService = {
  getAll: (params?: PaginationParams & { search?: string; grade?: string }) => apiService.getStudents(params),
  getById: (id: number) => apiService.getStudent(id),
  create: (student: StudentCreate) => apiService.createStudent(student),
  update: (id: number, updates: StudentUpdate) => apiService.updateStudent(id, updates),
  delete: (id: number) => apiService.deleteStudent(id),
  getStats: (id: number) => apiService.getStudentStats(id),
}

// Analytics service for trends and summaries
export const analyticsService = {
  getErrorTrends: (studentId: number, subject: string, days?: number) =>
    apiService.getErrorTrends(studentId, subject, days),
  getMultiSubjectSummary: (studentId: number, subjects?: string[], timeframeDays?: number) =>
    apiService.getMultiSubjectSummary(studentId, subjects, timeframeDays),
  getSubjectProgress: (studentId: number, subject: string, timeframeDays?: number) =>
    apiService.getSubjectProgress(studentId, subject, timeframeDays),
  getLearningTrends: (studentId: number, days?: number) =>
    apiService.getLearningTrends(studentId, days),
}

// Export default
export default apiService
