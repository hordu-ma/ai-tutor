<template>
    <div class="homework-upload-container">
        <!-- Header Section -->
        <el-card class="upload-header">
            <div class="header-content">
                <div class="header-text">
                    <h2 class="header-title">
                        <el-icon class="title-icon"><UploadFilled /></el-icon>
                        作业批改
                    </h2>
                    <p class="header-subtitle">
                        上传作业图片，获取AI智能批改和详细分析
                    </p>
                </div>
                <div class="header-stats">
                    <div class="stat-card">
                        <div class="stat-number">{{ totalUploads }}</div>
                        <div class="stat-label">今日批改</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ averageScore }}%</div>
                        <div class="stat-label">平均得分</div>
                    </div>
                </div>
            </div>
        </el-card>

        <!-- Upload Form Section -->
        <el-card class="upload-form-card">
            <template #header>
                <div class="form-header">
                    <h3>📝 上传作业</h3>
                    <el-tag type="info" size="small"
                        >支持 JPG、PNG、WEBP 格式，最大 10MB</el-tag
                    >
                </div>
            </template>

            <el-form
                ref="uploadFormRef"
                :model="uploadForm"
                :rules="uploadRules"
                label-width="100px"
                @submit.prevent="handleSubmit"
            >
                <el-row :gutter="20">
                    <el-col :lg="12" :md="24">
                        <el-form-item label="选择科目" prop="subject" required>
                            <el-select
                                v-model="uploadForm.subject"
                                placeholder="请选择科目"
                                style="width: 100%"
                            >
                                <el-option label="数学" value="math">
                                    <span>📐 数学</span>
                                </el-option>
                                <el-option label="物理" value="physics">
                                    <el-icon><Lightning /></el-icon>
                                    <span style="margin-left: 8px">物理</span>
                                </el-option>
                                <el-option label="英语" value="english">
                                    <el-icon><ChatDotRound /></el-icon>
                                    <span style="margin-left: 8px">英语</span>
                                </el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>

                    <el-col :lg="12" :md="24">
                        <el-form-item label="AI模型" prop="provider">
                            <el-select
                                v-model="uploadForm.provider"
                                placeholder="选择AI模型"
                                style="width: 100%"
                            >
                                <el-option label="通义千问" value="qwen">
                                    <span>🤖 通义千问</span>
                                </el-option>
                                <el-option label="Kimi" value="kimi">
                                    <span>🚀 Kimi</span>
                                </el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-form-item label="作业图片" prop="file" required>
                    <el-upload
                        ref="uploadRef"
                        class="upload-area"
                        drag
                        :auto-upload="false"
                        :show-file-list="false"
                        :accept="acceptedFileTypes"
                        :before-upload="beforeUpload"
                        :on-change="handleFileChange"
                        :limit="1"
                    >
                        <div v-if="!selectedFile" class="upload-placeholder">
                            <el-icon class="upload-icon"><Plus /></el-icon>
                            <div class="upload-text">
                                <p class="upload-hint">将作业图片拖拽到此处或</p>
                                <p class="upload-action">点击上传</p>
                            </div>
                        </div>
                        <div v-else class="file-preview">
                            <img
                                :src="previewUrl"
                                alt="预览图片"
                                class="preview-image"
                            />
                            <div class="file-info">
                                <p class="file-name">{{ selectedFile.name }}</p>
                                <p class="file-size">
                                    {{ formatFileSize(selectedFile.size) }}
                                </p>
                                <el-button
                                    type="danger"
                                    size="small"
                                    text
                                    @click="removeFile"
                                >
                                    <el-icon><Delete /></el-icon>
                                    移除
                                </el-button>
                            </div>
                        </div>
                    </el-upload>
                </el-form-item>

                <el-form-item>
                    <div class="form-actions">
                        <el-button
                            type="primary"
                            size="large"
                            :loading="isUploading"
                            :disabled="!canSubmit"
                            @click="handleSubmit"
                        >
                            <el-icon v-if="!isUploading"><Upload /></el-icon>
                            {{ isUploading ? "批改中..." : "开始批改" }}
                        </el-button>
                        <el-button size="large" @click="resetForm">
                            <el-icon><Refresh /></el-icon>
                            重置
                        </el-button>
                    </div>
                </el-form-item>
            </el-form>
        </el-card>

        <!-- Result Section -->
        <el-card
            v-if="showResult"
            class="result-card"
            v-loading="isUploading"
            element-loading-text="AI正在分析作业中..."
        >
            <template #header>
                <div class="result-header">
                    <h3>📊 批改结果</h3>
                    <div class="result-actions">
                        <el-button type="success" size="small" @click="saveReport">
                            <el-icon><Download /></el-icon>
                            保存报告
                        </el-button>
                        <el-button size="small" @click="startNewAnalysis">
                            <el-icon><Plus /></el-icon>
                            新建分析
                        </el-button>
                    </div>
                </div>
            </template>

            <div v-if="analysisResult" class="result-content">
                <!-- 成绩概览 -->
                <div class="grade-overview">
                    <div class="grade-card">
                        <div
                            class="grade-score"
                            :class="getGradeClass(analysisResult.total_score)"
                        >
                            {{ analysisResult.total_score }}
                        </div>
                        <div class="grade-label">总分</div>
                    </div>
                    <div class="grade-details">
                        <el-descriptions :column="2" size="small">
                            <el-descriptions-item label="科目">
                                <el-tag
                                    :type="
                                        getSubjectTagType(analysisResult.subject) as any
                                    "
                                >
                                    {{ getSubjectLabel(analysisResult.subject) }}
                                </el-tag>
                            </el-descriptions-item>
                            <el-descriptions-item label="批改时间">
                                {{ formatDate(analysisResult.analyzed_at) }}
                            </el-descriptions-item>
                            <el-descriptions-item label="错题数量">
                                <el-tag
                                    type="danger"
                                    v-if="analysisResult.error_count > 0"
                                >
                                    {{ analysisResult.error_count }} 题
                                </el-tag>
                                <el-tag type="success" v-else>全部正确</el-tag>
                            </el-descriptions-item>
                            <el-descriptions-item label="掌握程度">
                                <el-progress
                                    :percentage="analysisResult.mastery_level"
                                    :color="
                                        getProgressColor(analysisResult.mastery_level)
                                    "
                                    :stroke-width="8"
                                />
                            </el-descriptions-item>
                        </el-descriptions>
                    </div>
                </div>

                <!-- 详细分析 -->
                <el-divider>详细分析</el-divider>

                <el-tabs v-model="activeTab" class="result-tabs">
                    <el-tab-pane label="错题分析" name="errors">
                        <div
                            v-if="
                                analysisResult.errors &&
                                analysisResult.errors.length > 0
                            "
                        >
                            <div
                                v-for="(error, index) in analysisResult.errors"
                                :key="index"
                                class="error-item"
                            >
                                <div class="error-header">
                                    <el-tag type="danger" size="small"
                                        >第{{ error.question_number }}题</el-tag
                                    >
                                    <span class="error-type">{{
                                        error.error_type
                                    }}</span>
                                </div>
                                <div class="error-content">
                                    <p><strong>错误原因：</strong>{{ error.reason }}</p>
                                    <p>
                                        <strong>正确解答：</strong
                                        >{{ error.correct_answer }}
                                    </p>
                                    <p>
                                        <strong>解题思路：</strong
                                        >{{ error.explanation }}
                                    </p>
                                </div>
                            </div>
                        </div>
                        <el-empty v-else description="恭喜！没有发现错误" />
                    </el-tab-pane>

                    <el-tab-pane label="知识点掌握" name="knowledge">
                        <div v-if="analysisResult.knowledge_points">
                            <div
                                v-for="(
                                    point, index
                                ) in analysisResult.knowledge_points"
                                :key="index"
                                class="knowledge-item"
                            >
                                <div class="knowledge-header">
                                    <span class="knowledge-name">{{ point.name }}</span>
                                    <el-tag
                                        :type="
                                            getMasteryTagType(
                                                point.mastery_level,
                                            ) as any
                                        "
                                        size="small"
                                    >
                                        {{ getMasteryLabel(point.mastery_level) }}
                                    </el-tag>
                                </div>
                                <el-progress
                                    :percentage="point.score"
                                    :color="getProgressColor(point.score)"
                                />
                                <p class="knowledge-suggestion">
                                    {{ point.suggestion }}
                                </p>
                            </div>
                        </div>
                    </el-tab-pane>

                    <el-tab-pane label="改进建议" name="suggestions">
                        <div v-if="analysisResult.improvement_plan">
                            <div class="improvement-section">
                                <h4>📈 学习建议</h4>
                                <ul class="suggestion-list">
                                    <li
                                        v-for="(suggestion, index) in analysisResult
                                            .improvement_plan.suggestions"
                                        :key="index"
                                    >
                                        {{ suggestion }}
                                    </li>
                                </ul>
                            </div>

                            <div class="improvement-section">
                                <h4>📚 推荐练习</h4>
                                <div class="practice-items">
                                    <el-tag
                                        v-for="(practice, index) in analysisResult
                                            .improvement_plan.recommended_practice"
                                        :key="index"
                                        class="practice-tag"
                                    >
                                        {{ practice }}
                                    </el-tag>
                                </div>
                            </div>
                        </div>
                    </el-tab-pane>
                </el-tabs>
            </div>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import {
    ElMessage,
    type FormInstance,
    type FormRules,
    type UploadFile,
} from "element-plus";
import {
    UploadFilled,
    Plus,
    Upload,
    Delete,
    Refresh,
    Download,
    Lightning,
    ChatDotRound,
} from "@element-plus/icons-vue";
import { homeworkService } from "@/services/api";
import type { HomeworkAnalysis } from "@/types/homework";

