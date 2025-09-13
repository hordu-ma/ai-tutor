// 学生管理相关的类型定义

export interface Student {
  id: number
  name: string
  email?: string
  phone?: string
  grade: string
  class?: string
  student_number?: string
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface StudentCreate {
  name: string
  email?: string
  phone?: string
  grade: string
  class?: string
  student_number?: string
}

export interface StudentUpdate {
  name?: string
  email?: string
  phone?: string
  grade?: string
  class?: string
  student_number?: string
  is_active?: boolean
}

export interface StudentStats {
  total_homework: number
  average_score: number
  improvement_rate: number
  active_days: number
  last_activity: string
  subject_performance: SubjectPerformance[]
}

export interface SubjectPerformance {
  subject: string
  average_score: number
  total_questions: number
  correct_rate: number
  recent_trend: 'improving' | 'stable' | 'declining'
}

export interface StudentFilter {
  search?: string
  grade?: string
  class?: string
  is_active?: boolean
}

export interface StudentListResponse {
  students: Student[]
  total: number
  page: number
  size: number
}

// 学习进度相关
export interface SubjectProgress {
  student_id: number
  subject: string
  total_questions: number
  correct_answers: number
  accuracy_rate: number
  improvement_rate: number
  knowledge_points: KnowledgePointProgress[]
  recent_performance: RecentPerformance[]
  weak_areas: string[]
  strengths: string[]
}

export interface KnowledgePointProgress {
  name: string
  mastery_level: number // 0-100
  total_practiced: number
  correct_count: number
  last_practiced: string
  difficulty: 'easy' | 'medium' | 'hard'
}

export interface RecentPerformance {
  date: string
  score: number
  total: number
  accuracy: number
}

// 学习趋势分析
export interface LearningTrend {
  student_id: number
  subject: string
  time_period: 'week' | 'month' | 'quarter'
  trend_data: TrendPoint[]
  overall_trend: 'improving' | 'stable' | 'declining'
  prediction: TrendPrediction
}

export interface TrendPoint {
  date: string
  accuracy_rate: number
  questions_count: number
  average_score: number
  study_time_minutes: number
}

export interface TrendPrediction {
  expected_improvement: number
  confidence_level: number
  recommended_actions: string[]
}

// 错误趋势分析
export interface ErrorTrendAnalysis {
  student_id: number
  subject: string
  analysis_period: string
  overall_trend: 'improving' | 'stable' | 'declining'
  error_rate_trend: ErrorRatePoint[]
  error_type_trends: ErrorTypeTrend[]
  systematic_improvements: string[]
  persistent_issues: string[]
}

export interface ErrorRatePoint {
  date: string
  error_rate: number
  total_questions: number
  error_count: number
}

export interface ErrorTypeTrend {
  error_type: string
  trend: 'improving' | 'stable' | 'worsening'
  frequency_change: number
  recent_count: number
  historical_average: number
}

// 多科目汇总
export interface MultiSubjectSummary {
  student_id: number
  analysis_period: string
  overall_performance: OverallPerformance
  subject_comparisons: SubjectComparison[]
  cross_subject_patterns: CrossSubjectPattern[]
  recommendations: GlobalRecommendation[]
}

export interface OverallPerformance {
  total_questions: number
  total_errors: number
  overall_accuracy: number
  improvement_trend: 'improving' | 'stable' | 'declining'
  grade_equivalent: string
}

export interface SubjectComparison {
  subject: string
  accuracy_rate: number
  error_count: number
  rank_among_subjects: number
  strength_level: 'strong' | 'average' | 'weak'
  key_issues: string[]
}

export interface CrossSubjectPattern {
  pattern_type: string
  affected_subjects: string[]
  description: string
  severity: 'high' | 'medium' | 'low'
  improvement_suggestions: string[]
}

export interface GlobalRecommendation {
  priority: 'high' | 'medium' | 'low'
  category: 'study_method' | 'time_management' | 'concept_review' | 'practice_focus'
  description: string
  estimated_impact: string
  time_investment: string
}

// API响应类型
export interface StudentApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 分页相关
export interface PaginationParams {
  page: number
  size: number
}

export interface PaginatedStudentResponse<T = any> {
  items: T[]
  total: number
  page: number
  size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}
