<template>
    <div class="error-trends">
        <!-- 页面头部 -->
        <div class="page-header">
            <div class="header-left">
                <h2>错误趋势分析</h2>
                <el-breadcrumb separator="/">
                    <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                    <el-breadcrumb-item>错误趋势分析</el-breadcrumb-item>
                </el-breadcrumb>
            </div>
            <div class="header-right">
                <el-button :icon="Download" @click="exportReport" size="small">
                    导出报告
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
                    <el-form-item label="科目">
                        <el-select
                            v-model="filters.subject"
                            placeholder="选择科目"
                            @change="handleFilterChange"
                            style="width: 150px"
                        >
                            <el-option label="数学" value="math" />
                            <el-option label="物理" value="physics" />
                            <el-option label="英语" value="english" />
                            <el-option label="化学" value="chemistry" />
                        </el-select>
                    </el-form-item>
                    <el-form-item label="时间范围">
                        <el-select
                            v-model="filters.days"
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

        <!-- 总体趋势概览 -->
        <div class="overview-section">
            <el-row :gutter="16">
                <el-col :span="6">
                    <el-card class="metric-card">
                        <div class="metric-content">
                            <div
                                class="metric-value"
                                :class="getStatusClass(trendData?.overall_trend)"
                            >
                                {{ getTrendText(trendData?.overall_trend) }}
                            </div>
                            <div class="metric-label">整体趋势</div>
                        </div>
                        <el-icon
                            class="metric-icon"
                            :class="getStatusClass(trendData?.overall_trend)"
                            :size="36"
                        >
                            <component :is="getTrendIcon(trendData?.overall_trend)" />
                        </el-icon>
                    </el-card>
                </el-col>
                <el-col :span="6">
                    <el-card class="metric-card">
                        <div class="metric-content">
                            <div class="metric-value">{{ currentErrorRate }}%</div>
                            <div class="metric-label">当前错误率</div>
                        </div>
                        <el-icon class="metric-icon" color="#F56C6C" :size="36">
                            <WarningFilled />
                        </el-icon>
                    </el-card>
                </el-col>
                <el-col :span="6">
                    <el-card class="metric-card">
                        <div class="metric-content">
                            <div class="metric-value">{{ totalQuestions }}</div>
                            <div class="metric-label">总题目数</div>
                        </div>
                        <el-icon class="metric-icon" color="#409EFF" :size="36">
                            <DocumentCopy />
                        </el-icon>
                    </el-card>
                </el-col>
                <el-col :span="6">
                    <el-card class="metric-card">
                        <div class="metric-content">
                            <div class="metric-value">{{ systematicErrors }}</div>
                            <div class="metric-label">系统性错误</div>
                        </div>
                        <el-icon class="metric-icon" color="#E6A23C" :size="36">
                            <Flag />
                        </el-icon>
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <!-- 图表区域 -->
        <div class="charts-section">
            <el-row :gutter="16">
                <!-- 错误率趋势图 -->
                <el-col :span="16">
                    <el-card>
                        <template #header>
                            <div class="chart-header">
                                <span>错误率趋势</span>
                                <el-button-group size="small">
                                    <el-button
                                        :type="
                                            chartViewMode === 'line' ? 'primary' : ''
                                        "
                                        @click="chartViewMode = 'line'"
                                    >
                                        线形图
                                    </el-button>
                                    <el-button
                                        :type="chartViewMode === 'bar' ? 'primary' : ''"
                                        @click="chartViewMode = 'bar'"
                                    >
                                        柱状图
                                    </el-button>
                                </el-button-group>
                            </div>
                        </template>
                        <div ref="errorRateChart" class="chart-container"></div>
                    </el-card>
                </el-col>

                <!-- 错误类型分布 -->
                <el-col :span="8">
                    <el-card>
                        <template #header>错误类型分布</template>
                        <div ref="errorTypeChart" class="chart-container"></div>
                    </el-card>
                </el-col>
            </el-row>

            <!-- 错误类型趋势 -->
            <el-row :gutter="16" style="margin-top: 16px">
                <el-col :span="24">
                    <el-card>
                        <template #header>
                            <div class="chart-header">
                                <span>错误类型趋势对比</span>
                                <el-checkbox-group
                                    v-model="selectedErrorTypes"
                                    @change="updateErrorTypeTrend"
                                >
                                    <el-checkbox
                                        v-for="type in availableErrorTypes"
                                        :key="type.error_type"
                                        :label="type.error_type"
                                    >
                                        {{ type.error_type }}
                                    </el-checkbox>
                                </el-checkbox-group>
                            </div>
                        </template>
                        <div
                            ref="errorTypeTrendChart"
                            class="chart-container-large"
                        ></div>
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <!-- 分析结果 -->
        <div class="analysis-section">
            <el-row :gutter="16">
                <!-- 系统性改进 -->
                <el-col :span="12">
                    <el-card>
                        <template #header>
                            <span>系统性改进</span>
                        </template>
                        <div
                            v-if="trendData?.systematic_improvements?.length"
                            class="improvement-list"
                        >
                            <div
                                v-for="(
                                    improvement, index
                                ) in trendData.systematic_improvements"
                                :key="index"
                                class="improvement-item"
                            >
                                <el-icon color="#67C23A" :size="16">
                                    <Check />
                                </el-icon>
                                <span>{{ improvement }}</span>
                            </div>
                        </div>
                        <el-empty
                            v-else
                            description="暂无系统性改进记录"
                            :image-size="80"
                        />
                    </el-card>
                </el-col>

                <!-- 持续问题 -->
                <el-col :span="12">
                    <el-card>
                        <template #header>
                            <span>持续存在问题</span>
                        </template>
                        <div
                            v-if="trendData?.persistent_issues?.length"
                            class="issue-list"
                        >
                            <div
                                v-for="(issue, index) in trendData.persistent_issues"
                                :key="index"
                                class="issue-item"
                            >
                                <el-icon color="#F56C6C" :size="16">
                                    <WarningFilled />
                                </el-icon>
                                <span>{{ issue }}</span>
                            </div>
                        </div>
                        <el-empty
                            v-else
                            description="暂无持续问题记录"
                            :image-size="80"
                        />
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <!-- 详细数据表格 -->
        <div class="table-section">
            <el-card>
                <template #header>
                    <span>错误类型详细分析</span>
                </template>
                <el-table :data="errorTypeTrends" stripe>
                    <el-table-column prop="error_type" label="错误类型" width="150" />
                    <el-table-column prop="trend" label="趋势" width="100">
                        <template #default="{ row }">
                            <el-tag :type="getTrendTagType(row.trend)">
                                {{ getTrendText(row.trend) }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="frequency_change"
                        label="频率变化"
                        width="120"
                    >
                        <template #default="{ row }">
                            <span
                                :class="
                                    row.frequency_change >= 0
                                        ? 'text-danger'
                                        : 'text-success'
                                "
                            >
                                {{ row.frequency_change >= 0 ? "+" : ""
                                }}{{ (row.frequency_change * 100).toFixed(1) }}%
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="recent_count" label="近期次数" width="100" />
                    <el-table-column
                        prop="historical_average"
                        label="历史平均"
                        width="100"
                    >
                        <template #default="{ row }">
                            {{ row.historical_average.toFixed(1) }}
                        </template>
                    </el-table-column>
                    <el-table-column label="对比分析" min-width="200">
                        <template #default="{ row }">
                            <div class="analysis-text">
                                <span
                                    v-if="row.recent_count > row.historical_average"
                                    class="text-danger"
                                >
                                    高于历史平均
                                    {{
                                        (
                                            row.recent_count - row.historical_average
                                        ).toFixed(1)
                                    }}
                                    次
                                </span>
                                <span
                                    v-else-if="
                                        row.recent_count < row.historical_average
                                    "
                                    class="text-success"
                                >
                                    低于历史平均
                                    {{
                                        (
                                            row.historical_average - row.recent_count
                                        ).toFixed(1)
                                    }}
                                    次
                                </span>
                                <span v-else class="text-info"> 与历史平均持平 </span>
                            </div>
                        </template>
                    </el-table-column>
                </el-table>
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed, watch } from "vue";
import { ElMessage } from "element-plus";
import {
    Download,
    Refresh,
    // TrendCharts - removed unused import
    Check,
    WarningFilled,
    DocumentCopy,
    Flag,
    ArrowUp,
    ArrowDown,
    Minus,
} from "@element-plus/icons-vue";
// @ts-ignore
import * as echarts from "echarts";
import { analyticsService, studentService } from "@/services/api";
import type { ErrorTrendAnalysis, Student } from "@/types/student";