// 响应式数据
const uploadFormRef = ref<FormInstance>();
const uploadRef = ref();
const isUploading = ref(false);
const showResult = ref(false);
const selectedFile = ref<File | null>(null);
const previewUrl = ref("");
const analysisResult = ref<HomeworkAnalysis | null>(null);
const activeTab = ref("errors");

// 统计数据
const totalUploads = ref(5);
const averageScore = ref(85);

// 表单数据
const uploadForm = reactive({
    subject: "math",
    provider: "qwen",
    file: null as File | null,
});

// 表单验证规则
const uploadRules: FormRules = {
    subject: [{ required: true, message: "请选择科目", trigger: "change" }],
    provider: [{ required: true, message: "请选择AI模型", trigger: "change" }],
};

// 计算属性
const acceptedFileTypes = computed(() => "image/jpeg,image/jpg,image/png,image/webp");

const canSubmit = computed(() => {
    return (
        uploadForm.subject &&
        uploadForm.provider &&
        selectedFile.value &&
        !isUploading.value
    );
});

// 方法
const beforeUpload = (file: File) => {
    const isValidType = ["image/jpeg", "image/jpg", "image/png", "image/webp"].includes(
        file.type,
    );
    const isValidSize = file.size / 1024 / 1024 < 10;

    if (!isValidType) {
        ElMessage.error("只支持 JPG、PNG、WEBP 格式的图片!");
        return false;
    }
    if (!isValidSize) {
        ElMessage.error("图片大小不能超过 10MB!");
        return false;
    }
    return false; // 阻止自动上传
};

