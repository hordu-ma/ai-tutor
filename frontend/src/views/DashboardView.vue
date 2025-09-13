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

        <!-- First Row: Knowledge Mastery & Learning Progress Trend -->
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

            <!-- Learning Progress Trend Chart -->
            <el-col :xl="12" :lg="24">
                <el-card class="chart-card">
                    <template #header>
                        <div class="card-header">
                            <el-icon><TrendCharts /></el-icon>
                            <span>学习进度趋势</span>
                            <el-select
                                v-model="progressTimeRange"
                                @change="loadProgressTrend"
                                size="small"
                                style="margin-left: auto; width: 120px"
                            >
                                <el-option label="最近7天" :value="7" />
                                <el-option label="最近30天" :value="30" />
                                <el-option label="最近90天" :value="90" />
                            </el-select>
                        </div>
                    </template>
                    <div class="chart-container">
                        <div
                            v-if="isLoadingProgressTrend"
                            class="loading-placeholder"
                            v-loading="true"
                            element-loading-text="正在加载趋势数据..."
                        />
                        <div
                            v-else
                            ref="progressTrendChart"
                            class="chart-element"
                        ></div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- Second Row: Subject Comparison & Error Statistics -->
        <el-row :gutter="24" style="margin-top: 20px">
            <!-- Subject Performance Comparison -->
            <el-col :xl="12" :lg="24">
                <el-card class="chart-card">
                    <template #header>
                        <div class="card-header">
                            <el-icon><DataAnalysis /></el-icon>
                            <span>各科目成绩对比</span>
                            <el-button-group size="small" style="margin-left: auto">
                                <el-button
                                    :type="chartViewMode === 'scores' ? 'primary' : ''"
                                    @click="
                                        chartViewMode = 'scores';
                                        renderSubjectComparisonChart();
                                    "
                                    size="small"
                                >
                                    分数
                                </el-button>
                                <el-button
                                    :type="
                                        chartViewMode === 'accuracy' ? 'primary' : ''
                                    "
                                    @click="
                                        chartViewMode = 'accuracy';
                                        renderSubjectComparisonChart();
                                    "
                                    size="small"
                                >
                                    正确率
                                </el-button>
                            </el-button-group>
                        </div>
                    </template>
                    <div class="chart-container">
                        <div
                            v-if="isLoadingSubjectComparison"
                            class="loading-placeholder"
                            v-loading="true"
                            element-loading-text="正在加载对比数据..."
                        />
                        <div
                            v-else
                            ref="subjectComparisonChart"
                            class="chart-element"
                        ></div>
                    </div>
                </el-card>
            </el-col>

            <!-- Error Statistics Pie Chart -->
            <el-col :xl="12" :lg="24">
                <el-card class="chart-card">
                    <template #header>
                        <div class="card-header">
                            <el-icon><Warning /></el-icon>
                            <span>错误类型统计</span>
                            <el-select
                                v-model="errorStatsSubject"
                                @change="loadErrorStatistics"
                                size="small"
                                style="margin-left: auto; width: 100px"
                            >
                                <el-option label="全部" value="all" />
                                <el-option label="数学" value="math" />
                                <el-option label="物理" value="physics" />
                                <el-option label="英语" value="english" />
                            </el-select>
                        </div>
                    </template>
                    <div class="chart-container">
                        <div
                            v-if="isLoadingErrorStats"
                            class="loading-placeholder"
                            v-loading="true"
                            element-loading-text="正在加载错误统计..."
                        />
                        <div v-else ref="errorStatsChart" class="chart-element"></div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- Third Row: Learning Time Heatmap & Quick Stats -->
        <el-row :gutter="24" style="margin-top: 20px">
            <!-- Learning Time Distribution Heatmap -->
            <el-col :xl="16" :lg="24">
                <el-card class="chart-card">
                    <template #header>
                        <div class="card-header">
                            <el-icon><Clock /></el-icon>
                            <span>学习时间分布热力图</span>
                            <el-date-picker
                                v-model="heatmapDateRange"
                                type="daterange"
                                range-separator="至"
                                start-placeholder="开始日期"
                                end-placeholder="结束日期"
                                size="small"
                                style="margin-left: auto; width: 240px"
                                @change="loadLearningTimeHeatmap"
                            />
                        </div>
                    </template>
                    <div class="chart-container">
                        <div
                            v-if="isLoadingHeatmap"
                            class="loading-placeholder"
                            v-loading="true"
                            element-loading-text="正在加载热力图..."
                        />
                        <div
                            v-else
                            ref="learningHeatmapChart"
                            class="chart-element"
                        ></div>
                    </div>
                </el-card>
            </el-col>

            <!-- Quick Statistics -->
            <el-col :xl="8" :lg="24">
                <el-card class="stats-card">
                    <template #header>
                        <div class="card-header">
                            <el-icon><DataAnalysis /></el-icon>
                            <span>学习统计</span>
                        </div>
                    </template>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-icon">
                                <el-icon><TrendCharts /></el-icon>
                            </div>
                            <div class="stat-content">
                                <div class="stat-number">{{ weeklyProgress }}%</div>
                                <div class="stat-label">本周进步</div>
                            </div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-icon">
                                <el-icon><Clock /></el-icon>
                            </div>
                            <div class="stat-content">
                                <div class="stat-number">{{ totalStudyTime }}h</div>
                                <div class="stat-label">总学习时长</div>
                            </div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-icon">
                                <el-icon><Warning /></el-icon>
                            </div>
                            <div class="stat-content">
                                <div class="stat-number">{{ errorReductionRate }}%</div>
                                <div class="stat-label">错误减少率</div>
                            </div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-icon">
                                <el-icon><ArrowUp /></el-icon>
                            </div>
                            <div class="stat-content">
                                <div class="stat-number">{{ improvementPoints }}</div>
                                <div class="stat-label">改进知识点</div>
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
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue";
// @ts-ignore
import { useRouter } from "vue-router";
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
} from "@element-plus/icons-vue";
// @ts-ignore
import * as echarts from "echarts";
import {
    apiService,
    type KnowledgePoint,
    type ImprovementPlan as ImprovementPlanType,
} from "@/services/api";
import ImprovementPlan from "@/components/ImprovementPlan.vue";

