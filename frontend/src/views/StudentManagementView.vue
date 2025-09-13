<template>
    <div class="student-management">
        <!-- 页面头部 -->
        <div class="page-header">
            <div class="header-left">
                <h2>学生管理</h2>
                <el-breadcrumb separator="/">
                    <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                    <el-breadcrumb-item>学生管理</el-breadcrumb-item>
                </el-breadcrumb>
            </div>
            <div class="header-right">
                <el-button type="primary" :icon="Plus" @click="showAddDialog = true">
                    添加学生
                </el-button>
            </div>
        </div>

        <!-- 搜索和筛选 -->
        <div class="filters-section">
            <el-card>
                <el-form :model="filters" inline>
                    <el-form-item label="搜索学生">
                        <el-input
                            v-model="filters.search"
                            placeholder="姓名、学号或邮箱"
                            :prefix-icon="Search"
                            @input="handleSearch"
                            clearable
                            style="width: 250px"
                        />
                    </el-form-item>
                    <el-form-item label="年级">
                        <el-select
                            v-model="filters.grade"
                            placeholder="选择年级"
                            @change="handleFilter"
                            clearable
                        >
                            <el-option label="初一" value="初一" />
                            <el-option label="初二" value="初二" />
                            <el-option label="初三" value="初三" />
                            <el-option label="高一" value="高一" />
                            <el-option label="高二" value="高二" />
                            <el-option label="高三" value="高三" />
                        </el-select>
                    </el-form-item>
                    <el-form-item label="班级">
                        <el-input
                            v-model="filters.class"
                            placeholder="班级"
                            @input="handleFilter"
                            clearable
                        />
                    </el-form-item>
                    <el-form-item label="状态">
                        <el-select
                            v-model="filters.is_active"
                            placeholder="学生状态"
                            @change="handleFilter"
                            clearable
                        >
                            <el-option label="活跃" :value="true" />
                            <el-option label="非活跃" :value="false" />
                        </el-select>
                    </el-form-item>
                    <el-form-item>
                        <el-button :icon="Refresh" @click="resetFilters"
                            >重置</el-button
                        >
                    </el-form-item>
                </el-form>
            </el-card>
        </div>

        <!-- 统计卡片 -->
        <div class="stats-section">
            <el-row :gutter="16">
                <el-col :span="6">
                    <el-card class="stat-card">
                        <div class="stat-content">
                            <div class="stat-number">{{ totalStudents }}</div>
                            <div class="stat-label">总学生数</div>
                        </div>
                        <el-icon class="stat-icon" color="#409EFF" :size="40">
                            <User />
                        </el-icon>
                    </el-card>
                </el-col>
                <el-col :span="6">
                    <el-card class="stat-card">
                        <div class="stat-content">
                            <div class="stat-number">{{ activeStudents }}</div>
                            <div class="stat-label">活跃学生</div>
                        </div>
                        <el-icon class="stat-icon" color="#67C23A" :size="40">
                            <UserFilled />
                        </el-icon>
                    </el-card>
                </el-col>
                <el-col :span="6">
                    <el-card class="stat-card">
                        <div class="stat-content">
                            <div class="stat-number">{{ todayActive }}</div>
                            <div class="stat-label">今日活跃</div>
                        </div>
                        <el-icon class="stat-icon" color="#E6A23C" :size="40">
                            <Calendar />
                        </el-icon>
                    </el-card>
                </el-col>
                <el-col :span="6">
                    <el-card class="stat-card">
                        <div class="stat-content">
                            <div class="stat-number">{{ newStudentsThisMonth }}</div>
                            <div class="stat-label">本月新增</div>
                        </div>
                        <el-icon class="stat-icon" color="#F56C6C" :size="40">
                            <TrendCharts />
                        </el-icon>
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <!-- 学生列表 -->
        <div class="table-section">
            <el-card>
                <template #header>
                    <div class="table-header">
                        <span>学生列表</span>
                        <div class="table-actions">
                            <el-button
                                :icon="Download"
                                @click="exportStudents"
                                size="small"
                            >
                                导出Excel
                            </el-button>
                            <el-button
                                :icon="Refresh"
                                @click="refreshData"
                                size="small"
                                :loading="loading"
                            >
                                刷新
                            </el-button>
                        </div>
                    </div>
                </template>

                <el-table
                    :data="studentList"
                    v-loading="loading"
                    stripe
                    @selection-change="handleSelectionChange"
                >
                    <el-table-column type="selection" width="55" />
                    <el-table-column prop="id" label="ID" width="70" />
                    <el-table-column prop="name" label="姓名" width="120">
                        <template #default="{ row }">
                            <div class="student-name">
                                <el-avatar :size="32" style="margin-right: 8px">
                                    {{ row.name.charAt(0) }}
                                </el-avatar>
                                <span>{{ row.name }}</span>
                            </div>
                        </template>
                    </el-table-column>
                    <el-table-column prop="student_number" label="学号" width="120" />
                    <el-table-column prop="grade" label="年级" width="80" />
                    <el-table-column prop="class" label="班级" width="80" />
                    <el-table-column prop="email" label="邮箱" min-width="180" />
                    <el-table-column prop="phone" label="电话" width="120" />
                    <el-table-column label="状态" width="80">
                        <template #default="{ row }">
                            <el-tag :type="row.is_active ? 'success' : 'danger'">
                                {{ row.is_active ? "活跃" : "停用" }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="created_at" label="创建时间" width="180">
                        <template #default="{ row }">
                            {{ formatDate(row.created_at) }}
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="200" fixed="right">
                        <template #default="{ row }">
                            <el-button-group size="small">
                                <el-button :icon="View" @click="viewStudent(row)" link>
                                    详情
                                </el-button>
                                <el-button
                                    :icon="Edit"
                                    @click="editStudent(row)"
                                    link
                                    type="primary"
                                >
                                    编辑
                                </el-button>
                                <el-button
                                    :icon="DataAnalysis"
                                    @click="viewStats(row)"
                                    link
                                    type="warning"
                                >
                                    统计
                                </el-button>
                                <el-button
                                    :icon="Delete"
                                    @click="deleteStudent(row)"
                                    link
                                    type="danger"
                                    :disabled="row.is_active"
                                >
                                    删除
                                </el-button>
                            </el-button-group>
                        </template>
                    </el-table-column>
                </el-table>

                <!-- 分页 -->
                <div class="pagination-container">
                    <el-pagination
                        v-model:current-page="pagination.page"
                        v-model:page-size="pagination.size"
                        :page-sizes="[10, 20, 50, 100]"
                        :total="pagination.total"
                        layout="total, sizes, prev, pager, next, jumper"
                        @size-change="handleSizeChange"
                        @current-change="handleCurrentChange"
                    />
                </div>
            </el-card>
        </div>

        <!-- 添加/编辑学生对话框 -->
        <el-dialog
            v-model="showAddDialog"
            :title="editingStudent ? '编辑学生' : '添加学生'"
            width="500px"
            @close="resetForm"
        >
            <el-form
                ref="studentFormRef"
                :model="studentForm"
                :rules="studentRules"
                label-width="80px"
            >
                <el-form-item label="姓名" prop="name">
                    <el-input v-model="studentForm.name" placeholder="请输入学生姓名" />
                </el-form-item>
                <el-form-item label="学号" prop="student_number">
                    <el-input
                        v-model="studentForm.student_number"
                        placeholder="请输入学号"
                    />
                </el-form-item>
                <el-form-item label="年级" prop="grade">
                    <el-select
                        v-model="studentForm.grade"
                        placeholder="选择年级"
                        style="width: 100%"
                    >
                        <el-option label="初一" value="初一" />
                        <el-option label="初二" value="初二" />
                        <el-option label="初三" value="初三" />
                        <el-option label="高一" value="高一" />
                        <el-option label="高二" value="高二" />
                        <el-option label="高三" value="高三" />
                    </el-select>
                </el-form-item>
                <el-form-item label="班级" prop="class">
                    <el-input v-model="studentForm.class" placeholder="请输入班级" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                    <el-input
                        v-model="studentForm.email"
                        placeholder="请输入邮箱地址"
                    />
                </el-form-item>
                <el-form-item label="电话" prop="phone">
                    <el-input
                        v-model="studentForm.phone"
                        placeholder="请输入联系电话"
                    />
                </el-form-item>
                <el-form-item v-if="editingStudent" label="状态">
                    <el-switch
                        v-model="studentForm.is_active"
                        active-text="活跃"
                        inactive-text="停用"
                    />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showAddDialog = false">取消</el-button>
                <el-button type="primary" @click="saveStudent" :loading="submitting">
                    {{ editingStudent ? "更新" : "添加" }}
                </el-button>
            </template>
        </el-dialog>

        <!-- 学生详情对话框 -->
        <el-dialog v-model="showDetailDialog" title="学生详情" width="800px">
            <div v-if="selectedStudent" class="student-detail">
                <el-descriptions :column="2" border>
                    <el-descriptions-item label="学生ID">{{
                        selectedStudent.id
                    }}</el-descriptions-item>
                    <el-descriptions-item label="姓名">{{
                        selectedStudent.name
                    }}</el-descriptions-item>
                    <el-descriptions-item label="学号">{{
                        selectedStudent.student_number
                    }}</el-descriptions-item>
                    <el-descriptions-item label="年级">{{
                        selectedStudent.grade
                    }}</el-descriptions-item>
                    <el-descriptions-item label="班级">{{
                        selectedStudent.class || "-"
                    }}</el-descriptions-item>
                    <el-descriptions-item label="邮箱">{{
                        selectedStudent.email || "-"
                    }}</el-descriptions-item>
                    <el-descriptions-item label="电话">{{
                        selectedStudent.phone || "-"
                    }}</el-descriptions-item>
                    <el-descriptions-item label="状态">
                        <el-tag
                            :type="selectedStudent.is_active ? 'success' : 'danger'"
                        >
                            {{ selectedStudent.is_active ? "活跃" : "停用" }}
                        </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="创建时间">{{
                        formatDate(selectedStudent.created_at)
                    }}</el-descriptions-item>
                    <el-descriptions-item label="更新时间">{{
                        formatDate(selectedStudent.updated_at)
                    }}</el-descriptions-item>
                </el-descriptions>

                <!-- 学习统计 -->
                <div v-if="selectedStudentStats" class="student-stats">
                    <h4>学习统计</h4>
                    <el-row :gutter="16">
                        <el-col :span="6">
                            <div class="stat-item">
                                <div class="stat-value">
                                    {{ selectedStudentStats.total_homework }}
                                </div>
                                <div class="stat-name">总作业数</div>
                            </div>
                        </el-col>
                        <el-col :span="6">
                            <div class="stat-item">
                                <div class="stat-value">
                                    {{ selectedStudentStats.average_score.toFixed(1) }}
                                </div>
                                <div class="stat-name">平均分数</div>
                            </div>
                        </el-col>
                        <el-col :span="6">
                            <div class="stat-item">
                                <div class="stat-value">
                                    {{
                                        selectedStudentStats.improvement_rate.toFixed(
                                            1,
                                        )
                                    }}%
                                </div>
                                <div class="stat-name">进步率</div>
                            </div>
                        </el-col>
                        <el-col :span="6">
                            <div class="stat-item">
                                <div class="stat-value">
                                    {{ selectedStudentStats.active_days }}
                                </div>
                                <div class="stat-name">活跃天数</div>
                            </div>
                        </el-col>
                    </el-row>

                    <div class="subject-performance">
                        <h5>科目表现</h5>
                        <el-table
                            :data="selectedStudentStats.subject_performance"
                            size="small"
                        >
                            <el-table-column prop="subject" label="科目" width="100" />
                            <el-table-column
                                prop="average_score"
                                label="平均分"
                                width="100"
                            >
                                <template #default="{ row }">
                                    {{ row.average_score.toFixed(1) }}
                                </template>
                            </el-table-column>
                            <el-table-column
                                prop="total_questions"
                                label="题目总数"
                                width="100"
                            />
                            <el-table-column
                                prop="correct_rate"
                                label="正确率"
                                width="100"
                            >
                                <template #default="{ row }">
                                    {{ (row.correct_rate * 100).toFixed(1) }}%
                                </template>
                            </el-table-column>
                            <el-table-column
                                prop="recent_trend"
                                label="趋势"
                                width="100"
                            >
                                <template #default="{ row }">
                                    <el-tag
                                        :type="
                                            row.recent_trend === 'improving'
                                                ? 'success'
                                                : row.recent_trend === 'declining'
                                                  ? 'danger'
                                                  : undefined
                                        "
                                        size="small"
                                    >
                                        {{ getTrendText(row.recent_trend) }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import {
    ElMessage,
    ElMessageBox,
    type FormRules,
    type FormInstance,
} from "element-plus";
import {
    Plus,
    Search,
    Refresh,
    Download,
    View,
    Edit,
    Delete,
    DataAnalysis,
    User,
    UserFilled,
    Calendar,
    TrendCharts,
} from "@element-plus/icons-vue";
import { studentService } from "@/services/api";
import type {
    Student,
    StudentCreate,
    StudentUpdate,
    StudentStats,
    StudentFilter,
    PaginationParams,
} from "@/types/student";

// 响应式数据
const loading = ref(false);
const submitting = ref(false);
const showAddDialog = ref(false);
const showDetailDialog = ref(false);
const editingStudent = ref<Student | null>(null);
const selectedStudent = ref<Student | null>(null);
const selectedStudentStats = ref<StudentStats | null>(null);
const studentList = ref<Student[]>([]);
const selectedStudents = ref<Student[]>([]);

// 表单相关
const studentFormRef = ref<FormInstance>();
const studentForm = reactive<StudentCreate & { is_active?: boolean }>({
    name: "",
    email: "",
    phone: "",
    grade: "",
    class: "",
    student_number: "",
    is_active: true,
});

// 表单验证规则
const studentRules: FormRules = {
    name: [
        { required: true, message: "请输入学生姓名", trigger: "blur" },
        { min: 2, max: 20, message: "姓名长度在 2 到 20 个字符", trigger: "blur" },
    ],
    student_number: [{ required: true, message: "请输入学号", trigger: "blur" }],
    grade: [{ required: true, message: "请选择年级", trigger: "change" }],
    email: [
        { type: "email", message: "请输入正确的邮箱地址", trigger: ["blur", "change"] },
    ],
    phone: [
        { pattern: /^1[3-9]\d{9}$/, message: "请输入正确的手机号码", trigger: "blur" },
    ],
};

// 筛选条件
const filters = reactive<StudentFilter & { search: string }>({
    search: "",
    grade: "",
    class: "",
    is_active: undefined,
});

// 分页
const pagination = reactive({
    page: 1,
    size: 20,
    total: 0,
});

// 统计数据
const totalStudents = ref(0);
const activeStudents = ref(0);
const todayActive = ref(0);
const newStudentsThisMonth = ref(0);

// 计算属性
const computedFilters = computed(() => {
    const result: any = {};
    if (filters.search) result.search = filters.search;
    if (filters.grade) result.grade = filters.grade;
    if (filters.class) result.class = filters.class;
    if (filters.is_active !== undefined) result.is_active = filters.is_active;
    return result;
});

// 加载学生列表
const loadStudents = async () => {
    try {
        loading.value = true;
        const params: PaginationParams & StudentFilter & { search?: string } = {
            page: pagination.page,
            size: pagination.size,
            ...computedFilters.value,
        };

        const response = await studentService.getAll(params);
        studentList.value = response.students;
        pagination.total = response.total;

        // 更新统计数据
        updateStats();
    } catch (error) {
        console.error("加载学生列表失败:", error);
        ElMessage.error("加载学生列表失败");
    } finally {
        loading.value = false;
    }
};

// 更新统计数据
const updateStats = () => {
    totalStudents.value = pagination.total;
    activeStudents.value = studentList.value.filter((s) => s.is_active).length;
    todayActive.value = Math.floor(activeStudents.value * 0.6); // 模拟数据
    newStudentsThisMonth.value = Math.floor(totalStudents.value * 0.1); // 模拟数据
};

// 搜索处理
let searchTimer: number;
const handleSearch = () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
        pagination.page = 1;
        loadStudents();
    }, 500);
};