const handleFileChange = (file: UploadFile) => {
    if (file.raw) {
        selectedFile.value = file.raw;
        uploadForm.file = file.raw;

        // 创建预览URL
        const reader = new FileReader();
        reader.onload = (e) => {
            previewUrl.value = e.target?.result as string;
        };
        reader.readAsDataURL(file.raw);
    }
};

const removeFile = () => {
    selectedFile.value = null;
    uploadForm.file = null;
    previewUrl.value = "";
    uploadRef.value?.clearFiles();
};

const formatFileSize = (size: number) => {
    if (size < 1024) return size + " B";
    if (size < 1024 * 1024) return (size / 1024).toFixed(1) + " KB";
    return (size / 1024 / 1024).toFixed(1) + " MB";
};

const handleSubmit = async () => {
    if (!uploadFormRef.value) return;

    try {
        const valid = await uploadFormRef.value.validate();
        if (!valid || !selectedFile.value) return;

        isUploading.value = true;
        showResult.value = true;

        const formData = new FormData();
        formData.append("file", selectedFile.value);
        formData.append("subject", uploadForm.subject);
        formData.append("provider", uploadForm.provider);

        const result = await homeworkService.gradeHomework(formData);

        analysisResult.value = result;
        ElMessage.success("作业批改完成！");

        // 更新统计数据
        totalUploads.value += 1;
    } catch (error) {
        console.error("上传失败:", error);
        ElMessage.error("批改失败，请重试");
        showResult.value = false;
    } finally {
        isUploading.value = false;
    }
};