// 响应式数据
const loading = ref(false);
const trendData = ref<ErrorTrendAnalysis | null>(null);
const students = ref<Student[]>([]);
const chartViewMode = ref<"line" | "bar">("line");
const selectedErrorTypes = ref<string[]>([]);

// 图表引用
const errorRateChart = ref<HTMLElement>();
const errorTypeChart = ref<HTMLElement>();
const errorTypeTrendChart = ref<HTMLElement>();

// 图表实例
let errorRateChartInstance: echarts.ECharts | null = null;
let errorTypeChartInstance: echarts.ECharts | null = null;
let errorTypeTrendChartInstance: echarts.ECharts | null = null;

// 筛选条件
const filters = reactive({
    studentId: 1, // 默认学生ID
    subject: "math",
    days: 30,
});

// 计算属性
const currentErrorRate = computed(() => {
    if (!trendData.value?.error_rate_trend.length) return 0;
    const latest =
        trendData.value.error_rate_trend[trendData.value.error_rate_trend.length - 1];
    return (latest.error_rate * 100).toFixed(1);
});

const totalQuestions = computed(() => {
    if (!trendData.value?.error_rate_trend.length) return 0;
    return trendData.value.error_rate_trend.reduce(
        (sum, item) => sum + item.total_questions,
        0,
    );
});