const router = useRouter();

// Student info (in a real app, this would come from auth/user service)
const studentId = ref(1); // Demo student ID
const studentName = ref("学生");

// Dashboard state
const isLoadingKnowledge = ref(false);

const isLoadingProgressTrend = ref(false);
const isLoadingSubjectComparison = ref(false);
const isLoadingErrorStats = ref(false);
const isLoadingHeatmap = ref(false);
const knowledgeError = ref(false);
const selectedSubject = ref<"math" | "physics" | "english">("math");

const activeImprovementTab = ref("math");

// New chart controls
const progressTimeRange = ref(30);
const chartViewMode = ref<"scores" | "accuracy">("scores");
const errorStatsSubject = ref("all");
const heatmapDateRange = ref<[Date, Date]>([
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    new Date(),
]);

// Data
const knowledgePoints = ref<KnowledgePoint[]>([]);

const improvementPlans = ref<{
    math?: ImprovementPlanType;
    physics?: ImprovementPlanType;
    english?: ImprovementPlanType;
}>({});

// Chart data
const progressTrendData = ref<any[]>([]);
const subjectComparisonData = ref<any[]>([]);
const errorStatsData = ref<any[]>([]);
const learningHeatmapData = ref<any[]>([]);

// Chart refs
const progressTrendChart = ref<HTMLElement>();
const subjectComparisonChart = ref<HTMLElement>();
const errorStatsChart = ref<HTMLElement>();
const learningHeatmapChart = ref<HTMLElement>();

// Chart instances
let progressTrendChartInstance: echarts.ECharts | null = null;
let subjectComparisonChartInstance: echarts.ECharts | null = null;
let errorStatsChartInstance: echarts.ECharts | null = null;
let learningHeatmapChartInstance: echarts.ECharts | null = null;

// Computed properties
const filteredKnowledgePoints = computed(() => {
    return knowledgePoints.value.filter(
        (point) => point.subject === selectedSubject.value,
    );
});

const totalAssignments = computed(() => {
    return 23;
});

const averageScore = computed(() => {
    const points = filteredKnowledgePoints.value;
    if (points.length === 0) return 0;
    const sum = points.reduce((acc, point) => acc + point.mastery_level, 0);
    return Math.round(sum / points.length);
});

// New computed properties for enhanced stats
const weeklyProgress = computed(() => {
    return 12.5;
});

const totalStudyTime = computed(() => {
    return 45.2;
});

const errorReductionRate = computed(() => {
    return 18.3;
});