const resetForm = () => {
    uploadFormRef.value?.resetFields();
    removeFile();
    showResult.value = false;
    analysisResult.value = null;
};

const startNewAnalysis = () => {
    resetForm();
    window.scrollTo({ top: 0, behavior: "smooth" });
};

const saveReport = async () => {
    if (!analysisResult.value) return;

    try {
        const reportData = await homeworkService.generateReport(
            analysisResult.value.id,
        );

        // 创建下载链接
        const blob = new Blob([reportData], { type: "application/pdf" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `批改报告_${formatDate(analysisResult.value.analyzed_at)}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        ElMessage.success("报告下载成功！");
    } catch (error) {
        console.error("保存报告失败:", error);
        ElMessage.error("保存报告失败，请重试");
    }
};

// 工具函数
const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString("zh-CN");
};

const getSubjectLabel = (subject: string) => {
    const labels = { math: "数学", physics: "物理", english: "英语" };
    return labels[subject as keyof typeof labels] || subject;
};

const getSubjectTagType = (subject: string) => {
    const types = { math: "primary", physics: "success", english: "warning" };
    return types[subject as keyof typeof types] || "info";
};

const getGradeClass = (score: number) => {
    if (score >= 90) return "grade-excellent";
    if (score >= 80) return "grade-good";
    if (score >= 70) return "grade-fair";
    return "grade-poor";
};

const getProgressColor = (percentage: number) => {
    if (percentage >= 80) return "#67c23a";
    if (percentage >= 60) return "#e6a23c";
    return "#f56c6c";
};

const getMasteryTagType = (level: string) => {
    const types = {
        excellent: "success",
        good: "primary",
        fair: "warning",
        poor: "danger",
    };
    return types[level as keyof typeof types] || "info";
};

const getMasteryLabel = (level: string) => {
    const labels = {
        excellent: "优秀",
        good: "良好",
        fair: "一般",
        poor: "待提高",
    };
    return labels[level as keyof typeof labels] || level;
};

// 初始化
onMounted(() => {
    // 可以在这里加载一些初始数据
});
</script>

<style scoped>
.homework-upload-container {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

/* Header Styles */
.upload-header {
    margin-bottom: 20px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
}

.header-text {
    flex: 1;
    min-width: 300px;
}

.header-title {
    display: flex;
    align-items: center;
    margin: 0 0 8px 0;
    font-size: 24px;
    font-weight: 600;
    color: var(--el-text-color-primary);
}

.title-icon {
    margin-right: 12px;
    color: var(--el-color-primary);
}

.header-subtitle {
    margin: 0;
    color: var(--el-text-color-regular);
    font-size: 14px;
}

.header-stats {
    display: flex;
    gap: 20px;
}

.stat-card {
    text-align: center;
    padding: 16px;
    background: linear-gradient(
        135deg,
        var(--el-color-primary-light-9),
        var(--el-color-primary-light-8)
    );
    border-radius: 8px;
    min-width: 100px;
}

.stat-number {
    font-size: 24px;
    font-weight: 700;
    color: var(--el-color-primary);
    margin-bottom: 4px;
}

.stat-label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
}

/* Form Styles */
.upload-form-card {
    margin-bottom: 20px;
}

.form-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.form-header h3 {
    margin: 0;
    font-size: 18px;
}

.upload-area {
    width: 100%;
}

.upload-area :deep(.el-upload) {
    width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
    width: 100%;
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.upload-placeholder {
    text-align: center;
}

.upload-icon {
    font-size: 48px;
    color: var(--el-color-primary);
    margin-bottom: 16px;
}

.upload-text {
    color: var(--el-text-color-regular);
}

.upload-hint {
    margin: 0 0 4px 0;
    font-size: 14px;
}

.upload-action {
    margin: 0;
    font-weight: 500;
    color: var(--el-color-primary);
}

.file-preview {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    width: 100%;
}

.preview-image {
    max-width: 120px;
    max-height: 120px;
    border-radius: 8px;
    object-fit: cover;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.file-info {
    flex: 1;
}

.file-name {
    margin: 0 0 4px 0;
    font-weight: 500;
    color: var(--el-text-color-primary);
}

.file-size {
    margin: 0 0 8px 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
}

.form-actions {
    display: flex;
    gap: 12px;
}

/* Result Styles */
.result-card {
    margin-bottom: 20px;
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.result-header h3 {
    margin: 0;
}

.result-actions {
    display: flex;
    gap: 8px;
}

.grade-overview {
    display: flex;
    gap: 24px;
    align-items: center;
    margin-bottom: 24px;
    padding: 20px;
    background: var(--el-color-info-light-9);
    border-radius: 8px;
}

.grade-card {
    text-align: center;
    min-width: 120px;
}

.grade-score {
    font-size: 48px;
    font-weight: 700;
    margin-bottom: 8px;
}

.grade-excellent {
    color: var(--el-color-success);
}
.grade-good {
    color: var(--el-color-primary);
}
.grade-fair {
    color: var(--el-color-warning);
}
.grade-poor {
    color: var(--el-color-danger);
}

.grade-label {
    font-size: 14px;
    color: var(--el-text-color-secondary);
}

.grade-details {
    flex: 1;
}

.result-tabs {
    margin-top: 20px;
}

.error-item {
    margin-bottom: 20px;
    padding: 16px;
    border: 1px solid var(--el-border-color-light);
    border-radius: 8px;
    background: var(--el-color-danger-light-9);
}

.error-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.error-type {
    font-weight: 500;
    color: var(--el-text-color-primary);
}

.error-content p {
    margin: 8px 0;
    line-height: 1.6;
}

.knowledge-item {
    margin-bottom: 20px;
    padding: 16px;
    border: 1px solid var(--el-border-color-light);
    border-radius: 8px;
}

.knowledge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.knowledge-name {
    font-weight: 500;
    color: var(--el-text-color-primary);
}

.knowledge-suggestion {
    margin: 8px 0 0 0;
    font-size: 13px;
    color: var(--el-text-color-regular);
    line-height: 1.5;
}

.improvement-section {
    margin-bottom: 24px;
}

.improvement-section h4 {
    margin: 0 0 12px 0;
    color: var(--el-text-color-primary);
}

.suggestion-list {
    margin: 0;
    padding-left: 20px;
}

.suggestion-list li {
    margin-bottom: 8px;
    line-height: 1.6;
}

.practice-items {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.practice-tag {
    margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .homework-upload-container {
        padding: 16px;
    }

    .header-content {
        flex-direction: column;
        align-items: flex-start;
    }

    .header-stats {
        width: 100%;
        justify-content: space-around;
    }

    .grade-overview {
        flex-direction: column;
        text-align: center;
    }

    .file-preview {
        flex-direction: column;
        text-align: center;
    }

    .form-actions {
        flex-direction: column;
    }

    .result-actions {
        flex-direction: column;
        gap: 4px;
    }
}

@media (max-width: 480px) {
    .stat-card {
        padding: 12px;
        min-width: 80px;
    }

    .stat-number {
        font-size: 20px;
    }

    .grade-score {
        font-size: 36px;
    }
}
</style>