// 筛选处理
const handleFilter = () => {
    pagination.page = 1;
    loadStudents();
};

// 重置筛选
const resetFilters = () => {
    Object.assign(filters, {
        search: "",
        grade: "",
        class: "",
        is_active: undefined,
    });
    pagination.page = 1;
    loadStudents();
};

// 分页处理
const handleSizeChange = (size: number) => {
    pagination.size = size;
    loadStudents();
};

const handleCurrentChange = (page: number) => {
    pagination.page = page;
    loadStudents();
};

// 选择处理
const handleSelectionChange = (students: Student[]) => {
    selectedStudents.value = students;
};

// 刷新数据
const refreshData = () => {
    loadStudents();
};

// 导出学生
const exportStudents = () => {
    ElMessage.info("导出功能开发中...");
};

// 查看学生详情
const viewStudent = async (student: Student) => {
    selectedStudent.value = student;
    try {
        selectedStudentStats.value = await studentService.getStats(student.id);
    } catch (error) {
        console.error("加载学生统计失败:", error);
    }
    showDetailDialog.value = true;
};

// 编辑学生
const editStudent = (student: Student) => {
    editingStudent.value = student;
    Object.assign(studentForm, {
        name: student.name,
        email: student.email || "",
        phone: student.phone || "",
        grade: student.grade,
        class: student.class || "",
        student_number: student.student_number || "",
        is_active: student.is_active,
    });
    showAddDialog.value = true;
};