const systematicErrors = computed(() => {
    return (
        trendData.value?.error_type_trends.filter((t) => t.trend === "worsening")
            .length || 0
    );
});

const availableErrorTypes = computed(() => {
    return trendData.value?.error_type_trends || [];
});

const errorTypeTrends = computed(() => {
    return trendData.value?.error_type_trends || [];
});

// 加载学生列表
const loadStudents = async () => {
    try {
        const response = await studentService.getAll({ page: 1, size: 100 });
        students.value = response.students;
    } catch (error) {
        console.error("加载学生列表失败:", error);
    }
};

// 加载趋势数据
const loadTrendData = async () => {
    try {
        loading.value = true;
        const data = await analyticsService.getErrorTrends(
            filters.studentId,
            filters.subject,
            filters.days,
        );

        // 添加数据验证和默认值
        trendData.value = data || {
            student_id: filters.studentId,
            subject: filters.subject,
            analysis_period: `最近${filters.days}天`,
            overall_trend: "stable",
            error_rate_trend: [],
            error_type_trends: [],
            systematic_improvements: [],
            persistent_issues: [],
        };

        // 安全访问数组属性
        if (data?.error_type_trends?.length > 0) {
            selectedErrorTypes.value = data.error_type_trends
                .slice(0, 3)
                .map((t) => t.error_type);
        } else {
            selectedErrorTypes.value = [];
        }

        // 等待DOM更新后渲染图表
        await nextTick();
        renderCharts();
    } catch (error) {
        console.error("加载趋势数据失败:", error);
        ElMessage.error("加载数据失败");

        // 设置默认值防止undefined错误
        trendData.value = {
            student_id: filters.studentId,
            subject: filters.subject,
            analysis_period: `最近${filters.days}天`,
            overall_trend: "stable",
            error_rate_trend: [],
            error_type_trends: [],
            systematic_improvements: [],
            persistent_issues: [],
        };
        selectedErrorTypes.value = [];
    } finally {
        loading.value = false;
    }
};

// 渲染图表
const renderCharts = () => {
    renderErrorRateChart();
    renderErrorTypeChart();
    renderErrorTypeTrendChart();
};

