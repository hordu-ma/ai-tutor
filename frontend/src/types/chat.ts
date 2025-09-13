// AI聊天相关的类型定义

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  status?: 'sending' | 'sent' | 'failed'
}

export interface ChatSession {
  id: string
  title: string
  subject?: string
  created_at: string
  updated_at: string
  message_count: number
  is_active: boolean
}

export interface ChatRequest {
  messages: ChatMessage[]
  provider?: 'qwen' | 'kimi'
  model?: string
  temperature?: number
  max_tokens?: number
  context?: ChatContext
}

export interface ChatResponse {
  success: boolean
  data?: {
    response: string
    provider: string
    model?: string
    metadata?: {
      messages_count: number
      response_length: number
      processing_time?: number
    }
  }
  message?: string
  error?: string
}

export interface ChatContext {
  student_id?: number
  subject?: string
  current_topic?: string
  difficulty_level?: 'beginner' | 'intermediate' | 'advanced'
  learning_objectives?: string[]
}

export interface QuickPrompt {
  id: string
  title: string
  content: string
  category: 'homework_help' | 'concept_explanation' | 'practice_problems' | 'study_tips'
  subject?: string
  usage_count: number
}

export interface ChatSettings {
  provider: 'qwen' | 'kimi'
  model?: string
  temperature: number
  max_tokens: number
  auto_save: boolean
  show_thinking_process: boolean
}

export interface GenerateTextRequest {
  prompt: string
  provider?: 'qwen' | 'kimi'
  model?: string
  temperature?: number
  max_tokens?: number
  context?: GenerationContext
}

export interface GenerationContext {
  type: 'homework_solution' | 'explanation' | 'practice_problem' | 'study_plan'
  subject?: string
  difficulty?: 'easy' | 'medium' | 'hard'
  target_audience?: 'student' | 'teacher' | 'parent'
}

export interface GenerateTextResponse {
  success: boolean
  data?: {
    text: string
    provider: string
    model?: string
    metadata?: {
      prompt_length: number
      response_length: number
      generation_time?: number
    }
  }
  message?: string
  error?: string
}

export interface ConversationSummary {
  session_id: string
  main_topics: string[]
  key_concepts_discussed: string[]
  student_questions: number
  assistant_responses: number
  learning_progress: string
  suggested_next_steps: string[]
}

export interface ChatAnalytics {
  total_sessions: number
  total_messages: number
  average_session_length: number
  most_discussed_subjects: SubjectUsage[]
  user_engagement_score: number
  common_question_types: QuestionType[]
}

export interface SubjectUsage {
  subject: string
  session_count: number
  message_count: number
  average_satisfaction: number
}

export interface QuestionType {
  type: string
  count: number
  percentage: number
  typical_examples: string[]
}

export interface ChatError {
  type: 'network' | 'api' | 'validation' | 'rate_limit' | 'server'
  message: string
  details?: string
  retry_after?: number
}

export interface MessageReaction {
  message_id: string
  type: 'helpful' | 'not_helpful' | 'needs_clarification'
  feedback?: string
  timestamp: string
}
