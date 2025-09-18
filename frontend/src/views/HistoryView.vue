<template>
    <div class="history-container">
        <!-- Header Section -->
        <el-card class="history-header">
            <div class="header-content">
                <div class="header-text">
                    <h2 class="header-title">
                        <el-icon class="title-icon"><Clock /></el-icon>
                        批改历史
                    </h2>
                    <p class="header-subtitle">浏览所有作业提交记录及AI智能分析结果</p>
                </div>
                <div class="header-stats">
                    <div class="stat-card">
                        <div class="stat-number">{{ totalSubmissions }}</div>
                        <div class="stat-label">总提交次数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ averageGrade }}%</div>
                        <div class="stat-label">平均成绩</div>
                    </div>
                </div>
            </div>
        </el-card>

        <!-- Filters Section -->
        <el-card class="filters-card">
            <div class="filters-content">
                <el-row :gutter="16" align="middle">
                    <el-col :xl="4" :lg="6" :md="8" :sm="12" :xs="24">
                        <div class="filter-item">
                            <label class="filter-label">学科</label>
                            <el-select
                                v-model="filters.subject"
                                placeholder="所有科目"
                                clearable
                                @change="handleFilterChange"
                                style="width: 100%"
                            >
                                <el-option label="数学" value="math" />
                                <el-option label="物理" value="physics" />
                                <el-option label="英语" value="english" />
                            </el-select>
                        </div>
                    </el-col>
                    <el-col :xl="4" :lg="6" :md="8" :sm="12" :xs="24">
                        <div class="filter-item">
                            <label class="filter-label">状态</label>
                            <el-select
                                v-model="filters.status"
                                placeholder="所有状态"
                                clearable
                                @change="handleFilterChange"
                                style="width: 100%"
                            >
                                <el-option label="已完成" value="completed" />
                                <el-option label="处理中" value="pending" />
                                <el-option label="失败" value="failed" />
                            </el-select>
                        </div>
                    </el-col>
                    <el-col :xl="6" :lg="12" :md="16" :sm="24" :xs="24">
                        <div class="filter-item">
                            <label class="filter-label">日期范围</label>
                            <el-date-picker
                                v-model="filters.dateRange"
                                type="daterange"
                                range-separator="至"
                                start-placeholder="开始日期"
                                end-placeholder="结束日期"
                                @change="handleFilterChange"
                                style="width: 100%"
                            />
                        </div>
                    </el-col>
                    <el-col :xl="6" :lg="12" :md="8" :sm="24" :xs="24">
                        <div class="filter-item">
                            <label class="filter-label">搜索</label>
                            <el-input
                                v-model="filters.search"
                                placeholder="按文件名搜索..."
                                clearable
                                @input="handleSearchChange"
                                style="width: 100%"
                            >
                                <template #prefix>
                                    <el-icon><Search /></el-icon>
                                </template>
                            </el-input>
                        </div>
                    </el-col>
                    <el-col :xl="4" :lg="6" :md="16" :sm="24" :xs="24">
                        <div class="filter-actions">
                            <el-button @click="resetFilters" size="default">
                                <el-icon><Refresh /></el-icon>
                                重置
                            </el-button>
                        </div>
                    </el-col>
                </el-row>
            </div>
        </el-card>

        <!-- History List -->

        <el-card class="history-list-card">
            <template #header>
                <div class="list-header">
                    <span class="results-count">
                        找到 {{ filteredSubmissions.length }} 条提交记录
                    </span>
                    <el-button
                        type="primary"
                        @click="refreshHistory"
                        :loading="isLoading"
                        size="small"
                    >
                        <el-icon><Refresh /></el-icon>
                        刷新
                    </el-button>
                </div>
            </template>

            <div class="history-content">
                <!-- Loading State -->
                <div
                    v-if="isLoading"
                    class="loading-state"
                    v-loading="true"
                    element-loading-text="加载历史记录中..."
                >
                    <div style="height: 200px"></div>
                </div>

                <!-- Empty State -->
                <div v-else-if="filteredSubmissions.length === 0" class="empty-state">
                    <el-empty
                        :description="
                            hasFilters
                                ? '没有符合筛选条件的提交记录'
                                : '暂无作业提交记录'
                        "
                        :image-size="100"
                    >
                        <el-button
                            v-if="hasFilters"
                            type="primary"
                            @click="resetFilters"
                        >
                            清除筛选
                        </el-button>
                        <el-button
                            v-else
                            type="primary"
                            @click="navigateToQuickAnalysis"
                        >
                            开始分析
                        </el-button>
                    </el-empty>
                </div>

                <!-- History Items -->
                <div v-else class="history-items">
                    <div
                        v-for="submission in paginatedSubmissions"
                        :key="submission.id"
                        class="history-item"
                    >
                        <div class="item-left">
                            <div class="item-icon">
                                <el-icon class="file-icon">
                                    <Document />
                                </el-icon>
                            </div>
                            <div class="item-info">
                                <div class="item-title">
                                    作业 #{{ submission.id }} -
                                    {{ getSubjectLabel(submission.subject) }}
                                </div>
                                <div class="item-meta">
                                    <el-tag
                                        :type="
                                            getSubjectTagType(submission.subject) as any
                                        "
                                        size="small"
                                    >
                                        {{ getSubjectLabel(submission.subject) }}
                                    </el-tag>
                                    <span class="meta-separator">•</span>
                                    <span class="submit-date">
                                        {{ formatDate(submission.submission_date) }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="item-center">
                            <div class="grade-info">
                                <div
                                    v-if="submission.grade_percentage !== undefined"
                                    class="grade-score"
                                >
                                    <span class="score-label">得分:</span>
                                    <span
                                        :class="
                                            getGradeClass(submission.grade_percentage)
                                        "
                                    >
                                        {{ submission.grade_percentage }}%
                                    </span>
                                </div>
                                <div class="status-badge">
                                    <el-tag
                                        :type="
                                            getStatusTagType(
                                                submission.is_completed,
                                            ) as any
                                        "
                                        :effect="
                                            !submission.is_completed ? 'plain' : 'dark'
                                        "
                                        size="small"
                                    >
                                        <el-icon v-if="!submission.is_completed">
                                            <Loading />
                                        </el-icon>
                                        <el-icon v-else-if="submission.is_completed">
                                            <Select />
                                        </el-icon>
                                        <el-icon v-else>
                                            <Close />
                                        </el-icon>
                                        {{ getStatusLabel(submission.is_completed) }}
                                    </el-tag>
                                </div>
                            </div>
                        </div>

                        <div class="item-right">
                            <div class="item-actions">
                                <el-button
                                    type="primary"
                                    link
                                    @click="viewDetails(submission)"
                                    :disabled="!submission.is_completed"
                                >
                                    <el-icon><View /></el-icon>
                                    查看详情
                                </el-button>
                                <el-dropdown @command="handleAction">
                                    <el-button type="info" link>
                                        <el-icon><MoreFilled /></el-icon>
                                    </el-button>
                                    <template #dropdown>
                                        <el-dropdown-menu>
                                            <el-dropdown-item
                                                :command="`regrade-${submission.id}`"
                                                :disabled="!submission.is_completed"
                                            >
                                                <el-icon><Refresh /></el-icon>
                                                重新批改
                                            </el-dropdown-item>
                                            <el-dropdown-item
                                                :command="`download-${submission.id}`"
                                                :disabled="!submission.is_completed"
                                            >
                                                <el-icon><Download /></el-icon>
                                                下载报告
                                            </el-dropdown-item>
                                            <el-dropdown-item
                                                :command="`delete-${submission.id}`"
                                                divided
                                            >
                                                <el-icon><Delete /></el-icon>
                                                删除
                                            </el-dropdown-item>
                                        </el-dropdown-menu>
                                    </template>
                                </el-dropdown>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Pagination -->
                <div
                    v-if="filteredSubmissions.length > pageSize"
                    class="pagination-container"
                >
                    <el-pagination
                        v-model:current-page="currentPage"
                        v-model:page-size="pageSize"
                        :page-sizes="[10, 20, 50, 100]"
                        :total="filteredSubmissions.length"
                        layout="total, sizes, prev, pager, next, jumper"
                        @size-change="handleSizeChange"
                        @current-change="handleCurrentChange"
                    />
                </div>
            </div>
        </el-card>
    </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
    Clock,
    Search,
    Refresh,
    Document,
    View,
    MoreFilled,
    Download,
    Delete,
    Loading,
    Select,
    Close,
} from "@element-plus/icons-vue";
import { apiService } from "@/services/api";
import type { HomeworkSubmission } from "@/types/homework";