// 渲染错误率趋势图
const renderErrorRateChart = () => {
    if (!errorRateChart.value || !trendData.value) return;

    if (errorRateChartInstance) {
        errorRateChartInstance.dispose();
    }

    errorRateChartInstance = echarts.init(errorRateChart.value);

    const dates = trendData.value.error_rate_trend.map((item) => item.date);
    const errorRates = trendData.value.error_rate_trend.map((item) =>
        (item.error_rate * 100).toFixed(1),
    );
    const questionCounts = trendData.value.error_rate_trend.map(
        (item) => item.total_questions,
    );

    const option = {
        tooltip: {
            trigger: "axis",
            axisPointer: {
                type: "cross",
            },
            formatter: (params: any) => {
                const date = params[0].axisValue;
                const errorRate = params[0].value;
                const questions = params[1]?.value || 0;
                return `
          <div>
            <strong>${date}</strong><br/>
            错误率: ${errorRate}%<br/>
            题目数: ${questions}题
          </div>
        `;
            },
        },
        legend: {
            data: ["错误率", "题目数"],
        },
        xAxis: {
            type: "category",
            data: dates,
            axisLabel: {
                formatter: (value: string) => {
                    return new Date(value).toLocaleDateString().slice(5);
                },
            },
        },
        yAxis: [
            {
                type: "value",
                name: "错误率 (%)",
                position: "left",
                axisLabel: {
                    formatter: "{value}%",
                },
            },
            {
                type: "value",
                name: "题目数",
                position: "right",
                axisLabel: {
                    formatter: "{value}题",
                },
            },
        ],
        series: [
            {
                name: "错误率",
                type: chartViewMode.value,
                yAxisIndex: 0,
                data: errorRates,
                itemStyle: {
                    color: "#F56C6C",
                },
                smooth: true,
            },
            {
                name: "题目数",
                type: "bar",
                yAxisIndex: 1,
                data: questionCounts,
                itemStyle: {
                    color: "#409EFF",
                    opacity: 0.6,
                },
            },
        ],
    };

    errorRateChartInstance.setOption(option);
};

// 渲染错误类型分布图
const renderErrorTypeChart = () => {
    if (!errorTypeChart.value || !trendData.value) return;

    if (errorTypeChartInstance) {
        errorTypeChartInstance.dispose();
    }

    errorTypeChartInstance = echarts.init(errorTypeChart.value);

    const data = trendData.value.error_type_trends.map((item) => ({
        name: item.error_type,
        value: item.recent_count,
    }));

    const option = {
        tooltip: {
            trigger: "item",
            formatter: "{a} <br/>{b}: {c} ({d}%)",
        },
        series: [
            {
                name: "错误类型",
                type: "pie",
                radius: "70%",
                data: data,
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: "rgba(0, 0, 0, 0.5)",
                    },
                },
            },
        ],
    };

    errorTypeChartInstance.setOption(option);
};

// 渲染错误类型趋势对比图
const renderErrorTypeTrendChart = () => {
    if (!errorTypeTrendChart.value || !trendData.value) return;

    if (errorTypeTrendChartInstance) {
        errorTypeTrendChartInstance.dispose();
    }

    errorTypeTrendChartInstance = echarts.init(errorTypeTrendChart.value);

    // 模拟错误类型随时间变化的数据
    const dates = trendData.value.error_rate_trend.map((item) => item.date);
    const series: any[] = [];

    selectedErrorTypes.value.forEach((errorType, index) => {
        const trend = trendData.value!.error_type_trends.find(
            (t) => t.error_type === errorType,
        );
        if (trend) {
            // 模拟该错误类型的历史数据
            const data = dates.map((_, i) => {
                const baseValue = trend.historical_average;
                const variation = (Math.random() - 0.5) * 4;
                const trendFactor =
                    trend.trend === "improving"
                        ? -i * 0.1
                        : trend.trend === "worsening"
                          ? i * 0.1
                          : 0;
                return Math.max(0, baseValue + variation + trendFactor).toFixed(1);
            });

            series.push({
                name: errorType,
                type: "line",
                data: data,
                smooth: true,
                itemStyle: {
                    color: ["#409EFF", "#67C23A", "#E6A23C", "#F56C6C", "#909399"][
                        index % 5
                    ],
                },
            });
        }
    });

    const option = {
        tooltip: {
            trigger: "axis",
        },
        legend: {
            data: selectedErrorTypes.value,
        },
        xAxis: {
            type: "category",
            data: dates,
            axisLabel: {
                formatter: (value: string) => {
                    return new Date(value).toLocaleDateString().slice(5);
                },
            },
        },
        yAxis: {
            type: "value",
            name: "错误次数",
            axisLabel: {
                formatter: "{value}次",
            },
        },
        series: series,
    };

    errorTypeTrendChartInstance.setOption(option);
};

