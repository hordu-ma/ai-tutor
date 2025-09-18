<template>
    <div class="improvement-plan">
        <div v-if="plan" class="plan-content">
            <!-- Focus Areas -->
            <div class="section">
                <div class="section-header">
                    <el-icon class="section-icon"><Aim /></el-icon>
                    <h3 class="section-title">重点领域</h3>
                </div>
                <div class="focus-areas">
                    <el-tag
                        v-for="area in plan.focus_areas"
                        :key="area"
                        type="primary"
                        size="large"
                        class="focus-tag"
                    >
                        {{ area }}
                    </el-tag>
                </div>
            </div>

            <!-- Recommended Actions -->
            <div class="section">
                <div class="section-header">
                    <el-icon class="section-icon"><List /></el-icon>
                    <h3 class="section-title">推荐行动</h3>
                </div>
                <div class="actions-list">
                    <div
                        v-for="(action, index) in plan.recommended_actions"
                        :key="index"
                        class="action-item"
                    >
                        <div class="action-number">{{ index + 1 }}</div>
                        <div class="action-content">
                            <p class="action-text">{{ action }}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Plan Metadata -->
            <div class="plan-metadata">
                <el-row :gutter="16">
                    <el-col :span="12">
                        <div class="metadata-item">
                            <el-icon class="metadata-icon"><Trophy /></el-icon>
                            <div class="metadata-content">
                                <div class="metadata-label">难度等级</div>
                                <el-tag
                                    :type="getDifficultyType(plan.difficulty_level)"
                                    class="difficulty-tag"
                                >
                                    {{ plan.difficulty_level || "未知" }}
                                </el-tag>
                            </div>
                        </div>
                    </el-col>
                    <el-col :span="12">
                        <div class="metadata-item">
                            <el-icon class="metadata-icon"><Timer /></el-icon>
                            <div class="metadata-content">
                                <div class="metadata-label">预计时间</div>
                                <div class="metadata-value">
                                    {{ plan.estimated_time_weeks }} 周
                                </div>
                            </div>
                        </div>
                    </el-col>
                </el-row>
            </div>

            <!-- Progress Tracking -->
            <div class="section">
                <div class="section-header">
                    <el-icon class="section-icon"><TrendCharts /></el-icon>
                    <h3 class="section-title">进度跟踪</h3>
                </div>
                <div class="progress-container">
                    <div class="progress-info">
                        <span>计划进度</span>
                        <span class="progress-percentage">{{ planProgress }}%</span>
                    </div>
                    <el-progress
                        :percentage="planProgress"
                        :color="getProgressColor(planProgress)"
                        :stroke-width="8"
                    />
                    <div class="progress-actions">
                        <el-button
                            type="primary"
                            size="small"
                            @click="startPlan"
                            :disabled="isStarted"
                        >
                            {{ isStarted ? "计划进行中" : "开始计划" }}
                        </el-button>
                        <el-button
                            size="small"
                            @click="updateProgress"
                            :disabled="!isStarted"
                        >
                            更新进度
                        </el-button>
                    </div>
                </div>
            </div>
        </div>

        <div v-else class="no-plan">
            <el-empty description="该科目暂无改进计划" :image-size="80">
                <el-button type="primary" @click="generatePlan"> 生成计划 </el-button>
            </el-empty>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, computed } from "vue";
import { ElMessage } from "element-plus";
import { Aim, List, Trophy, Timer, TrendCharts } from "@element-plus/icons-vue";
import type { ImprovementPlan as ImprovementPlanType } from "@/services/api";

// Props
interface Props {
    plan?: ImprovementPlanType;
    subject: string;
}

const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
    generatePlan: [subject: string];
    startPlan: [subject: string];
    updateProgress: [subject: string, progress: number];
}>();

// Component state
const planProgress = ref(0);
const isStarted = ref(false);

// Computed properties
const getDifficultyType = computed(() => (difficulty: string | undefined) => {
    if (!difficulty) return "info";
    switch (difficulty.toLowerCase()) {
        case "easy":
        case "beginner":
        case "简单":
        case "初级":
            return "success";
        case "medium":
        case "intermediate":
        case "中等":
        case "中级":
            return "warning";
        case "hard":
        case "advanced":
        case "困难":
        case "高级":
            return "danger";
        default:
            return "info";
    }
});

const getProgressColor = computed(() => (progress: number) => {
    if (progress < 30) return "#f56c6c";
    if (progress < 70) return "#e6a23c";
    return "#67c23a";
});

// Methods
const startPlan = () => {
    isStarted.value = true;
    planProgress.value = 0;
    emit("startPlan", props.subject);
    ElMessage.success(`已开始${getSubjectDisplayName(props.subject)}改进计划！`);
};

const getSubjectDisplayName = (subject: string) => {
    switch (subject) {
        case "math":
            return "数学";
        case "physics":
            return "物理";
        case "english":
            return "英语";
        default:
            return subject;
    }
};

const updateProgress = () => {
    // In a real app, this would open a dialog to update progress
    const newProgress = Math.min(planProgress.value + 20, 100);
    planProgress.value = newProgress;
    emit("updateProgress", props.subject, newProgress);

    if (newProgress === 100) {
        ElMessage.success("恭喜！您已完成此改进计划！");
    } else {
        ElMessage.info(`进度已更新：${newProgress}%`);
    }
};

const generatePlan = () => {
    emit("generatePlan", props.subject);
    ElMessage.info(`正在生成${getSubjectDisplayName(props.subject)}改进计划...`);
};
</script>

<style scoped>
.improvement-plan {
    min-height: 200px;
}

.plan-content {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.section {
    background: #fafafa;
    border-radius: 8px;
    padding: 20px;
    border: 1px solid #e8e8e8;
}

.section-header {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
}

.section-icon {
    margin-right: 8px;
    color: #1890ff;
    font-size: 18px;
}

.section-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
}

.focus-areas {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.focus-tag {
    font-size: 14px;
    padding: 8px 16px;
    border-radius: 16px;
}

.actions-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.action-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 16px;
    background: white;
    border-radius: 6px;
    border: 1px solid #e8e8e8;
}

.action-number {
    width: 28px;
    height: 28px;
    background: #1890ff;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
    flex-shrink: 0;
}

.action-content {
    flex: 1;
}

.action-text {
    margin: 0;
    line-height: 1.6;
    color: #606266;
}

.plan-metadata {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    border: 1px solid #e8e8e8;
}

.metadata-item {
    display: flex;
    align-items: center;
    gap: 12px;
}

.metadata-icon {
    font-size: 20px;
    color: #1890ff;
}

.metadata-content {
    flex: 1;
}

.metadata-label {
    font-size: 12px;
    color: #909399;
    margin-bottom: 4px;
}

.metadata-value {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
}

.difficulty-tag {
    font-weight: 600;
}

.progress-container {
    background: white;
    border-radius: 6px;
    padding: 16px;
    border: 1px solid #e8e8e8;
}

.progress-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-weight: 600;
}

.progress-percentage {
    color: #1890ff;
}

.progress-actions {
    display: flex;
    gap: 12px;
    margin-top: 16px;
    justify-content: flex-start;
}

.no-plan {
    min-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Responsive design */
@media (max-width: 768px) {
    .plan-metadata .el-row {
        gap: 16px;
    }

    .plan-metadata .el-col {
        width: 100%;
        margin-bottom: 16px;
    }

    .focus-areas {
        justify-content: center;
    }

    .progress-actions {
        flex-direction: column;
    }

    .progress-actions .el-button {
        width: 100%;
    }
}
</style>
