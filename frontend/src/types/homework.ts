// 作业批改相关的类型定义

export interface HomeworkSubmission {
  id: number
  student_id: number
  subject: string
  submission_date: string
  total_questions: number
  correct_answers: number
  accuracy_rate: number
  total_score: number
  max_score: number
  grade_percentage: number
  time_spent_minutes?: number
  difficulty_level: number
  ai_provider?: string
  ocr_text?: string
  processing_time?: number
  feedback?: string
  weak_knowledge_points: string[]
  improvement_suggestions: string[]
  error_types: string[]
  is_completed: boolean
  created_at: string
  updated_at: string
}

export interface HomeworkAnalysis {
  id: string
  submission_id: string
  subject: 'math' | 'physics' | 'english'
  total_score: number
  max_score: number
  error_count: number
  correct_count: number
  mastery_level: number
  analyzed_at: string

  errors?: ErrorAnalysis[]
  knowledge_points?: KnowledgePoint[]
  improvement_plan?: ImprovementPlan
}

export interface ErrorAnalysis {
  question_number: number
  error_type: string
  reason: string
  correct_answer: string
  explanation: string
  knowledge_point?: string
  difficulty_level?: 'easy' | 'medium' | 'hard'
}

export interface KnowledgePoint {
  name: string
  score: number
  mastery_level: 'excellent' | 'good' | 'fair' | 'poor'
  suggestion: string
  related_errors?: number[]
}

export interface ImprovementPlan {
  suggestions: string[]
  recommended_practice: string[]
  focus_areas: string[]
  estimated_study_time?: string
}

export interface UploadForm {
  subject: 'math' | 'physics' | 'english'
  provider: 'qwen' | 'kimi'
  file: File | null
}

export interface GradingResponse {
  success: boolean
  message: string
  data?: HomeworkAnalysis
  error?: string
}

export interface ReportGenerationRequest {
  analysis_id: string
  format: 'pdf' | 'html'
  include_suggestions?: boolean
  include_explanations?: boolean
}

export interface HomeworkStats {
  total_submissions: number
  average_grade: number
  recent_submissions: number
  improvement_trend: number
}

export interface FilterOptions {
  subject?: string
  status?: string
  dateRange?: [Date, Date]
  search?: string
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 分页响应类型
export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  size: number
  has_next: boolean
  has_prev: boolean
}