const router = useRouter();

// Component state
const isLoading = ref(false);
const submissions = ref<HomeworkSubmission[]>([]);
const currentPage = ref(1);
const pageSize = ref(20);

// Filters
const filters = ref({
    subject: "",
    status: "",
    dateRange: null as [Date, Date] | null,
    search: "",
});

// Search debounce
let searchTimer: ReturnType<typeof setTimeout> | null = null;

// Computed properties
const filteredSubmissions = computed(() => {
    let result = submissions.value;

    // Filter by subject
    if (filters.value.subject) {
        result = result.filter(
            (item: HomeworkSubmission) => item.subject === filters.value.subject,
        );
    }

    // Filter by status
    if (filters.value.status && filters.value.status !== "all") {
        result = result.filter((item: HomeworkSubmission) =>
            filters.value.status === "completed"
                ? item.is_completed
                : !item.is_completed,
        );
    }

    // Filter by date range
    if (filters.value.dateRange && filters.value.dateRange.length === 2) {
        const [startDate, endDate] = filters.value.dateRange;
        result = result.filter((item: HomeworkSubmission) => {
            const itemDate = new Date(item.submission_date);
            return itemDate >= startDate && itemDate <= endDate;
        });
    }

    // Filter by search
    if (filters.value.search) {
        const searchLower = filters.value.search.toLowerCase();
        result = result.filter((item: HomeworkSubmission) =>
            `作业 #${item.id} - ${getSubjectLabel(item.subject)}`
                .toLowerCase()
                .includes(searchLower),
        );
    }

    return result.sort(
        (a: HomeworkSubmission, b: HomeworkSubmission) =>
            new Date(b.submission_date).getTime() -
            new Date(a.submission_date).getTime(),
    );
});

