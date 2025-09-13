<template>
    <div class="quick-analysis-container">
        <el-card class="analysis-card">
            <template #header>
                <div class="card-header">
                    <el-icon class="header-icon"><Lightning /></el-icon>
                    <span class="header-title">单题快速分析</span>
                </div>
            </template>

            <div class="analysis-content">
                <el-form
                    ref="formRef"
                    :model="form"
                    :rules="rules"
                    label-width="140px"
                    class="analysis-form"
                >
                    <el-form-item label="学科" prop="subject">
                        <el-select
                            v-model="form.subject"
                            placeholder="选择学科"
                            style="width: 100%"
                        >
                            <el-option label="数学" value="math" />
                            <el-option label="物理" value="physics" />
                            <el-option label="英语" value="english" />
                        </el-select>
                    </el-form-item>

                    <el-form-item label="题目" prop="question_text">
                        <el-input
                            v-model="form.question_text"
                            type="textarea"
                            :rows="3"
                            placeholder="请输入题目..."
                            show-word-limit
                            maxlength="500"
                        />
                    </el-form-item>

                    <el-form-item label="学生答案" prop="student_answer">
                        <el-input
                            v-model="form.student_answer"
                            type="textarea"
                            :rows="2"
                            placeholder="请输入学生的答案..."
                            show-word-limit
                            maxlength="200"
                        />
                    </el-form-item>

                    <el-form-item label="正确答案" prop="correct_answer">
                        <el-input
                            v-model="form.correct_answer"
                            type="textarea"
                            :rows="2"
                            placeholder="请输入正确答案..."
                            show-word-limit
                            maxlength="200"
                        />
                    </el-form-item>

                    <el-form-item>
                        <el-button
                            type="primary"
                            @click="analyzeQuestion"
                            :loading="isAnalyzing"
                            :disabled="!isFormValid"
                            size="large"
                        >
                            <el-icon><Search /></el-icon>
                            {{ isAnalyzing ? "分析中..." : "开始分析" }}
                        </el-button>
                        <el-button @click="resetForm" size="large">
                            <el-icon><Refresh /></el-icon>
                            重置
                        </el-button>
                    </el-form-item>
                </el-form>

                <!-- Analysis Results -->
                <div v-if="analysisResult" class="analysis-results">
                    <el-divider>
                        <el-icon><DataAnalysis /></el-icon>
                        分析结果
                    </el-divider>

                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-card shadow="never" class="result-card">
                                <template #header>
                                    <div class="result-header">
                                        <el-icon class="result-icon error-type"
                                            ><Warning
                                        /></el-icon>
                                        <span>错误分类</span>
                                    </div>
                                </template>
                                <div class="error-info">
                                    <el-tag
                                        :type="
                                            getErrorSeverityType(
                                                analysisResult.error_severity,
                                            )
                                        "
                                        size="large"
                                        class="error-tag"
                                    >
                                        {{ analysisResult.error_type }}
                                    </el-tag>
                                    <div class="severity">
                                        <span class="severity-label">严重程度: </span>
                                        <el-tag
                                            :type="
                                                getErrorSeverityType(
                                                    analysisResult.error_severity,
                                                )
                                            "
                                        >
                                            {{
                                                analysisResult.error_severity.toUpperCase()
                                            }}
                                        </el-tag>
                                    </div>
                                </div>
                            </el-card>
                        </el-col>

                        <el-col :span="12">
                            <el-card shadow="never" class="result-card">
                                <template #header>
                                    <div class="result-header">
                                        <el-icon class="result-icon explanation"
                                            ><Document
                                        /></el-icon>
                                        <span>详细解释</span>
                                    </div>
                                </template>
                                <div class="explanation-content">
                                    {{ analysisResult.explanation }}
                                </div>
                            </el-card>
                        </el-col>
                    </el-row>

                    <el-row :gutter="20" style="margin-top: 20px">
                        <el-col :span="12">
                            <el-card shadow="never" class="result-card">
                                <template #header>
                                    <div class="result-header">
                                        <el-icon class="result-icon suggestions"
                                            ><Star
                                        /></el-icon>
                                        <span>改进建议</span>
                                    </div>
                                </template>
                                <ul class="suggestions-list">
                                    <li
                                        v-for="(
                                            suggestion, index
                                        ) in analysisResult.improvement_suggestions"
                                        :key="index"
                                        class="suggestion-item"
                                    >
                                        <el-icon class="suggestion-icon"
                                            ><Right
                                        /></el-icon>
                                        {{ suggestion }}
                                    </li>
                                </ul>
                            </el-card>
                        </el-col>

                        <el-col :span="12">
                            <el-card shadow="never" class="result-card">
                                <template #header>
                                    <div class="result-header">
                                        <el-icon class="result-icon concepts"
                                            ><Connection
                                        /></el-icon>
                                        <span>相关概念</span>
                                    </div>
                                </template>
                                <div class="concepts-container">
                                    <el-tag
                                        v-for="(
                                            concept, index
                                        ) in analysisResult.related_concepts"
                                        :key="index"
                                        class="concept-tag"
                                        type="info"
                                    >
                                        {{ concept }}
                                    </el-tag>
                                </div>
                            </el-card>
                        </el-col>
                    </el-row>
                </div>

                <!-- Error State -->
                <div v-if="errorMessage" class="error-state">
                    <el-alert
                        :title="errorMessage"
                        type="error"
                        show-icon
                        :closable="false"
                    />
                </div>
            </div>
        </el-card>

        <!-- Demo Examples -->
        <el-card class="demo-card" style="margin-top: 20px">
            <template #header>
                <div class="card-header">
                    <el-icon class="header-icon"><Edit /></el-icon>
                    <span class="header-title">快速示例</span>
                </div>
            </template>

            <div class="demo-examples">
                <el-button
                    v-for="example in demoExamples"
                    :key="example.subject"
                    @click="loadExample(example)"
                    class="demo-button"
                    plain
                >
                    试试{{ getSubjectLabel(example.subject) }}示例
                </el-button>
            </div>
        </el-card>
    </div>
