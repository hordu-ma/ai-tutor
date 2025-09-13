<template>
    <div class="dashboard-container">
        <!-- Welcome Section -->
        <el-card class="welcome-card">
            <div class="welcome-content">
                <div class="welcome-text">
                    <h2 class="welcome-title">欢迎回来，{{ studentName }}！ 📚</h2>
                    <p class="welcome-subtitle">追踪您的学习进度并获得个性化见解</p>
                </div>
                <div class="welcome-stats">
                    <div class="stat-item">
                        <div class="stat-number">{{ totalAssignments }}</div>
                        <div class="stat-label">已完成作业</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{ averageScore }}%</div>
                        <div class="stat-label">平均分</div>
                    </div>
                </div>
            </div>
        </el-card>

        <!-- Main Dashboard Content -->
        <el-row :gutter="24" style="margin-top: 20px">
            <!-- Knowledge Mastery Radar Chart -->
            <el-col :xl="12" :lg="24">
                <el-card class="chart-card">
                    <template #header>
                        <div class="card-header">
                            <el-icon><DataAnalysis /></el-icon>
                            <span>知识点掌握情况</span>
                        </div>
                    </template>
                    <div class="chart-container">
                        <div
                            v-if="isLoadingKnowledge"
                            class="loading-placeholder"
                            v-loading="true"
                            element-loading-text="正在加载知识点..."
                        />
                        <div v-else-if="knowledgeError" class="error-placeholder">
                            <el-empty description="无法加载知识点数据" :image-size="60">
                                <el-button type="primary" @click="loadKnowledgeData">
                                    重试
                                </el-button>
                            </el-empty>
                        </div>
                        <div v-else class="knowledge-mastery">
                            <div class="subject-tabs">
                                <el-radio-group
                                    v-model="selectedSubject"
                                    @change="handleSubjectChange"
                                >
                                    <el-radio-button label="math">数学</el-radio-button>
                                    <el-radio-button label="physics"
                                        >物理</el-radio-button
                                    >
                                    <el-radio-button label="english"
                                        >英语</el-radio-button
                                    >
                                </el-radio-group>
                            </div>
                            <div class="mastery-grid">
                                <div
                                    v-for="point in filteredKnowledgePoints"
                                    :key="point.id"
                                    class="mastery-item"
                                >
                                    <div class="mastery-header">
                                        <span class="point-name">{{ point.name }}</span>
                                        <span class="mastery-score"
                                            >{{ point.mastery_level }}%</span
                                        >
                                    </div>
                                    <el-progress
                                        :percentage="point.mastery_level"
                                        :color="getMasteryColor(point.mastery_level)"
                                        :show-text="false"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>

            <!-- Error Patterns Analysis -->
            <el-col :xl="12" :lg="24">
                <el-card class="chart-card">
                    <template #header>
                        <div class="card-header">
                            <el-icon><Warning /></el-icon>
                            <span>近期错误模式</span>
                            <el-select
                                v-model="errorPatternTimeframe"
                                @change="loadErrorPatterns"
                                size="small"
                                style="margin-left: auto; width: 120px"
                            >
                                <el-option label="最近7天" :value="7" />
                                <el-option label="最近30天" :value="30" />
                                <el-option label="最近90天" :value="90" />
                            </el-select>
                        </div>
                    </template>
                    <div class="error-patterns-container">
                        <div
                            v-if="isLoadingErrors"
                            class="loading-placeholder"
                            v-loading="true"
                            element-loading-text="正在加载错误模式..."
                        />
                        <div v-else-if="errorPatterns.length === 0" class="no-data">
                            <el-empty description="未找到错误模式" :image-size="60" />
                        </div>
                        <div v-else class="error-patterns-list">
                            <div
                                v-for="pattern in errorPatterns"
                                :key="pattern.pattern_type"
                                class="error-pattern-item"
                            >
                                <div class="pattern-header">
                                    <el-tag
                                        :type="getTrendType(pattern.trend)"
                                        size="small"
                                    >
                                        {{ pattern.pattern_type }}
                                    </el-tag>
                                    <span class="frequency"
                                        >{{ pattern.frequency }} 次</span
                                    >
                                </div>
                                <div class="pattern-description">
                                    {{ pattern.description }}
                                </div>
                                <div class="pattern-trend">
                                    <el-icon :class="getTrendIconClass(pattern.trend)">
                                        <component :is="getTrendIcon(pattern.trend)" />
                                    </el-icon>
                                    <span>{{
                                        getTrendDisplayName(pattern.trend)
                                    }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- Improvement Plans Section -->
        <el-row :gutter="24" style="margin-top: 20px">
            <el-col :span="24">
                <el-card class="improvement-card">
                    <template #header>
                        <div class="card-header">
                            <el-icon><ArrowUp /></el-icon>
                            <span>个性化提升计划</span>
                        </div>
                    </template>
                    <div class="improvement-tabs">
                        <el-tabs
                            v-model="activeImprovementTab"
                            @tab-change="handleImprovementTabChange"
                        >
                            <el-tab-pane label="数学" name="math">
                                <ImprovementPlan
                                    v-if="improvementPlans.math"
                                    :plan="improvementPlans.math"
                                    subject="math"
                                />
                                <div v-else class="no-plan">
                                    <el-empty description="暂无提升计划" />
                                </div>
                            </el-tab-pane>
                            <el-tab-pane label="物理" name="physics">
                                <ImprovementPlan
                                    v-if="improvementPlans.physics"
                                    :plan="improvementPlans.physics"
                                    subject="physics"
                                />
                                <div v-else class="no-plan">
                                    <el-empty description="暂无提升计划" />
                                </div>
                            </el-tab-pane>
                            <el-tab-pane label="英语" name="english">
                                <ImprovementPlan
                                    v-if="improvementPlans.english"
                                    :plan="improvementPlans.english"
                                    subject="english"
                                />
                                <div v-else class="no-plan">
                                    <el-empty description="暂无提升计划" />
                                </div>
                            </el-tab-pane>
                        </el-tabs>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- Quick Actions -->
        <el-row :gutter="24" style="margin-top: 20px">
            <el-col :span="24">
                <el-card class="quick-actions-card">
                    <template #header>
                        <div class="card-header">
                            <el-icon><Operation /></el-icon>
                            <span>快捷操作</span>
                        </div>
                    </template>
                    <div class="quick-actions">
                        <el-button
                            type="primary"
                            size="large"
                            @click="navigateToQuickAnalysis"
                            class="action-button"
                        >
                            <el-icon><Lightning /></el-icon>
                            单题分析
                        </el-button>
                        <el-button
                            type="success"
                            size="large"
                            @click="navigateToHistory"
                            class="action-button"
                        >
                            <el-icon><Clock /></el-icon>
                            查看历史
                        </el-button>
                        <el-button
                            size="large"
                            @click="refreshDashboard"
                            class="action-button"
                        >
                            <el-icon><Refresh /></el-icon>
                            刷新数据
                        </el-button>
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import {
    DataAnalysis,
    Warning,
    ArrowUp,
    Operation,
    Lightning,
    Clock,
    Refresh,
    TrendCharts,
    Bottom,
    Top,
} from "@element-plus/icons-vue";
import {
    apiService,
    type KnowledgePoint,
    type StudentErrorPattern,
    type ImprovementPlan as ImprovementPlanType,
} from "@/services/api";
import ImprovementPlan from "@/components/ImprovementPlan.vue";

const router = useRouter();

// Student info (in a real app, this would come from auth/user service)
const studentId = ref(1); // Demo student ID
const studentName = ref("学生");

// Dashboard state
const isLoadingKnowledge = ref(false);
const isLoadingErrors = ref(false);
const knowledgeError = ref(false);
const selectedSubject = ref<"math" | "physics" | "english">("math");
const errorPatternTimeframe = ref(30);
const activeImprovementTab = ref("math");

// Data
const knowledgePoints = ref<KnowledgePoint[]>([]);
const errorPatterns = ref<StudentErrorPattern[]>([]);
const improvementPlans = ref<{
    math?: ImprovementPlanType;
    physics?: ImprovementPlanType;
    english?: ImprovementPlanType;
}>({});

// Computed properties
const filteredKnowledgePoints = computed(() => {
    return knowledgePoints.value.filter(
        (point) => point.subject === selectedSubject.value,
    );
});

const totalAssignments = computed(() => {
    // In a real app, this would be calculated from actual data
    return 15;
});

const averageScore = computed(() => {
    // Calculate average mastery level
    const points = filteredKnowledgePoints.value;
    if (points.length === 0) return 0;
    const sum = points.reduce((acc, point) => acc + point.mastery_level, 0);
    return Math.round(sum / points.length);
});

// Methods
const loadKnowledgeData = async () => {
    isLoadingKnowledge.value = true;
    knowledgeError.value = false;

    try {
        const data = await apiService.getKnowledgePointMastery(studentId.value);
        knowledgePoints.value = data;
    } catch (error) {
        console.error("Failed to load knowledge points:", error);
        knowledgeError.value = true;
        ElMessage.error("加载知识点数据失败");
    } finally {
        isLoadingKnowledge.value = false;
    }
};

const loadErrorPatterns = async () => {
    isLoadingErrors.value = true;

    try {
        const data = await apiService.getStudentErrorPatterns(
            studentId.value,
            selectedSubject.value,
            errorPatternTimeframe.value,
        );
        errorPatterns.value = data;
    } catch (error) {
        console.error("Failed to load error patterns:", error);
        ElMessage.error("加载错误模式失败");
        errorPatterns.value = [];
    } finally {
        isLoadingErrors.value = false;
    }
};

const loadImprovementPlan = async (subject: string) => {
    try {
        const plan = await apiService.getImprovementPlan(studentId.value, subject);
        improvementPlans.value[subject as keyof typeof improvementPlans.value] = plan;
    } catch (error) {
        console.error(`Failed to load improvement plan for ${subject}:`, error);
        ElMessage.warning(`加载${getSubjectDisplayName(subject)}提升计划失败`);
    }
};

const handleSubjectChange = (newSubject: string | number | boolean | undefined) => {
    selectedSubject.value = newSubject as "math" | "physics" | "english";
    loadErrorPatterns();
};

const handleImprovementTabChange = (tabName: string | number) => {
    const tabNameStr = String(tabName);
    activeImprovementTab.value = tabNameStr;
    if (!improvementPlans.value[tabNameStr as keyof typeof improvementPlans.value]) {
        loadImprovementPlan(tabNameStr);
    }
};

const getMasteryColor = (level: number) => {
    if (level >= 80) return "#67c23a";
    if (level >= 60) return "#e6a23c";
    if (level >= 40) return "#f56c6c";
    return "#909399";
};

const getTrendType = (trend: string) => {
    switch (trend) {
        case "increasing":
            return "danger";
        case "decreasing":
            return "success";
        case "stable":
            return "warning";
        default:
            return "info";
    }
};

const getTrendIcon = (trend: string) => {
    switch (trend) {
        case "increasing":
            return Top;
        case "decreasing":
            return Bottom;
        case "stable":
            return TrendCharts;
        default:
            return TrendCharts;
    }
};

const getTrendIconClass = (trend: string) => {
    switch (trend) {
        case "increasing":
            return "trend-icon trend-up";
        case "decreasing":
            return "trend-icon trend-down";
        case "stable":
            return "trend-icon trend-stable";
        default:
            return "trend-icon";
    }
};

const getTrendDisplayName = (trend: string) => {
    switch (trend) {
        case "increasing":
            return "上升";
        case "decreasing":
            return "下降";
        case "stable":
            return "稳定";
        default:
            return trend;
    }
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

const navigateToQuickAnalysis = () => {
    router.push("/quick-analysis");
};

const navigateToHistory = () => {
    router.push("/history");
};

const refreshDashboard = async () => {
    ElMessage.info("正在刷新仪表盘数据...");
    await Promise.all([
        loadKnowledgeData(),
        loadErrorPatterns(),
        loadImprovementPlan("math"),
        loadImprovementPlan("physics"),
        loadImprovementPlan("english"),
    ]);
    ElMessage.success("仪表盘数据刷新完成！");
};

// Initialize dashboard
onMounted(async () => {
    await Promise.all([
        loadKnowledgeData(),
        loadErrorPatterns(),
        loadImprovementPlan("math"),
    ]);
});
</script>

<style scoped>
.dashboard-container {
    max-width: 1400px;
    margin: 0 auto;
}

.welcome-card {
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
}

.welcome-card :deep(.el-card__body) {
    padding: 24px;
}

.welcome-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: white;
}

.welcome-text {
    flex: 1;
}

.welcome-title {
    font-size: 28px;
    font-weight: 700;
    margin: 0 0 8px 0;
    color: white;
}

.welcome-subtitle {
    font-size: 16px;
    opacity: 0.9;
    margin: 0;
}

.welcome-stats {
    display: flex;
    gap: 40px;
}

.stat-item {
    text-align: center;
}

.stat-number {
    font-size: 32px;
    font-weight: 700;
    line-height: 1;
}

.stat-label {
    font-size: 14px;
    opacity: 0.8;
    margin-top: 4px;
}

.chart-card,
.improvement-card,
.quick-actions-card {
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
    display: flex;
    align-items: center;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
}

.card-header el-icon {
    margin-right: 8px;
    color: #1890ff;
}

.chart-container {
    min-height: 300px;
}

.loading-placeholder,
.error-placeholder {
    min-height: 200px;
}

.knowledge-mastery {
    padding: 16px 0;
}

.subject-tabs {
    margin-bottom: 20px;
}

.mastery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
}