const improvementPoints = computed(() => {
    return 15;
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

// New chart methods
const loadProgressTrend = async () => {
    isLoadingProgressTrend.value = true;
    try {
        // Mock data - in real app, call API
        const mockData = [
            { date: "2024-11-01", math: 75, physics: 68, english: 82 },
            { date: "2024-11-08", math: 78, physics: 72, english: 85 },
            { date: "2024-11-15", math: 82, physics: 75, english: 87 },
            { date: "2024-11-22", math: 85, physics: 78, english: 89 },
            { date: "2024-11-29", math: 87, physics: 82, english: 91 },
        ];
        progressTrendData.value = mockData;
        await nextTick();
        renderProgressTrendChart();
    } catch (error) {
        console.error("Failed to load progress trend:", error);
        ElMessage.error("加载进度趋势失败");
    } finally {
        isLoadingProgressTrend.value = false;
    }
};

const loadSubjectComparison = async () => {
    isLoadingSubjectComparison.value = true;
    try {
        // Mock data
        const mockData = [
            { subject: "数学", score: 87, accuracy: 0.85 },
            { subject: "物理", score: 82, accuracy: 0.78 },
            { subject: "英语", score: 91, accuracy: 0.92 },
        ];
        subjectComparisonData.value = mockData;
        await nextTick();
        renderSubjectComparisonChart();
    } catch (error) {
        console.error("Failed to load subject comparison:", error);
        ElMessage.error("加载科目对比失败");
    } finally {
        isLoadingSubjectComparison.value = false;
    }
};

const loadErrorStatistics = async () => {
    isLoadingErrorStats.value = true;
    try {
        // Mock data
        const mockData = [
            { name: "计算错误", value: 15, color: "#ff6b6b" },
            { name: "概念混淆", value: 8, color: "#4ecdc4" },
            { name: "逻辑错误", value: 5, color: "#45aaf2" },
            { name: "粗心大意", value: 12, color: "#96ceb4" },
            { name: "理解不足", value: 7, color: "#feca57" },
        ];
        errorStatsData.value = mockData;
        await nextTick();
        renderErrorStatsChart();
    } catch (error) {
        console.error("Failed to load error statistics:", error);
        ElMessage.error("加载错误统计失败");
    } finally {
        isLoadingErrorStats.value = false;
    }
};

const loadLearningTimeHeatmap = async () => {
    isLoadingHeatmap.value = true;
    try {
        // Mock heatmap data
        const mockData = [];
        const startDate = new Date(heatmapDateRange.value[0]);
        const endDate = new Date(heatmapDateRange.value[1]);

        for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
            for (let hour = 0; hour < 24; hour++) {
                mockData.push([
                    d.toISOString().split("T")[0],
                    hour,
                    Math.floor(Math.random() * 120), // minutes
                ]);
            }
        }
        learningHeatmapData.value = mockData;
        await nextTick();
        renderLearningHeatmapChart();
    } catch (error) {
        console.error("Failed to load learning heatmap:", error);
        ElMessage.error("加载学习热力图失败");
    } finally {
        isLoadingHeatmap.value = false;
    }
};

// Chart rendering methods
const renderProgressTrendChart = () => {
    if (!progressTrendChart.value) return;

    if (progressTrendChartInstance) {
        progressTrendChartInstance.dispose();
    }

    progressTrendChartInstance = echarts.init(progressTrendChart.value);

    const option = {
        title: {
            text: "学习进度趋势",
            left: "center",
            textStyle: { fontSize: 14, color: "#333" },
        },
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "line" },
        },
        legend: {
            data: ["数学", "物理", "英语"],
            bottom: 0,
        },
        grid: {
            left: "3%",
            right: "4%",
            bottom: "15%",
            top: "15%",
            containLabel: true,
        },
        xAxis: {
            type: "category",
            data: progressTrendData.value.map((item) => item.date.slice(5)),
        },
        yAxis: {
            type: "value",
            min: 0,
            max: 100,
            axisLabel: {
                formatter: "{value}%",
            },
        },
        series: [
            {
                name: "数学",
                type: "line",
                data: progressTrendData.value.map((item) => item.math),
                smooth: true,
                lineStyle: { color: "#5470c6" },
                itemStyle: { color: "#5470c6" },
            },
            {
                name: "物理",
                type: "line",
                data: progressTrendData.value.map((item) => item.physics),
                smooth: true,
                lineStyle: { color: "#91cc75" },
                itemStyle: { color: "#91cc75" },
            },
            {
                name: "英语",
                type: "line",
                data: progressTrendData.value.map((item) => item.english),
                smooth: true,
                lineStyle: { color: "#fac858" },
                itemStyle: { color: "#fac858" },
            },
        ],
    };

    progressTrendChartInstance.setOption(option);
};