</template>

<script lang="ts" setup>
import { ref, computed } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import {
    Lightning,
    Search,
    Refresh,
    DataAnalysis,
    Warning,
    Document,
    Star,
    Right,
    Connection,
    Edit,
} from "@element-plus/icons-vue";
import {
    apiService,
    type ErrorAnalysisRequest,
    type ErrorAnalysisResponse,
} from "@/services/api";

// Form data
const form = ref<ErrorAnalysisRequest>({
    subject: "math",
    question_text: "",
    student_answer: "",
    correct_answer: "",
});

// Form validation rules
const rules: FormRules = {
    subject: [{ required: true, message: "请选择学科", trigger: "change" }],
    question_text: [
        { required: true, message: "请输入题目内容", trigger: "blur" },
        {
            min: 5,
            message: "题目内容至少需要5个字符",
            trigger: "blur",
        },
    ],
    student_answer: [
        { required: true, message: "请输入学生答案", trigger: "blur" },
        { min: 1, message: "学生答案不能为空", trigger: "blur" },
    ],
    correct_answer: [
        { required: true, message: "请输入正确答案", trigger: "blur" },
        { min: 1, message: "正确答案不能为空", trigger: "blur" },
    ],
};

// Component state
const formRef = ref<FormInstance>();
const isAnalyzing = ref(false);
const analysisResult = ref<ErrorAnalysisResponse | null>(null);
const errorMessage = ref("");

// Computed properties
const isFormValid = computed(() => {
    return (
        form.value.subject &&
        form.value.question_text &&
        form.value.student_answer &&
        form.value.correct_answer
    );
});