const paginatedSubmissions = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    return filteredSubmissions.value.slice(start, end);
});

const hasFilters = computed(() => {
    return !!(
        filters.value.subject ||
        filters.value.status ||
        filters.value.dateRange ||
        filters.value.search
    );
});

const totalSubmissions = computed(() => submissions.value.length);

const averageGrade = computed(() => {
    const completedSubmissions = submissions.value.filter(
        (s: HomeworkSubmission) => s.is_completed && s.grade_percentage !== undefined,
    );
    if (completedSubmissions.length === 0) return 0;

    const sum = completedSubmissions.reduce(
        (acc: number, s: HomeworkSubmission) => acc + (s.grade_percentage || 0),
        0,
    );
    return Math.round(sum / completedSubmissions.length);
});

// Methods
const loadHistory = async () => {
    isLoading.value = true;
    try {
        // Using demo student ID 1
        const data = await apiService.getHomeworkHistory(1, 100);

        // 添加数据验证，确保返回的是数组
        submissions.value = Array.isArray(data) ? data : [];
    } catch (error) {
        console.error("Failed to load history:", error);
        ElMessage.error("无法加载作业历史记录");

        // 设置空数组防止undefined错误
        submissions.value = [];
    } finally {
        isLoading.value = false;
    }
};

const refreshHistory = () => {
    loadHistory();
    ElMessage.info("正在刷新历史记录...");
};

const handleFilterChange = () => {
    currentPage.value = 1;
};

const handleSearchChange = () => {
    if (searchTimer) {
        clearTimeout(searchTimer);
    }
    searchTimer = setTimeout(() => {
        currentPage.value = 1;
    }, 300);
};

const resetFilters = () => {
    filters.value = {
        subject: "",
        status: "",
        dateRange: null,
        search: "",
    };
    currentPage.value = 1;
};

const handleSizeChange = (newSize: number) => {
    pageSize.value = newSize;
    currentPage.value = 1;
};

const handleCurrentChange = (newPage: number) => {
    currentPage.value = newPage;
};

const viewDetails = (submission: HomeworkSubmission) => {
    // In a real app, this would navigate to a detailed view
    ElMessage.info(`正在查看作业 #${submission.id} 的详情`);
};

const handleAction = async (command: string) => {
    const [action, idStr] = command.split("-");
    const submission = submissions.value.find((s) => s.id.toString() === idStr);

    if (!submission) return;

    switch (action) {
        case "regrade":
            ElMessage.info(`正在重新批改作业 #${submission.id}...`);
            break;
        case "download":
            ElMessage.info(`正在下载作业 #${submission.id} 的报告...`);
            break;
        case "delete":
            try {
                await ElMessageBox.confirm(
                    `确定要删除作业 #${submission.id} 吗？`,
                    "确认删除",
                    {
                        confirmButtonText: "删除",
                        cancelButtonText: "取消",
                        type: "warning",
                    },
                );
                ElMessage.success("提交记录删除成功");
                // In real app, make API call to delete and refresh data
            } catch {
                // User cancelled
            }
            break;
    }
};

const navigateToQuickAnalysis = () => {
    router.push("/quick-analysis");
};

// Utility methods
const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
};

const getSubjectLabel = (subject: string) => {
    const labels = {
        math: "数学",
        physics: "物理",
        english: "英语",
    };
    return labels[subject as keyof typeof labels] || subject;
};

const getSubjectTagType = (subject: string) => {
    const types = {
        math: "primary" as const,
        physics: "success" as const,
        english: "warning" as const,
    };
    return types[subject as keyof typeof types] || "info";
};

const getStatusLabel = (isCompleted: boolean) => {
    return isCompleted ? "已完成" : "处理中";
};