// 查看统计
const viewStats = (_student: Student) => {
    // 跳转到学生详细统计页面
    ElMessage.info("跳转到学生统计页面功能开发中...");
};

// 删除学生
const deleteStudent = async (student: Student) => {
    try {
        await ElMessageBox.confirm(
            `确定要删除学生 "${student.name}" 吗？此操作不可恢复。`,
            "确认删除",
            {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning",
            },
        );

        await studentService.delete(student.id);
        ElMessage.success("删除成功");
        loadStudents();
    } catch (error: any) {
        if (error !== "cancel") {
            console.error("删除学生失败:", error);
            ElMessage.error("删除失败");
        }
    }
};

// 保存学生
const saveStudent = async () => {
    try {
        await studentFormRef.value?.validate();
        submitting.value = true;

        if (editingStudent.value) {
            // 更新学生
            const updates: StudentUpdate = {
                name: studentForm.name,
                email: studentForm.email || undefined,
                phone: studentForm.phone || undefined,
                grade: studentForm.grade,
                class: studentForm.class || undefined,
                student_number: studentForm.student_number || undefined,
                is_active: studentForm.is_active,
            };
            await studentService.update(editingStudent.value.id, updates);
            ElMessage.success("更新成功");
        } else {
            // 创建学生
            const newStudent: StudentCreate = {
                name: studentForm.name,
                email: studentForm.email || undefined,
                phone: studentForm.phone || undefined,
                grade: studentForm.grade,
                class: studentForm.class || undefined,
                student_number: studentForm.student_number || undefined,
            };
            await studentService.create(newStudent);
            ElMessage.success("添加成功");
        }

        showAddDialog.value = false;
        loadStudents();
    } catch (error) {
        console.error("保存学生失败:", error);
        ElMessage.error("保存失败");
    } finally {
        submitting.value = false;
    }
};

