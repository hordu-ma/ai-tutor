<template>
    <div class="multi-subject-summary">
        <!-- 页面头部 -->
        <div class="page-header">
            <div class="header-left">
                <h2>多科目汇总分析</h2>
                <el-breadcrumb separator="/">
                    <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                    <el-breadcrumb-item>多科目汇总分析</el-breadcrumb-item>
                </el-breadcrumb>
            </div>
            <div class="header-right">
                <el-button :icon="Download" @click="exportSummary" size="small">
                    导出汇总报告
                </el-button>
                <el-button
                    :icon="Refresh"
                    @click="refreshData"
                    size="small"
                    :loading="loading"
                >
                    刷新数据
                </el-button>
            </div>
        </div>

        <!-- 筛选条件 -->
        <div class="filters-section">
            <el-card>
                <el-form :model="filters" inline>
                    <el-form-item label="学生">
                        <el-select
                            v-model="filters.studentId"
                            placeholder="选择学生"
                            @change="handleFilterChange"
                            style="width: 200px"
                        >
                            <el-option
                                v-for="student in students"
                                :key="student.id"
                                :label="student.name"
                                :value="student.id"
                            />
                        </el-select>
                    </el-form-item>
                    <el-form-item label="科目选择">
                        <el-checkbox-group
                            v-model="filters.subjects"
                            @change="handleFilterChange"
                        >
                            <el-checkbox label="math">数学</el-checkbox>
                            <el-checkbox label="physics">物理</el-checkbox>
                            <el-checkbox label="english">英语</el-checkbox>
                            <el-checkbox label="chemistry">化学</el-checkbox>
                        </el-checkbox-group>
                    </el-form-item>
                    <el-form-item label="分析时间">
                        <el-select
                            v-model="filters.timeframeDays"
                            placeholder="选择时间范围"
                            @change="handleFilterChange"
                            style="width: 150px"
                        >
                            <el-option label="最近7天" :value="7" />
                            <el-option label="最近30天" :value="30" />
                            <el-option label="最近60天" :value="60" />
                            <el-option label="最近90天" :value="90" />
                        </el-select>
                    </el-form-item>
                </el-form>
            </el-card>
        </div>

        <!-- 整体表现概览 -->
        <div class="overview-section">
            <el-card>
                <template #header>
                    <span>整体学习表现</span>
                </template>
                <el-row :gutter="24" v-if="summaryData">
                    <el-col :span="4">
                        <div class="performance-metric">
                            <div class="metric-icon">
                                <el-icon :size="32" color="#409EFF">
                                    <DataAnalysis />
                                </el-icon>
                            </div>
                            <div class="metric-content">
                                <div class="metric-value">
                                    {{
                                        summaryData.overall_performance.total_questions
                                    }}
                                </div>
                                <div class="metric-label">总题目数</div>
                            </div>
                        </div>
                    </el-col>
                    <el-col :span="4">
                        <div class="performance-metric">
                            <div class="metric-icon">
                                <el-icon :size="32" color="#F56C6C">
                                    <WarningFilled />
                                </el-icon>
                            </div>
                            <div class="metric-content">
                                <div class="metric-value">
                                    {{ summaryData.overall_performance.total_errors }}
                                </div>
                                <div class="metric-label">总错误数</div>
                            </div>
                        </div>
                    </el-col>
                    <el-col :span="4">
                        <div class="performance-metric">
                            <div class="metric-icon">
                                <el-icon :size="32" color="#67C23A">
                                    <CircleCheckFilled />
                                </el-icon>
                            </div>
                            <div class="metric-content">
                                <div class="metric-value">
                                    {{
                                        (
                                            summaryData.overall_performance
                                                .overall_accuracy * 100
                                        ).toFixed(1)
                                    }}%
                                </div>
                                <div class="metric-label">整体正确率</div>
                            </div>
                        </div>
                    </el-col>
                    <el-col :span="4">
                        <div class="performance-metric">
                            <div class="metric-icon">
                                <el-icon
                                    :size="32"
                                    :color="
                                        getTrendColor(
                                            summaryData.overall_performance
                                                .improvement_trend,
                                        )
                                    "
                                >
                                    <component
                                        :is="
                                            getTrendIcon(
                                                summaryData.overall_performance
                                                    .improvement_trend,
                                            )
                                        "
                                    />
                                </el-icon>
                            </div>
                            <div class="metric-content">
                                <div
                                    class="metric-value"
                                    :style="{
                                        color: getTrendColor(
                                            summaryData.overall_performance
                                                .improvement_trend,
                                        ),
                                    }"
                                >
                                    {{
                                        getTrendText(
                                            summaryData.overall_performance
                                                .improvement_trend,
                                        )
                                    }}
                                </div>
                                <div class="metric-label">整体趋势</div>
                            </div>
                        </div>
                    </el-col>
                    <el-col :span="4">
                        <div class="performance-metric">
                            <div class="metric-icon">
                                <el-icon :size="32" color="#E6A23C">
                                    <Trophy />
                                </el-icon>
                            </div>
                            <div class="metric-content">
                                <div class="metric-value">
                                    {{
                                        summaryData.overall_performance.grade_equivalent
                                    }}
                                </div>
                                <div class="metric-label">等级评定</div>
                            </div>
                        </div>
                    </el-col>
                    <el-col :span="4">
                        <div class="performance-metric">
                            <div class="metric-icon">
                                <el-icon :size="32" color="#909399">
                                    <Calendar />
                                </el-icon>
                            </div>
                            <div class="metric-content">
                                <div class="metric-value">
                                    {{ summaryData.analysis_period }}
                                </div>
                                <div class="metric-label">分析周期</div>
                            </div>
                        </div>
                    </el-col>
                </el-row>
            </el-card>
        </div>

        <!-- 科目对比分析 -->
        <div class="comparison-section">
            <el-row :gutter="16">
                <!-- 科目表现雷达图 -->
                <el-col :span="12">
                    <el-card>
                        <template #header>科目能力雷达图</template>
                        <div ref="radarChart" class="chart-container"></div>
                    </el-card>
                </el-col>

                <!-- 科目排名柱状图 -->
                <el-col :span="12">
                    <el-card>
                        <template #header>科目正确率对比</template>
                        <div ref="barChart" class="chart-container"></div>
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <!-- 科目详细对比表格 -->
        <div class="details-section">
            <el-card>
                <template #header>科目详细分析</template>
                <el-table :data="subjectComparisons" stripe>
                    <el-table-column prop="subject" label="科目" width="100">
                        <template #default="{ row }">
                            <el-tag
                                :color="getSubjectColor(row.subject)"
                                effect="light"
                            >
                                {{ getSubjectName(row.subject) }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="accuracy_rate" label="正确率" width="120">
                        <template #default="{ row }">
                            <el-progress
                                :percentage="row.accuracy_rate * 100"
                                :color="getAccuracyColor(row.accuracy_rate)"
                                :show-text="true"
                                :format="
                                    () => `${(row.accuracy_rate * 100).toFixed(1)}%`
                                "
                            />
                        </template>
                    </el-table-column>
                    <el-table-column prop="error_count" label="错误数量" width="100" />
                    <el-table-column prop="rank_among_subjects" label="排名" width="80">
                        <template #default="{ row }">
                            <el-tag
                                :type="
                                    row.rank_among_subjects <= 2
                                        ? 'success'
                                        : row.rank_among_subjects <= 4
                                          ? 'warning'
                                          : 'danger'
                                "
                                size="small"
                            >
                                第{{ row.rank_among_subjects }}名
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="strength_level" label="能力水平" width="100">
                        <template #default="{ row }">
                            <el-tag :type="getStrengthType(row.strength_level) as any">
                                {{ getStrengthText(row.strength_level) }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="key_issues" label="主要问题" min-width="200">
                        <template #default="{ row }">
                            <div class="issues-list">
                                <el-tag
                                    v-for="(issue, index) in row.key_issues"
                                    :key="index"
                                    size="small"
                                    type="warning"
                                    style="margin: 2px"
                                >
                                    {{ issue }}
                                </el-tag>
                                <span
                                    v-if="row.key_issues.length === 0"
                                    class="text-muted"
                                    >无明显问题</span
                                >
                            </div>
                        </template>
                    </el-table-column>
                </el-table>
            </el-card>
        </div>

        <!-- 跨科目模式分析 -->
        <div class="patterns-section">
            <el-card>
                <template #header>跨科目学习模式</template>
                <div v-if="crossSubjectPatterns.length > 0" class="patterns-grid">
                    <div
                        v-for="pattern in crossSubjectPatterns"
                        :key="pattern.pattern_type"
                        class="pattern-card"
                        :class="`severity-${pattern.severity}`"
                    >
                        <div class="pattern-header">
                            <h4>{{ pattern.pattern_type }}</h4>
                            <el-tag
                                :type="getSeverityType(pattern.severity) as any"
                                size="small"
                            >
                                {{ getSeverityText(pattern.severity) }}
                            </el-tag>
                        </div>
                        <div class="pattern-subjects">
                            <span class="label">影响科目：</span>
                            <el-tag
                                v-for="subject in pattern.affected_subjects"
                                :key="subject"
                                size="small"
                                style="margin-right: 4px"
                            >
                                {{ getSubjectName(subject) }}
                            </el-tag>
                        </div>
                        <div class="pattern-description">
                            {{ pattern.description }}
                        </div>
                        <div class="pattern-suggestions">
                            <div class="suggestions-header">改进建议：</div>
                            <ul class="suggestions-list">
                                <li
                                    v-for="suggestion in pattern.improvement_suggestions"
                                    :key="suggestion"
                                >
                                    {{ suggestion }}
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                <el-empty
                    v-else
                    description="暂无跨科目学习模式数据"
                    :image-size="100"
                />
            </el-card>
        </div>

        <!-- 全局改进建议 -->
        <div class="recommendations-section">
            <el-card>
                <template #header>个性化改进建议</template>
                <div
                    v-if="globalRecommendations.length > 0"
                    class="recommendations-list"
                >
                    <div
                        v-for="(recommendation, index) in globalRecommendations"
                        :key="index"
                        class="recommendation-item"
                        :class="`priority-${recommendation.priority}`"
                    >
                        <div class="recommendation-header">
                            <div class="recommendation-title">
                                <el-icon
                                    :size="16"
                                    :color="getPriorityColor(recommendation.priority)"
                                >
                                    <component
                                        :is="getPriorityIcon(recommendation.priority)"
                                    />
                                </el-icon>
                                <span class="category">{{
                                    getCategoryText(recommendation.category)
                                }}</span>
                                <el-tag
                                    :type="getPriorityType(recommendation.priority)"
                                    size="small"
                                >
                                    {{ getPriorityText(recommendation.priority) }}
                                </el-tag>
                            </div>
                        </div>
                        <div class="recommendation-content">
                            <p class="description">{{ recommendation.description }}</p>
                            <div class="recommendation-details">
                                <div class="detail-item">
                                    <span class="label">预期效果：</span>
                                    <span class="value">{{
                                        recommendation.estimated_impact
                                    }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">时间投入：</span>
                                    <span class="value">{{
                                        recommendation.time_investment
                                    }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <el-empty v-else description="暂无改进建议" :image-size="100" />
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from "vue";
import { ElMessage } from "element-plus";
import {
    Download,
    Refresh,
    DataAnalysis,
    WarningFilled,
    CircleCheckFilled,
    Trophy,
    Calendar,
    ArrowUp,
    ArrowDown,
    Minus,
    Flag,
    StarFilled,
    WarnTriangleFilled,
} from "@element-plus/icons-vue";
// @ts-ignore
import * as echarts from "echarts";
import { analyticsService, studentService } from "@/services/api";
import type { MultiSubjectSummary, Student } from "@/types/student";

// 响应式数据
const loading = ref(false);
const summaryData = ref<MultiSubjectSummary | null>(null);
const students = ref<Student[]>([]);

// 图表引用
const radarChart = ref<HTMLElement>();
const barChart = ref<HTMLElement>();

// 图表实例
let radarChartInstance: echarts.ECharts | null = null;
let barChartInstance: echarts.ECharts | null = null;

// 筛选条件
const filters = reactive({
    studentId: 1,
    subjects: ["math", "physics", "english"],
    timeframeDays: 30,
});

// 计算属性
const subjectComparisons = computed(() => {
    return summaryData.value?.subject_comparisons || [];
});

const crossSubjectPatterns = computed(() => {
    return summaryData.value?.cross_subject_patterns || [];
});

const globalRecommendations = computed(() => {
    return summaryData.value?.recommendations || [];
});

// 科目名称映射
const subjectNames: Record<string, string> = {
    math: "数学",
    physics: "物理",
    english: "英语",
    chemistry: "化学",
};

// 科目颜色映射
const subjectColors: Record<string, string> = {
    math: "#409EFF",
    physics: "#67C23A",
    english: "#E6A23C",
    chemistry: "#F56C6C",
};

// 加载学生列表
const loadStudents = async () => {
    try {
        const response = await studentService.getAll({ page: 1, size: 100 });
        students.value = response.students;
    } catch (error) {
        console.error("加载学生列表失败:", error);
    }
};

// 加载汇总数据
const loadSummaryData = async () => {
    try {
        loading.value = true;
        const data = await analyticsService.getMultiSubjectSummary(
            filters.studentId,
            filters.subjects,
            filters.timeframeDays,
        );
        summaryData.value = data;

        // 等待DOM更新后渲染图表
        await nextTick();
        renderCharts();
    } catch (error) {
        console.error("加载汇总数据失败:", error);
        ElMessage.error("加载数据失败");
    } finally {
        loading.value = false;
    }
};

// 渲染图表
const renderCharts = () => {
    renderRadarChart();
    renderBarChart();
};

// 渲染雷达图
const renderRadarChart = () => {
    if (!radarChart.value || !summaryData.value) return;

    if (radarChartInstance) {
        radarChartInstance.dispose();
    }

    radarChartInstance = echarts.init(radarChart.value);

    const indicators = summaryData.value.subject_comparisons.map((item) => ({
        name: getSubjectName(item.subject),
        max: 100,
    }));

    const data = summaryData.value.subject_comparisons.map(
        (item) => item.accuracy_rate * 100,
    );

    const option = {
        tooltip: {
            trigger: "axis",
        },
        radar: {
            indicator: indicators,
            name: {
                textStyle: {
                    color: "#606266",
                },
            },
        },
        series: [
            {
                name: "科目能力",
                type: "radar",
                data: [
                    {
                        value: data,
                        name: "正确率",
                        itemStyle: {
                            color: "#409EFF",
                        },
                        areaStyle: {
                            color: "rgba(64, 158, 255, 0.3)",
                        },
                    },
                ],
            },
        ],
    };

    radarChartInstance.setOption(option);
};

// 渲染柱状图
const renderBarChart = () => {
    if (!barChart.value || !summaryData.value) return;

    if (barChartInstance) {
        barChartInstance.dispose();
    }

    barChartInstance = echarts.init(barChart.value);

    const subjects = summaryData.value.subject_comparisons.map((item) =>
        getSubjectName(item.subject),
    );
    const accuracyRates = summaryData.value.subject_comparisons.map((item) =>
        (item.accuracy_rate * 100).toFixed(1),
    );
    const colors = summaryData.value.subject_comparisons.map(
        (item) => subjectColors[item.subject] || "#909399",
    );

    const option = {
        tooltip: {
            trigger: "axis",
            axisPointer: {
                type: "shadow",
            },
            formatter: (params: any) => {
                const item = params[0];
                return `${item.name}<br/>正确率: ${item.value}%`;
            },
        },
        xAxis: {
            type: "category",
            data: subjects,
        },
        yAxis: {
            type: "value",
            name: "正确率 (%)",
            min: 0,
            max: 100,
            axisLabel: {
                formatter: "{value}%",
            },
        },
        series: [
            {
                data: accuracyRates.map((value, index) => ({
                    value,
                    itemStyle: {
                        color: colors[index],
                    },
                })),
                type: "bar",
                showBackground: true,
                backgroundStyle: {
                    color: "rgba(180, 180, 180, 0.2)",
                },
            },
        ],
    };

    barChartInstance.setOption(option);
};

// 筛选条件变化处理
const handleFilterChange = () => {
    loadSummaryData();
};

// 刷新数据
const refreshData = () => {
    loadSummaryData();
};

// 导出汇总报告
const exportSummary = () => {
    ElMessage.info("导出功能开发中...");
};

// 获取科目名称
const getSubjectName = (subject: string) => {
    return subjectNames[subject] || subject;
};

// 获取科目颜色
const getSubjectColor = (subject: string) => {
    return subjectColors[subject] || "#909399";
};

// 获取趋势文本
const getTrendText = (trend: string) => {
    const trendMap: Record<string, string> = {
        improving: "上升",
        stable: "稳定",
        declining: "下降",
    };
    return trendMap[trend] || "未知";
};

// 获取趋势图标
const getTrendIcon = (trend: string) => {
    const iconMap: Record<string, any> = {
        improving: ArrowUp,
        stable: Minus,
        declining: ArrowDown,
    };
    return iconMap[trend] || Minus;
};

// 获取趋势颜色
const getTrendColor = (trend: string) => {
    const colorMap: Record<string, string> = {
        improving: "#67C23A",
        stable: "#909399",
        declining: "#F56C6C",
    };
    return colorMap[trend] || "#909399";
};

// 获取正确率颜色
const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 0.9) return "#67C23A";
    if (accuracy >= 0.8) return "#E6A23C";
    return "#F56C6C";
};

// 获取能力水平类型
const getStrengthType = (level: string) => {
    const typeMap: Record<string, string> = {
        strong: "success",
        average: "warning",
        weak: "danger",
    };
    return typeMap[level] || "info";
};

// 获取能力水平文本
const getStrengthText = (level: string) => {
    const textMap: Record<string, string> = {
        strong: "优秀",
        average: "良好",
        weak: "待提高",
    };
    return textMap[level] || level;
};

// 获取严重程度类型
const getSeverityType = (severity: string) => {
    const typeMap: Record<string, string> = {
        high: "danger",
        medium: "warning",
        low: "info",
    };
    return typeMap[severity] || "info";
};

// 获取严重程度文本
const getSeverityText = (severity: string) => {
    const textMap: Record<string, string> = {
        high: "高度关注",
        medium: "中等重要",
        low: "轻度关注",
    };
    return textMap[severity] || severity;
};

// 获取优先级类型
const getPriorityType = (priority: string): "danger" | "warning" | "info" => {
    const typeMap: Record<string, "danger" | "warning" | "info"> = {
        high: "danger",
        medium: "warning",
        low: "info",
    };
    return typeMap[priority] || "info";
};

// 获取优先级文本
const getPriorityText = (priority: string) => {
    const textMap: Record<string, string> = {
        high: "高优先级",
        medium: "中优先级",
        low: "低优先级",
    };
    return textMap[priority] || priority;
};

// 获取优先级颜色
const getPriorityColor = (priority: string) => {
    const colorMap: Record<string, string> = {
        high: "#F56C6C",
        medium: "#E6A23C",
        low: "#409EFF",
    };
    return colorMap[priority] || "#909399";
};

// 获取优先级图标
const getPriorityIcon = (priority: string) => {
    const iconMap: Record<string, any> = {
        high: WarnTriangleFilled,
        medium: Flag,
        low: StarFilled,
    };
    return iconMap[priority] || Flag;
};

// 获取类别文本
const getCategoryText = (category: string) => {
    const textMap: Record<string, string> = {
        study_method: "学习方法",
        time_management: "时间管理",
        concept_review: "概念复习",
        practice_focus: "练习重点",
    };
    return textMap[category] || category;
};

// 窗口大小变化处理
const handleResize = () => {
    radarChartInstance?.resize();
    barChartInstance?.resize();
};

// 组件挂载
onMounted(async () => {
    await loadStudents();
    await loadSummaryData();

    window.addEventListener("resize", handleResize);
});

// 组件卸载
import { onUnmounted } from "vue";
onUnmounted(() => {
    window.removeEventListener("resize", handleResize);
    radarChartInstance?.dispose();
    barChartInstance?.dispose();
});
</script>

<style scoped>
.multi-subject-summary {
    padding: 24px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.header-left h2 {
    margin: 0 0 8px 0;
    color: #303133;
}

.filters-section {
    margin-bottom: 24px;
}

.overview-section {
    margin-bottom: 24px;
}

.performance-metric {
    display: flex;
    align-items: center;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    height: 80px;
}

.metric-icon {
    margin-right: 16px;
}

.metric-content {
    flex: 1;
}

.metric-value {
    font-size: 20px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 4px;
}

.metric-label {
    color: #606266;
    font-size: 14px;
}

.comparison-section {
    margin-bottom: 24px;
}

.chart-container {
    height: 300px;
    width: 100%;
}

.details-section {
    margin-bottom: 24px;
}

.issues-list {
    line-height: 1.6;
}

.text-muted {
    color: #909399;
    font-style: italic;
}

.patterns-section {
    margin-bottom: 24px;
}

.patterns-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 16px;
}

.pattern-card {
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    padding: 16px;
    background: #fff;
}

.pattern-card.severity-high {
    border-left: 4px solid #f56c6c;
}

.pattern-card.severity-medium {
    border-left: 4px solid #e6a23c;
}

.pattern-card.severity-low {
    border-left: 4px solid #409eff;
}

.pattern-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.pattern-header h4 {
    margin: 0;
    color: #303133;
    font-size: 16px;
}

.pattern-subjects {
    margin-bottom: 8px;
}

.pattern-subjects .label {
    color: #606266;
    font-size: 14px;
    margin-right: 8px;
}

.pattern-description {
    color: #606266;
    line-height: 1.5;
    margin-bottom: 12px;
}

.pattern-suggestions .suggestions-header {
    font-weight: 500;
    color: #303133;
    margin-bottom: 8px;
}

.suggestions-list {
    margin: 0;
    padding-left: 20px;
    color: #606266;
}

.suggestions-list li {
    margin-bottom: 4px;
    line-height: 1.4;
}

.recommendations-section {
    margin-bottom: 24px;
}

.recommendations-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.recommendation-item {
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    padding: 16px;
    background: #fff;
}

.recommendation-item.priority-high {
    border-left: 4px solid #f56c6c;
    background: #fef0f0;
}

.recommendation-item.priority-medium {
    border-left: 4px solid #e6a23c;
    background: #fdf6ec;
}

.recommendation-item.priority-low {
    border-left: 4px solid #409eff;
    background: #ecf5ff;
}

.recommendation-header {
    margin-bottom: 12px;
}

.recommendation-title {
    display: flex;
    align-items: center;
    gap: 8px;
}

.recommendation-title .category {
    font-weight: 500;
    color: #303133;
    font-size: 16px;
}

.recommendation-content .description {
    color: #303133;
    line-height: 1.5;
    margin-bottom: 12px;
}

.recommendation-details {
    display: flex;
    gap: 24px;
}

.detail-item .label {
    color: #606266;
    font-size: 14px;
}

.detail-item .value {
    color: #303133;
    font-weight: 500;
    margin-left: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .multi-subject-summary {
        padding: 16px;
    }

    .page-header {
        flex-direction: column;
        align-items: stretch;
        gap: 16px;
    }

    .filters-section .el-form {
        flex-direction: column;
    }

    .filters-section .el-form-item {
        margin-bottom: 16px;
    }

    .overview-section .el-col {
        margin-bottom: 16px;
    }

    .performance-metric {
        flex-direction: column;
        text-align: center;
        height: auto;
    }

    .comparison-section .el-col {
        margin-bottom: 16px;
    }

    .chart-container {
        height: 250px;
    }

    .patterns-grid {
        grid-template-columns: 1fr;
    }

    .recommendation-details {
        flex-direction: column;
        gap: 8px;
    }
}
</style>