// 更新错误类型趋势图
const updateErrorTypeTrend = () => {
    renderErrorTypeTrendChart();
};

// 筛选条件变化处理
const handleFilterChange = () => {
    loadTrendData();
};

// 刷新数据
const refreshData = () => {
    loadTrendData();
};

// 导出报告
const exportReport = () => {
    ElMessage.info("导出功能开发中...");
};

// 获取趋势文本
const getTrendText = (trend?: string) => {
    const trendMap: Record<string, string> = {
        improving: "改善",
        stable: "稳定",
        declining: "下降",
        worsening: "恶化",
    };
    return trendMap[trend || ""] || "未知";
};

// 获取趋势图标
const getTrendIcon = (trend?: string) => {
    const iconMap: Record<string, any> = {
        improving: ArrowUp,
        stable: Minus,
        declining: ArrowDown,
        worsening: ArrowDown,
    };
    return iconMap[trend || ""] || Minus;
};

// 获取状态样式类
const getStatusClass = (trend?: string) => {
    const classMap: Record<string, string> = {
        improving: "status-success",
        stable: "status-info",
        declining: "status-warning",
        worsening: "status-danger",
    };
    return classMap[trend || ""] || "";
};

// 获取趋势标签类型
const getTrendTagType = (trend: string): "success" | "info" | "warning" | "danger" => {
    const typeMap: Record<string, "success" | "info" | "warning" | "danger"> = {
        improving: "success",
        stable: "info",
        declining: "warning",
        worsening: "danger",
    };
    return typeMap[trend] || "info";
};

// 监听图表视图模式变化
watch(chartViewMode, () => {
    renderErrorRateChart();
});

// 窗口大小变化处理
const handleResize = () => {
    errorRateChartInstance?.resize();
    errorTypeChartInstance?.resize();
    errorTypeTrendChartInstance?.resize();
};

// 组件挂载
onMounted(async () => {
    await loadStudents();
    await loadTrendData();

    window.addEventListener("resize", handleResize);
});

// 组件卸载
import { onUnmounted } from "vue";
onUnmounted(() => {
    window.removeEventListener("resize", handleResize);
    errorRateChartInstance?.dispose();
    errorTypeChartInstance?.dispose();
    errorTypeTrendChartInstance?.dispose();
});
</script>

<style scoped>
.error-trends {
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

.metric-card {
    display: flex;
    align-items: center;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.metric-content {
    flex: 1;
}

.metric-value {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 4px;
}

.metric-label {
    color: #606266;
    font-size: 14px;
}

.metric-icon {
    margin-left: 16px;
}

.status-success {
    color: #67c23a;
}

.status-info {
    color: #909399;
}

.status-warning {
    color: #e6a23c;
}

.status-danger {
    color: #f56c6c;
}

.charts-section {
    margin-bottom: 24px;
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chart-container {
    height: 300px;
    width: 100%;
}

.chart-container-large {
    height: 400px;
    width: 100%;
}

.analysis-section {
    margin-bottom: 24px;
}

.improvement-list,
.issue-list {
    max-height: 200px;
    overflow-y: auto;
}

.improvement-item,
.issue-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
}

.improvement-item:last-child,
.issue-item:last-child {
    border-bottom: none;
}

.table-section {
    margin-bottom: 24px;
}

.analysis-text {
    font-size: 14px;
}

.text-success {
    color: #67c23a;
}

.text-danger {
    color: #f56c6c;
}

.text-info {
    color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .error-trends {
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

    .charts-section .el-col {
        margin-bottom: 16px;
    }

    .chart-header {
        flex-direction: column;
        align-items: stretch;
        gap: 12px;
    }

    .chart-container {
        height: 250px;
    }

    .chart-container-large {
        height: 300px;
    }
}
</style>