.mastery-item {
    padding: 16px;
    border: 1px solid #e8e8e8;
    border-radius: 6px;
    background: #fafafa;
}

.mastery-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.point-name {
    font-weight: 600;
    color: #303133;
}

.mastery-score {
    font-weight: 700;
    color: #1890ff;
}

.error-patterns-container {
    min-height: 300px;
}

.error-patterns-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.error-pattern-item {
    padding: 16px;
    border: 1px solid #e8e8e8;
    border-radius: 6px;
    background: #fafafa;
}

.pattern-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.frequency {
    font-size: 12px;
    color: #909399;
}

.pattern-description {
    color: #606266;
    margin-bottom: 8px;
    line-height: 1.5;
}

.pattern-trend {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #909399;
}

.trend-icon {
    font-size: 14px;
}

.trend-up {
    color: #f56c6c;
}

.trend-down {
    color: #67c23a;
}

.trend-stable {
    color: #e6a23c;
}

.improvement-tabs {
    min-height: 200px;
}

.quick-actions {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

.action-button {
    flex: 1;
    min-width: 200px;
}

.no-data,
.no-plan {
    min-height: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Responsive design */
@media (max-width: 768px) {
    .welcome-content {
        flex-direction: column;
        text-align: center;
        gap: 20px;
    }

    .welcome-stats {
        gap: 20px;
    }

    .mastery-grid {
        grid-template-columns: 1fr;
    }

    .quick-actions {
        flex-direction: column;
    }

    .action-button {
        min-width: auto;
    }
}
</style>