// Demo examples
const demoExamples = [
    {
        subject: "math" as const,
        question_text: "求解方程：2x + 3 = 7",
        student_answer: "x = 3",
        correct_answer: "x = 2",
    },
    {
        subject: "physics" as const,
        question_text: "一辆汽车在2小时内行驶了60公里，它的平均速度是多少？",
        student_answer: "120 km/h",
        correct_answer: "30 km/h",
    },
    {
        subject: "english" as const,
        question_text: '选择正确的形式：\"She _____ to school every day.\"',
        student_answer: "go",
        correct_answer: "goes",
    },
];

// Methods
const analyzeQuestion = async () => {
    if (!formRef.value) return;

    try {
        await formRef.value.validate();
    } catch (error) {
        ElMessage.warning("请正确填写所有必填字段");
        return;
    }

    isAnalyzing.value = true;
    errorMessage.value = "";

    try {
        const result = await apiService.analyzeQuestionError(form.value);
        analysisResult.value = result;
        ElMessage.success("分析完成！");
    } catch (error) {
        console.error("Analysis failed:", error);
        errorMessage.value = "分析失败，请重试。";
        ElMessage.error("分析失败，请检查网络连接后重试。");
    } finally {
        isAnalyzing.value = false;
    }
};

const resetForm = () => {
    if (formRef.value) {
        formRef.value.resetFields();
    }
    analysisResult.value = null;
    errorMessage.value = "";
};

const getSubjectLabel = (subject: string) => {
    const labels = {
        math: "数学",
        physics: "物理",
        english: "英语",
    };
    return labels[subject as keyof typeof labels] || subject;
};

const loadExample = (example: (typeof demoExamples)[0]) => {
    form.value = { ...example };
    analysisResult.value = null;
    errorMessage.value = "";
    ElMessage.info(`已加载${getSubjectLabel(example.subject)}示例`);
};

const getErrorSeverityType = (severity: string) => {
    switch (severity) {
        case "high":
            return "danger";
        case "medium":
            return "warning";
        case "low":
            return "success";
        default:
            return "info";
    }
};
</script>

<style scoped>
.quick-analysis-container {
    max-width: 1200px;
    margin: 0 auto;
}

.analysis-card {
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
    color: #303133;
}

.header-icon {
    margin-right: 8px;
    color: #1890ff;
}

.header-title {
    color: #303133;
}

.analysis-content {
    padding: 20px 0;
}

.analysis-form {
    max-width: 800px;
}

.analysis-results {
    margin-top: 30px;
}

.result-card {
    border: 1px solid #e8e8e8;
    border-radius: 6px;
}

.result-header {
    display: flex;
    align-items: center;
    font-weight: 600;
    color: #303133;
}

.result-icon {
    margin-right: 6px;
}

.result-icon.error-type {
    color: #f56c6c;
}
.result-icon.explanation {
    color: #409eff;
}
.result-icon.suggestions {
    color: #67c23a;
}
.result-icon.concepts {
    color: #e6a23c;
}

.error-info {
    padding: 10px 0;
}

.error-tag {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 10px;
}

.severity {
    display: flex;
    align-items: center;
    margin-top: 10px;
}

.severity-label {
    font-weight: 600;
    margin-right: 8px;
}

.explanation-content {
    line-height: 1.6;
    color: #606266;
    padding: 10px 0;
}

.suggestions-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.suggestion-item {
    display: flex;
    align-items: flex-start;
    margin-bottom: 8px;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
    line-height: 1.5;
}

.suggestion-item:last-child {
    border-bottom: none;
}

.suggestion-icon {
    color: #67c23a;
    margin-right: 8px;
    margin-top: 2px;
    flex-shrink: 0;
}

.concepts-container {
    padding: 10px 0;
}

.concept-tag {
    margin: 4px 6px 4px 0;
}

.error-state {
    margin-top: 20px;
}

.demo-card {
    border-radius: 8px;
}

.demo-examples {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.demo-button {
    margin: 4px 0;
}

/* Responsive design */
@media (max-width: 768px) {
    .analysis-form {
        max-width: 100%;
    }

    .demo-examples {
        flex-direction: column;
    }

    .demo-button {
        width: 100%;
    }
}
</style>