const renderSubjectComparisonChart = () => {
    if (!subjectComparisonChart.value) return;

    if (subjectComparisonChartInstance) {
        subjectComparisonChartInstance.dispose();
    }

    subjectComparisonChartInstance = echarts.init(subjectComparisonChart.value);

    const isScoreMode = chartViewMode.value === "scores";

    const formatter = isScoreMode ? "{value}分" : "{value}%";

    const option = {
        title: {
            text: isScoreMode ? "各科目平均分数" : "各科目正确率",
            left: "center",
            textStyle: { fontSize: 14, color: "#333" },
        },
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "shadow" },
        },
        grid: {
            left: "3%",
            right: "4%",
            bottom: "3%",
            top: "15%",
            containLabel: true,
        },
        xAxis: {
            type: "category",
            data: subjectComparisonData.value.map((item) => item.subject),
        },
        yAxis: {
            type: "value",
            axisLabel: { formatter },
        },
        series: [
            {
                type: "bar",
                data: subjectComparisonData.value.map((item) =>
                    isScoreMode ? item.score : Math.round(item.accuracy * 100),
                ),
                itemStyle: {
                    color: function (params: any) {
                        const colors = ["#5470c6", "#91cc75", "#fac858"];
                        return colors[params.dataIndex % colors.length];
                    },
                },
                label: {
                    show: true,
                    position: "top",
                    formatter: isScoreMode ? "{c}分" : "{c}%",
                },
            },
        ],
    };

    subjectComparisonChartInstance.setOption(option);
};

const renderErrorStatsChart = () => {
    if (!errorStatsChart.value) return;

    if (errorStatsChartInstance) {
        errorStatsChartInstance.dispose();
    }

    errorStatsChartInstance = echarts.init(errorStatsChart.value);

    const option = {
        title: {
            text: "错误类型分布",
            left: "center",
            textStyle: { fontSize: 14, color: "#333" },
        },
        tooltip: {
            trigger: "item",
            formatter: "{b}: {c}次 ({d}%)",
        },
        legend: {
            orient: "vertical",
            left: "left",
            top: "middle",
        },
        series: [
            {
                type: "pie",
                radius: ["40%", "70%"],
                center: ["60%", "50%"],
                data: errorStatsData.value,
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: "rgba(0, 0, 0, 0.5)",
                    },
                },
                label: {
                    formatter: "{b}\n{c}次",
                },
            },
        ],
    };

    errorStatsChartInstance.setOption(option);
};

const renderLearningHeatmapChart = () => {
    if (!learningHeatmapChart.value) return;

    if (learningHeatmapChartInstance) {
        learningHeatmapChartInstance.dispose();
    }

    learningHeatmapChartInstance = echarts.init(learningHeatmapChart.value);

    const hours = Array.from({ length: 24 }, (_, i) => i + "h");
    const days = Array.from(
        new Set(learningHeatmapData.value.map((item) => item[0])),
    ).sort();

    const option = {
        title: {
            text: "学习时间分布热力图",
            left: "center",
            textStyle: { fontSize: 14, color: "#333" },
        },
        tooltip: {
            position: "top",
            formatter: function (params: any) {
                const [date, hour, minutes] = params.data;
                return `${date} ${hour}:00<br/>学习时长: ${minutes}分钟`;
            },
        },
        grid: {
            height: "50%",
            top: "15%",
            left: "10%",
            right: "5%",
        },
        xAxis: {
            type: "category",
            data: hours,
            splitArea: { show: true },
        },
        yAxis: {
            type: "category",
            data: days,
            splitArea: { show: true },
        },
        visualMap: {
            min: 0,
            max: 120,
            calculable: true,
            orient: "horizontal",
            left: "center",
            bottom: "5%",
            inRange: {
                color: ["#ffffff", "#4ecdc4", "#44a08d"],
            },
            text: ["高", "低"],
            textStyle: { color: "#333" },
        },
        series: [
            {
                type: "heatmap",
                data: learningHeatmapData.value,
                label: {
                    show: false,
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowColor: "rgba(0, 0, 0, 0.5)",
                    },
                },
            },
        ],
    };

    learningHeatmapChartInstance.setOption(option);
};

