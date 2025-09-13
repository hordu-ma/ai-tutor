<template>
    <el-container class="main-layout">
        <el-aside width="220px" class="sidebar">
            <div class="sidebar-header">
                <span class="sidebar-title">🎓 AI Tutor</span>
            </div>
            <el-menu
                :default-active="route.path"
                class="sidebar-menu"
                router
                background-color="#001529"
                text-color="rgba(255, 255, 255, 0.65)"
                active-text-color="#fff"
            >
                <el-menu-item index="/">
                    <el-icon><DataAnalysis /></el-icon>
                    <span>学习仪表盘</span>
                </el-menu-item>
                <el-menu-item index="/upload">
                    <el-icon><UploadFilled /></el-icon>
                    <span>作业批改</span>
                </el-menu-item>
                <el-menu-item index="/quick-analysis">
                    <el-icon><Lightning /></el-icon>
                    <span>单题快速分析</span>
                </el-menu-item>
                <el-menu-item index="/ai-chat">
                    <el-icon><ChatDotRound /></el-icon>
                    <span>AI智能辅导</span>
                </el-menu-item>
                <el-menu-item index="/history">
                    <el-icon><Clock /></el-icon>
                    <span>批改历史</span>
                </el-menu-item>
                <el-menu-item index="/student-management">
                    <el-icon><UserFilled /></el-icon>
                    <span>学生管理</span>
                </el-menu-item>
                <el-menu-item index="/error-trends">
                    <el-icon><TrendCharts /></el-icon>
                    <span>错误趋势分析</span>
                </el-menu-item>
                <el-menu-item index="/multi-subject-summary">
                    <el-icon><Collection /></el-icon>
                    <span>多科目汇总</span>
                </el-menu-item>
            </el-menu>
        </el-aside>

        <el-container>
            <el-header class="header">
                <div>学生学情管理系统</div>
            </el-header>

            <el-main class="content">
                <router-view />
            </el-main>
        </el-container>
    </el-container>
</template>

<script lang="ts" setup>
// Icons are imported automatically by unplugin-vue-components
// if they are used in the template like <DataAnalysis />
// However, explicit import can be clearer for team collaboration.
import {
    DataAnalysis,
    Lightning,
    Clock,
    UploadFilled,
    ChatDotRound,
    UserFilled,
    TrendCharts,
    Collection,
} from "@element-plus/icons-vue";
// @ts-ignore
import { useRoute } from "vue-router";

const route = useRoute();
</script>

<style scoped>
.main-layout {
    height: 100vh;
    width: 100vw;
}

.sidebar {
    background-color: #001529;
    color: #fff;
    display: flex;
    flex-direction: column;
}

.sidebar-header {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 64px;
    padding: 0 20px;
}

.sidebar-title {
    font-size: 20px;
    font-weight: 600;
    color: #fff;
}

.sidebar-menu {
    border-right: none;
    flex-grow: 1;
}

.sidebar-menu .el-menu-item {
    margin: 4px 0;
}

.sidebar-menu .el-menu-item.is-active {
    background-color: #1890ff !important;
    color: #fff !important;
}

.sidebar-menu .el-menu-item:hover {
    background-color: #1890ff;
    color: #fff;
}

.header {
    background-color: #fff;
    display: flex;
    align-items: center;
    padding: 0 20px;
    font-size: 1.2rem;
    box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
    z-index: 1;
}

.content {
    background-color: #f0f2f5;
    padding: 24px;
    overflow-y: auto;
}
</style>