// 重置表单
const resetForm = () => {
    studentFormRef.value?.resetFields();
    Object.assign(studentForm, {
        name: "",
        email: "",
        phone: "",
        grade: "",
        class: "",
        student_number: "",
        is_active: true,
    });
    editingStudent.value = null;
};

// 格式化日期
const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("zh-CN");
};

// 获取趋势文本
const getTrendText = (trend: string) => {
    const trendMap: Record<string, string> = {
        improving: "上升",
        stable: "稳定",
        declining: "下降",
    };
    return trendMap[trend] || trend;
};

// 组件挂载
onMounted(() => {
    loadStudents();
});
</script>

<style scoped>
.student-management {
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

.stats-section {
    margin-bottom: 24px;
}

.stat-card {
    display: flex;
    align-items: center;
    padding: 20px;
}

.stat-content {
    flex: 1;
}

.stat-number {
    font-size: 28px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 4px;
}

.stat-label {
    color: #606266;
    font-size: 14px;
}

.stat-icon {
    margin-left: 16px;
}

.table-section {
    margin-bottom: 24px;
}

.table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.table-actions {
    display: flex;
    gap: 8px;
}

.student-name {
    display: flex;
    align-items: center;
}

.pagination-container {
    margin-top: 16px;
    display: flex;
    justify-content: center;
}

.student-detail {
    margin-top: 16px;
}

.student-stats {
    margin-top: 24px;
}

.student-stats h4 {
    margin: 0 0 16px 0;
    color: #303133;
}

.stat-item {
    text-align: center;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
}

.stat-value {
    font-size: 24px;
    font-weight: bold;
    color: #409eff;
    margin-bottom: 4px;
}

.stat-name {
    color: #606266;
    font-size: 14px;
}

.subject-performance {
    margin-top: 24px;
}

.subject-performance h5 {
    margin: 0 0 16px 0;
    color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .student-management {
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

    .stats-section .el-col {
        margin-bottom: 16px;
    }

    .table-header {
        flex-direction: column;
        align-items: stretch;
        gap: 12px;
    }
}
</style>