const getSubjectDisplayName = (subject: string) => {
    const names: Record<string, string> = {
        math: "数学",
        physics: "物理",
        english: "英语",
    };
    return names[subject] || subject;
};

// Navigation methods
const navigateToQuickAnalysis = () => {
    router.push("/quick-analysis");
};

const navigateToHistory = () => {
    router.push("/history");
};

const refreshDashboard = async () => {
    ElMessage.info("正在刷新数据...");
    await Promise.all([
        loadKnowledgeData(),
        loadProgressTrend(),
        loadSubjectComparison(),
        loadErrorStatistics(),
        loadLearningTimeHeatmap(),
    ]);
    ElMessage.success("数据刷新完成");
};

// Window resize handler
const handleResize = () => {
    if (progressTrendChartInstance) {
        progressTrendChartInstance.resize();
    }
    if (subjectComparisonChartInstance) {
        subjectComparisonChartInstance.resize();
    }
    if (errorStatsChartInstance) {
        errorStatsChartInstance.resize();
    }
    if (learningHeatmapChartInstance) {
        learningHeatmapChartInstance.resize();
    }
};

// Lifecycle
onMounted(async () => {
    // Load initial data
    await Promise.all([
        loadKnowledgeData(),
        loadProgressTrend(),
        loadSubjectComparison(),
        loadErrorStatistics(),
        loadLearningTimeHeatmap(),
    ]);

    // Load improvement plans
    loadImprovementPlan("math");

    // Add resize listener
    window.addEventListener("resize", handleResize);
});

// Cleanup
onUnmounted(() => {
    window.removeEventListener("resize", handleResize);

    if (progressTrendChartInstance) {
        progressTrendChartInstance.dispose();
    }
    if (subjectComparisonChartInstance) {
        subjectComparisonChartInstance.dispose();
    }
    if (errorStatsChartInstance) {
        errorStatsChartInstance.dispose();
    }
    if (learningHeatmapChartInstance) {
        learningHeatmapChartInstance.dispose();
    }
});
</script>

<style scoped>
.dashboard-container {
    padding: 20px;
}

.welcome-card {
    margin-bottom: 20px;
}

.welcome-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.welcome-text h2 {
    margin: 0 0 8px 0;
    color: #303133;
}

.welcome-subtitle {
    color: #606266;
    margin: 0;
}

.welcome-stats {
    display: flex;
    gap: 30px;
}

.stat-item {
    text-align: center;
}

.stat-number {
    font-size: 28px;
    font-weight: bold;
    color: #409eff;
    margin-bottom: 4px;
}

.stat-label {
    color: #909399;
    font-size: 14px;
}

.chart-card {
    height: 400px;
}

.stats-card {
    height: 400px;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 8px;
}

.chart-container {
    height: 320px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.chart-element {
    width: 100%;
    height: 100%;
}

.loading-placeholder {
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.mastery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-top: 16px;
}

.mastery-item {
    padding: 16px;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    background: #fafafa;
}

.mastery-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.point-name {
    font-weight: 500;
    color: #303133;
}

.mastery-score {
    color: #409eff;
    font-weight: bold;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    height: 320px;
    align-content: start;
}

.stats-grid .stat-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    transition: transform 0.2s ease;
}

.stats-grid .stat-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
    font-size: 24px;
    color: #409eff;
}

.stat-content {
    flex: 1;
}

.stats-grid .stat-number {
    font-size: 24px;
    margin-bottom: 4px;
}

.stats-grid .stat-label {
    font-size: 12px;
}

.improvement-card,
.quick-actions-card {
    margin-top: 20px;
}

.quick-actions {
    display: flex;
    gap: 16px;
    justify-content: center;
}

.action-button {
    height: 50px;
    padding: 0 24px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.no-data {
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.subject-tabs {
    margin-bottom: 16px;
    text-align: center;
}

@media (max-width: 768px) {
    .welcome-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;
    }

    .welcome-stats {
        justify-content: space-around;
        width: 100%;
    }

    .quick-actions {
        flex-direction: column;
    }

    .chart-card {
        height: 350px;
    }

    .stats-grid {
        grid-template-columns: 1fr;
        gap: 12px;
    }
}
</style>