const getStatusTagType = (isCompleted: boolean) => {
    return isCompleted ? "success" : "warning";
};

const getGradeClass = (score: number) => {
    if (score >= 90) return "grade-excellent";
    if (score >= 80) return "grade-good";
    if (score >= 70) return "grade-fair";
    return "grade-poor";
};

// Initialize
onMounted(() => {
    loadHistory();
});

// Watch for filter changes to reset pagination
watch(
    filters,
    () => {
        currentPage.value = 1;
    },
    { deep: true },
);
</script>

<style scoped>
.history-container {
    max-width: 1400px;
    margin: 0 auto;
}

.history-header {
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
}

.history-header :deep(.el-card__body) {
    padding: 24px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: white;
}

.header-text {
    flex: 1;
}

.header-title {
    font-size: 28px;
    font-weight: 700;
    margin: 0 0 8px 0;
    color: white;
    display: flex;
    align-items: center;
}

.title-icon {
    margin-right: 12px;
    font-size: 32px;
}

.header-subtitle {
    font-size: 16px;
    opacity: 0.9;
    margin: 0;
}

.header-stats {
    display: flex;
    gap: 40px;
}

.stat-card {
    text-align: center;
    padding: 16px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

.stat-number {
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
}

.stat-label {
    font-size: 12px;
    opacity: 0.8;
    margin-top: 4px;
}

.filters-card {
    margin-top: 20px;
    border-radius: 8px;
}

.filters-content {
    padding: 4px 0;
}

.filter-item {
    margin-bottom: 16px;
}

.filter-label {
    display: block;
    font-size: 12px;
    color: #909399;
    margin-bottom: 4px;
    font-weight: 600;
}

.filter-actions {
    display: flex;
    align-items: flex-end;
    height: 100%;
    padding-bottom: 16px;
}

.history-list-card {
    margin-top: 20px;
    border-radius: 8px;
}

.list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.results-count {
    font-size: 14px;
    color: #606266;
    font-weight: 600;
}

.loading-state {
    min-height: 200px;
}

.empty-state {
    padding: 40px 0;
}

.history-items {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.history-item {
    display: flex;
    align-items: center;
    padding: 20px;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    background: #fafafa;
    transition: all 0.3s ease;
}

.history-item:hover {
    background: #f0f9ff;
    border-color: #409eff;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
}

.item-left {
    display: flex;
    align-items: center;
    flex: 1;
    min-width: 0;
}

.item-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    background: #409eff;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    flex-shrink: 0;
}

.file-icon {
    color: white;
    font-size: 20px;
}

.item-info {
    min-width: 0;
    flex: 1;
}

.item-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 4px;
    word-break: break-word;
}

.item-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #909399;
}

.meta-separator {
    color: #dcdfe6;
}

.submit-date {
    white-space: nowrap;
}

.item-center {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    margin: 0 24px;
}

.grade-info {
    text-align: center;
}

.grade-score {
    margin-bottom: 8px;
}

.score-label {
    font-size: 12px;
    color: #909399;
    margin-right: 4px;
}

.grade-excellent {
    color: #67c23a;
    font-weight: 700;
    font-size: 16px;
}

.grade-good {
    color: #409eff;
    font-weight: 700;
    font-size: 16px;
}

.grade-fair {
    color: #e6a23c;
    font-weight: 700;
    font-size: 16px;
}

.grade-poor {
    color: #f56c6c;
    font-weight: 700;
    font-size: 16px;
}

.item-right {
    display: flex;
    align-items: center;
}

.item-actions {
    display: flex;
    align-items: center;
    gap: 8px;
}

.pagination-container {
    display: flex;
    justify-content: center;
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid #e8e8e8;
}

/* Responsive design */
@media (max-width: 1200px) {
    .header-stats {
        gap: 20px;
    }

    .stat-card {
        padding: 12px;
    }

    .stat-number {
        font-size: 24px;
    }
}

@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        text-align: center;
        gap: 20px;
    }

    .header-stats {
        gap: 16px;
    }

    .history-item {
        flex-direction: column;
        align-items: stretch;
        gap: 16px;
        padding: 16px;
    }

    .item-left,
    .item-center,
    .item-right {
        margin: 0;
        justify-content: flex-start;
    }

    .item-center {
        flex-direction: row;
        justify-content: space-between;
    }

    .filter-actions {
        padding-bottom: 0;
    }

    .pagination-container {
        overflow-x: auto;
    }
}

@media (max-width: 480px) {
    .header-title {
        font-size: 24px;
    }

    .stat-number {
        font-size: 20px;
    }

    .item-actions {
        flex-direction: column;
        gap: 4px;
        width: 100%;
    }
}
</style>
