// Mock data service for testing frontend without backend
import type {
  ErrorAnalysisResponse,
  StudentErrorPattern,
  ImprovementPlan,
  KnowledgePoint
} from './api'
import type { HomeworkAnalysis, HomeworkSubmission } from '@/types/homework'
import type {
  Student,
  StudentStats,
  ErrorTrendAnalysis,
  MultiSubjectSummary,
  SubjectProgress,
  LearningTrend
} from '@/types/student'

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export const mockApiService = {
  /**
   * Mock single question error analysis
   */
  async analyzeQuestionError(): Promise<ErrorAnalysisResponse> {
    await delay(1500) // Simulate processing time

    return {
      error_type: "计算错误",
      error_severity: "medium" as const,
      explanation: "学生在解方程过程中出现了基本的代数运算错误。具体来说，在移项时没有正确处理常数项，导致最终答案不正确。",
      improvement_suggestions: [
        "复习基本的代数运算规则，特别是移项法则",
        "多练习类似的一元一次方程求解",
        "在计算过程中要仔细检查每一步",
        "建议使用验算来确认答案的正确性"
      ],
      related_concepts: ["一元一次方程", "移项", "代数运算", "方程求解"]
    }
  },

  /**
   * Mock student error patterns
   */
  async getStudentErrorPatterns(): Promise<StudentErrorPattern[]> {
    await delay(800)

    return [
      {
        pattern_type: "计算错误",
        frequency: 12,
        recent_occurrences: 8,
        trend: "decreasing" as const,
        description: "在基本四则运算中出现错误，主要集中在分数运算和负数处理上。"
      },
      {
        pattern_type: "概念理解错误",
        frequency: 6,
        recent_occurrences: 4,
        trend: "stable" as const,
        description: "对函数的定义域和值域概念理解不清晰，经常混淆相关概念。"
      },
      {
        pattern_type: "解题步骤遗漏",
        frequency: 9,
        recent_occurrences: 7,
        trend: "increasing" as const,
        description: "在解决复杂问题时经常跳过中间步骤，导致逻辑不完整。"
      }
    ]
  },

  /**
   * Mock improvement plan for a student in a specific subject
   */
  async getImprovementPlan(_studentId: number, subject: string): Promise<ImprovementPlan> {
    await delay(600)

    const plans: Record<string, ImprovementPlan> = {
      math: {
        focus_areas: ["基础代数", "方程求解", "函数概念"],
        recommended_actions: [
          "每日完成10道基础代数运算练习题",
          "观看函数概念相关的教学视频",
          "参加每周的数学辅导课程",
          "建立错题本，记录和分析错误原因"
        ],
        difficulty_level: "中等",
        estimated_time_weeks: 6
      },
      physics: {
        focus_areas: ["力学基础", "运动学", "能量守恒"],
        recommended_actions: [
          "复习牛顿三定律的基本概念",
          "练习匀速直线运动和加速运动问题",
          "通过实验加深对物理概念的理解",
          "多做综合性的力学计算题"
        ],
        difficulty_level: "初级",
        estimated_time_weeks: 8
      },
      english: {
        focus_areas: ["语法结构", "时态运用", "词汇积累"],
        recommended_actions: [
          "每日背诵20个新单词",
          "练习现在时、过去时和将来时的用法",
          "阅读英文短文并总结语法要点",
          "参加英语口语练习活动"
        ],
        difficulty_level: "简单",
        estimated_time_weeks: 4
      }
    }

    return plans[subject] || plans.math
  },

  /**
   * Mock knowledge point mastery
   */
  async getKnowledgePointMastery(): Promise<KnowledgePoint[]> {
    await delay(1000)

    return [
      // Math knowledge points
      { id: 1, name: "一元一次方程", subject: "math", mastery_level: 75, last_updated: "2024-01-15" },
      { id: 2, name: "二次函数", subject: "math", mastery_level: 60, last_updated: "2024-01-14" },
      { id: 3, name: "三角函数", subject: "math", mastery_level: 45, last_updated: "2024-01-13" },
      { id: 4, name: "概率统计", subject: "math", mastery_level: 85, last_updated: "2024-01-16" },
      { id: 5, name: "平面几何", subject: "math", mastery_level: 70, last_updated: "2024-01-12" },

      // Physics knowledge points
      { id: 6, name: "牛顿运动定律", subject: "physics", mastery_level: 80, last_updated: "2024-01-15" },
      { id: 7, name: "电磁感应", subject: "physics", mastery_level: 55, last_updated: "2024-01-14" },
      { id: 8, name: "波动光学", subject: "physics", mastery_level: 40, last_updated: "2024-01-13" },
      { id: 9, name: "热力学", subject: "physics", mastery_level: 65, last_updated: "2024-01-16" },
      { id: 10, name: "原子物理", subject: "physics", mastery_level: 35, last_updated: "2024-01-11" },

      // English knowledge points
      { id: 11, name: "现在时态", subject: "english", mastery_level: 90, last_updated: "2024-01-15" },
      { id: 12, name: "过去时态", subject: "english", mastery_level: 75, last_updated: "2024-01-14" },
      { id: 13, name: "条件语句", subject: "english", mastery_level: 50, last_updated: "2024-01-13" },
      { id: 14, name: "被动语态", subject: "english", mastery_level: 60, last_updated: "2024-01-16" },
      { id: 15, name: "阅读理解", subject: "english", mastery_level: 85, last_updated: "2024-01-12" }
    ]
  },

  /**
   * Mock homework history
   */
  async getHomeworkHistory(): Promise<HomeworkSubmission[]> {
    await delay(800)

    return [
      {
        id: "1",
        file_name: "数学作业_第三章.jpg",
        subject: "math" as const,
        provider: "qwen" as const,
        submitted_at: "2024-01-15T14:30:00Z",
        processing_status: "completed" as const,
        grade_score: 85,
        file_url: "/uploads/math_homework_3.jpg",
        analysis_id: "analysis_1"
      },
      {
        id: "2",
        file_name: "物理实验报告.jpg",
        subject: "physics" as const,
        provider: "kimi" as const,
        submitted_at: "2024-01-14T10:15:00Z",
        processing_status: "completed" as const,
        grade_score: 92,
        file_url: "/uploads/physics_report.jpg",
        analysis_id: "analysis_2"
      },
      {
        id: "3",
        file_name: "英语作文_环保主题.jpg",
        subject: "english" as const,
        provider: "qwen" as const,
        submitted_at: "2024-01-13T16:45:00Z",
        processing_status: "completed" as const,
        grade_score: 78,
        file_url: "/uploads/english_essay.jpg",
        analysis_id: "analysis_3"
      },
      {
        id: "4",
        file_name: "数学练习册_第四章.jpg",
        subject: "math" as const,
        provider: "qwen" as const,
        submitted_at: "2024-01-12T09:20:00Z",
        processing_status: "pending" as const,
        file_url: "/uploads/math_homework_4.jpg"
      },
      {
        id: "5",
        file_name: "物理作业_力学部分.jpg",
        subject: "physics" as const,
        provider: "kimi" as const,
        submitted_at: "2024-01-11T11:30:00Z",
        processing_status: "failed" as const,
        file_url: "/uploads/physics_mechanics.jpg"
      },
      {
        id: "6",
        file_name: "英语阅读理解练习.jpg",
        subject: "english" as const,
        provider: "qwen" as const,
        submitted_at: "2024-01-10T15:00:00Z",
        processing_status: "completed" as const,
        grade_score: 88,
        file_url: "/uploads/english_reading.jpg",
        analysis_id: "analysis_6"
      },
      {
        id: "7",
        file_name: "数学竞赛题目.jpg",
        subject: "math" as const,
        provider: "kimi" as const,
        submitted_at: "2024-01-09T13:45:00Z",
        processing_status: "completed" as const,
        grade_score: 95,
        file_url: "/uploads/math_competition.jpg",
        analysis_id: "analysis_7"
      },
      {
        id: "8",
        file_name: "物理概念题集.jpg",
        subject: "physics" as const,
        provider: "qwen" as const,
        submitted_at: "2024-01-08T08:30:00Z",
        processing_status: "completed" as const,
        grade_score: 82,
        file_url: "/uploads/physics_concepts.jpg",
        analysis_id: "analysis_8"
      }
    ]
  },

  /**
   * Mock health check
   */
  async healthCheck(): Promise<boolean> {
    await delay(200)
    return true
  },

  /**
   * Mock homework upload
   */
  async uploadHomework(): Promise<HomeworkSubmission> {
    await delay(2000) // Simulate file upload time

    return {
      id: Date.now().toString(),
      file_name: "数学作业_上传中.jpg",
      subject: "math" as const,
      provider: "qwen" as const,
      submitted_at: new Date().toISOString(),
      processing_status: "pending" as const
    }
  },

  /**
   * Mock homework details
   */
  async getHomeworkDetails(homeworkId: number): Promise<HomeworkSubmission> {
    await delay(500)

    return {
      id: homeworkId.toString(),
      file_name: "数学作业_第5章.jpg",
      subject: "math" as const,
      provider: "qwen" as const,
      submitted_at: "2024-03-15T10:30:00Z",
      processing_status: "completed" as const,
      grade_score: 85,
      file_url: "/uploads/math_homework_5.jpg",
      analysis_id: `analysis_${homeworkId}`
    }
  },

  /**
   * Mock homework grading for new frontend
   */
  async gradeHomework(): Promise<HomeworkAnalysis> {
    await delay(2000) // Simulate AI processing time

    return {
      id: `analysis_${Date.now()}`,
      submission_id: `sub_${Date.now()}`,
      subject: "math" as const,
      total_score: 85,
      max_score: 100,
      error_count: 2,
      correct_count: 8,
      mastery_level: 82,
      analyzed_at: new Date().toISOString(),

      errors: [
        {
          question_number: 3,
          error_type: "计算错误",
          reason: "在分式化简过程中，分母处理不当",
          correct_answer: "x = 3",
          explanation: "分式方程两边同时乘以分母的最小公倍数，然后化简求解。注意检验根是否为增根。"
        },
        {
          question_number: 7,
          error_type: "概念理解错误",
          reason: "对二次函数开口方向判断错误",
          correct_answer: "a > 0，开口向上",
          explanation: "二次函数 y = ax² + bx + c 中，当 a > 0 时开口向上，当 a < 0 时开口向下。"
        }
      ],

      knowledge_points: [
        {
          name: "分式方程",
          score: 75,
          mastery_level: "fair" as const,
          suggestion: "需要加强分式方程的解法练习，特别是增根的检验"
        },
        {
          name: "二次函数",
          score: 68,
          mastery_level: "fair" as const,
          suggestion: "需要复习二次函数的基本性质，包括开口方向、对称轴等"
        },
        {
          name: "因式分解",
          score: 95,
          mastery_level: "excellent" as const,
          suggestion: "掌握得很好，继续保持"
        }
      ],

      improvement_plan: {
        suggestions: [
          "重点复习分式方程的解法和增根检验",
          "加强二次函数基本性质的理解",
          "多做相关练习题巩固知识点",
          "注意计算过程的细心程度"
        ],
        recommended_practice: [
          "分式方程专项练习",
          "二次函数图像与性质",
          "因式分解综合题"
        ],
        focus_areas: ["分式方程", "二次函数性质"],
        estimated_study_time: "建议每天练习30分钟，持续1周"
      }
    }
  },

  /**
   * Mock report generation
   */
  async generateReport(analysisId: string): Promise<Blob> {
    await delay(1000)

    // Create a mock PDF blob
    const mockPdfContent = `作业批改报告

分析ID: ${analysisId}
生成时间: ${new Date().toLocaleString('zh-CN')}

总体评价: 85分
错题数量: 2题
掌握程度: 良好

详细分析请查看完整报告...`

    return new Blob([mockPdfContent], { type: 'application/pdf' })
  },

  /**
   * AI Chat - Mock chat functionality
   */
  async sendChatMessage(request: any): Promise<any> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const responses = [
          "我理解您的问题。让我为您详细解释一下这个概念...",
          "这是一个很好的问题！我们可以从以下几个角度来分析：1. 基础概念... 2. 实际应用... 3. 常见误区...",
          "根据您提供的信息，我建议您重点关注以下几个方面：首先，确保基础概念理解正确...",
          "让我用一个更简单的例子来解释这个问题。假设我们有...",
          "很好的练习！您的思路基本正确，但在第三步有个小问题..."
        ]

        const randomResponse = responses[Math.floor(Math.random() * responses.length)]

        resolve({
          success: true,
          data: {
            response: randomResponse,
            provider: request.provider || 'qwen',
            model: request.model || 'qwen-turbo',
            metadata: {
              messages_count: request.messages.length,
              response_length: randomResponse.length,
              processing_time: Math.random() * 2000 + 500
            }
          },
          message: 'AI对话成功'
        })
      }, 1000 + Math.random() * 1500)
    })
  },

  /**
   * AI Text Generation - Mock text generation
   */
  generateText(request: any): Promise<any> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const generatedTexts = [
          "这是一个关于" + (request.context?.subject || "学习") + "的详细解答。首先，我们需要理解核心概念...",
          "根据您的提示，我为您生成了以下内容：\n\n1. 问题分析\n2. 解决步骤\n3. 注意事项\n\n让我们逐一分析...",
          "这个问题可以通过以下方法解决：\n\n方法一：直接计算\n方法二：图形分析\n方法三：公式推导",
          "基于您的要求，我建议采用循序渐进的学习方法..."
        ]

        const randomText = generatedTexts[Math.floor(Math.random() * generatedTexts.length)]

        resolve({
          success: true,
          data: {
            text: randomText,
            provider: request.provider || 'qwen',
            model: request.model || 'qwen-turbo',
            metadata: {
              prompt_length: request.prompt.length,
              response_length: randomText.length,
              generation_time: Math.random() * 1500 + 800
            }
          },
          message: '文本生成成功'
        })
      }, 800 + Math.random() * 1200)
    })
  },

  /**
   * Student Management - Mock students data
   */
  getStudents(params?: any): Promise<any> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockStudents: Student[] = [
          {
            id: 1,
            name: "张小明",
            email: "xiaoming@example.com",
            phone: "13800138001",
            grade: "初三",
            class: "3班",
            student_number: "2023001",
            created_at: "2023-09-01T08:00:00Z",
            updated_at: "2024-01-15T10:30:00Z",
            is_active: true
          },
          {
            id: 2,
            name: "李小红",
            email: "xiaohong@example.com",
            phone: "13800138002",
            grade: "初三",
            class: "2班",
            student_number: "2023002",
            created_at: "2023-09-01T08:00:00Z",
            updated_at: "2024-01-14T15:20:00Z",
            is_active: true
          },
          {
            id: 3,
            name: "王小强",
            email: "xiaoqiang@example.com",
            phone: "13800138003",
            grade: "初二",
            class: "1班",
            student_number: "2023003",
            created_at: "2023-09-05T09:15:00Z",
            updated_at: "2024-01-13T11:45:00Z",
            is_active: true
          },
          {
            id: 4,
            name: "刘小芳",
            phone: "13800138004",
            grade: "初一",
            class: "4班",
            student_number: "2023004",
            created_at: "2023-09-10T10:00:00Z",
            updated_at: "2024-01-12T14:20:00Z",
            is_active: false
          }
        ]

        let filteredStudents = mockStudents

        // Apply filters
        if (params?.search) {
          const search = params.search.toLowerCase()
          filteredStudents = filteredStudents.filter(s =>
            s.name.toLowerCase().includes(search) ||
            s.student_number?.includes(search) ||
            s.email?.toLowerCase().includes(search)
          )
        }

        if (params?.grade) {
          filteredStudents = filteredStudents.filter(s => s.grade === params.grade)
        }

        resolve({
          students: filteredStudents,
          total: filteredStudents.length,
          page: params?.page || 1,
          size: params?.size || 20
        })
      }, 300)
    })
  },

  createStudent(student: any): Promise<any> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const newStudent: Student = {
          id: Date.now(),
          ...student,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          is_active: true
        }
        resolve(newStudent)
      }, 500)
    })
  },

  updateStudent(id: number, updates: any): Promise<any> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const updatedStudent: Student = {
          id,
          name: updates.name || "张小明",
          email: updates.email,
          phone: updates.phone,
          grade: updates.grade || "初三",
          class: updates.class,
          student_number: updates.student_number,
          created_at: "2023-09-01T08:00:00Z",
          updated_at: new Date().toISOString(),
          is_active: updates.is_active !== undefined ? updates.is_active : true
        }
        resolve(updatedStudent)
      }, 400)
    })
  },

  deleteStudent(_id: number): Promise<void> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve()
      }, 300)
    })
  },

  getStudent(id: number): Promise<any> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const student: Student = {
          id,
          name: "张小明",
          email: "xiaoming@example.com",
          phone: "13800138001",
          grade: "初三",
          class: "3班",
          student_number: "2023001",
          created_at: "2023-09-01T08:00:00Z",
          updated_at: "2024-01-15T10:30:00Z",
          is_active: true
        }
        resolve(student)
      }, 200)
    })
  },

  getStudentStats(_id: number): Promise<any> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const stats: StudentStats = {
          total_homework: 45,
          average_score: 82.5,
          improvement_rate: 15.2,
          active_days: 28,
          last_activity: "2024-01-15T14:30:00Z",
          subject_performance: [
            {
              subject: "数学",
              average_score: 85.2,
              total_questions: 180,
              correct_rate: 0.852,
              recent_trend: 'improving'
            },
            {
              subject: "物理",
              average_score: 78.9,
              total_questions: 125,
              correct_rate: 0.789,
              recent_trend: 'stable'
            },
            {
              subject: "英语",
              average_score: 83.6,
              total_questions: 200,
              correct_rate: 0.836,
              recent_trend: 'improving'
            }
          ]
        }
        resolve(stats)
      }, 400)
    })
  },

  /**
   * Error Trends Analysis - Mock error trends data
   */
  getErrorTrends(studentId: number, subject: string, days: number = 30): Promise<any> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockTrends: ErrorTrendAnalysis = {
          student_id: studentId,
          subject,
          analysis_period: `最近${days}天`,
          overall_trend: 'improving',
          error_rate_trend: Array.from({ length: days }, (_, i) => ({
            date: new Date(Date.now() - (days - i - 1) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            error_rate: 0.15 + Math.random() * 0.1 - (i * 0.001),
            total_questions: Math.floor(5 + Math.random() * 10),
            error_count: Math.floor((0.15 + Math.random() * 0.1) * (5 + Math.random() * 10))
          })),
          error_type_trends: [
            {
              error_type: "计算错误",
              trend: 'improving',
              frequency_change: -0.25,
              recent_count: 8,
              historical_average: 12.5
            },
            {
              error_type: "概念混淆",
              trend: 'stable',
              frequency_change: 0.02,
              recent_count: 5,
              historical_average: 4.8
            },
            {
              error_type: "公式误用",
              trend: 'improving',
              frequency_change: -0.18,
              recent_count: 3,
              historical_average: 6.2
            }
          ],
          systematic_improvements: [
            "计算准确率提升明显",
            "基础概念理解加深"
          ],
          persistent_issues: [
            "复杂应用题仍需加强",
            "注意审题细节"
          ]
        }
        resolve(mockTrends)
      }, 600)
    })
  },

  /**
   * Multi-Subject Summary - Mock multi-subject analysis
   */
  getMultiSubjectSummary(studentId: number, _subjects?: string[], _timeframeDays: number = 30): Promise<any> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockSummary: MultiSubjectSummary = {
          student_id: studentId,
          analysis_period: `最近${_timeframeDays}天`,
          overall_performance: {
            total_questions: 285,
            total_errors: 42,
            overall_accuracy: 0.853,
            improvement_trend: 'improving',
            grade_equivalent: "优秀"
          },
          subject_comparisons: [
            {
              subject: "数学",
              accuracy_rate: 0.862,
              error_count: 15,
              rank_among_subjects: 1,
              strength_level: 'strong',
              key_issues: ["复合函数理解需加强"]
            },
            {
              subject: "物理",
              accuracy_rate: 0.834,
              error_count: 18,
              rank_among_subjects: 2,
              strength_level: 'strong',
              key_issues: ["电路分析", "力学综合题"]
            },
            {
              subject: "英语",
              accuracy_rate: 0.876,
              error_count: 9,
              rank_among_subjects: 1,
              strength_level: 'strong',
              key_issues: ["语法选择题"]
            }
          ],
          cross_subject_patterns: [
            {
              pattern_type: "逻辑推理能力强",
              affected_subjects: ["数学", "物理"],
              description: "在需要逻辑推理的题目中表现优秀",
              severity: 'low',
              improvement_suggestions: ["继续保持，可尝试更具挑战性的题目"]
            },
            {
              pattern_type: "计算细心度有待提高",
              affected_subjects: ["数学", "物理"],
              description: "计算过程中偶有粗心错误",
              severity: 'medium',
              improvement_suggestions: ["建立检查习惯", "放慢计算速度"]
            }
          ],
          recommendations: [
            {
              priority: 'high',
              category: 'concept_review',
              description: "重点复习函数复合运算和电路基本定律",
              estimated_impact: "预计可提升整体成绩8-12分",
              time_investment: "每日30分钟，持续2周"
            },
            {
              priority: 'medium',
              category: 'practice_focus',
              description: "增加综合应用题练习，提高解题速度",
              estimated_impact: "提升解题效率20%",
              time_investment: "每周3次专项练习"
            }
          ]
        }
        resolve(mockSummary)
      }, 800)
    })
  },

  /**
   * Subject Progress - Mock subject progress data
   */
  getSubjectProgress(_studentId: number, _subject: string, _timeframeDays: number = 30): Promise<any> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockProgress: SubjectProgress = {
          student_id: _studentId,
          subject: _subject,
          total_questions: 95,
          correct_answers: 82,
          accuracy_rate: 0.863,
          improvement_rate: 0.125,
          knowledge_points: [
            {
              name: "二次函数",
              mastery_level: 85,
              total_practiced: 25,
              correct_count: 21,
              last_practiced: "2024-01-15T10:30:00Z",
              difficulty: 'medium'
            },
            {
              name: "几何证明",
              mastery_level: 78,
              total_practiced: 18,
              correct_count: 14,
              last_practiced: "2024-01-14T15:20:00Z",
              difficulty: 'hard'
            },
            {
              name: "代数运算",
              mastery_level: 92,
              total_practiced: 32,
              correct_count: 30,
              last_practiced: "2024-01-15T14:15:00Z",
              difficulty: 'easy'
            }
          ],
          recent_performance: Array.from({ length: 7 }, (_, i) => ({
            date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            score: 75 + Math.random() * 20,
            total: 100,
            accuracy: 0.75 + Math.random() * 0.2
          })),
          weak_areas: ["复合函数求值", "几何综合证明"],
          strengths: ["基础计算", "图形识别", "公式应用"]
        }
        resolve(mockProgress)
      }, 500)
    })
  },

  /**
   * Learning Trends - Mock learning trends data
   */
  getLearningTrends(studentId: number, days: number = 30): Promise<any> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const subjects = ['math', 'physics', 'english']
        const mockTrends: LearningTrend[] = subjects.map(subject => ({
          student_id: studentId,
          subject,
          time_period: 'month',
          trend_data: Array.from({ length: days }, (_, i) => ({
            date: new Date(Date.now() - (days - i - 1) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            accuracy_rate: 0.7 + Math.random() * 0.2 + (i * 0.005),
            questions_count: Math.floor(3 + Math.random() * 8),
            average_score: 70 + Math.random() * 20 + (i * 0.3),
            study_time_minutes: Math.floor(20 + Math.random() * 40)
          })),
          overall_trend: 'improving',
          prediction: {
            expected_improvement: 0.15,
            confidence_level: 0.82,
            recommended_actions: [
              "继续当前学习节奏",
              "增加薄弱环节练习",
              "定期回顾错题"
            ]
          }
        }))
        resolve(mockTrends)
      }, 700)
    })
  }

}

export default mockApiService
