<template>
    <div class="ai-chat-container">
        <!-- 聊天头部 -->
        <div class="chat-header">
            <div class="header-left">
                <h2>AI智能辅导</h2>
                <el-tag
                    v-if="currentProvider"
                    :type="currentProvider === 'qwen' ? 'primary' : 'success'"
                >
                    {{ currentProvider === "qwen" ? "通义千问" : "Kimi AI" }}
                </el-tag>
            </div>
            <div class="header-right">
                <el-button-group>
                    <el-button
                        :type="currentProvider === 'qwen' ? 'primary' : ''"
                        @click="switchProvider('qwen')"
                        size="small"
                    >
                        通义千问
                    </el-button>
                    <el-button
                        :type="currentProvider === 'kimi' ? 'primary' : ''"
                        @click="switchProvider('kimi')"
                        size="small"
                    >
                        Kimi AI
                    </el-button>
                </el-button-group>
                <el-button @click="clearChat" size="small" :icon="Delete">
                    清空对话
                </el-button>
                <el-button @click="showSettings = true" size="small" :icon="Setting">
                    设置
                </el-button>
            </div>
        </div>

        <!-- 快捷提示 -->
        <div v-if="messages.length === 0" class="quick-prompts">
            <h4>快速开始</h4>
            <div class="prompt-grid">
                <div
                    v-for="prompt in quickPrompts"
                    :key="prompt.id"
                    class="prompt-card"
                    @click="selectPrompt(prompt)"
                >
                    <div class="prompt-title">{{ prompt.title }}</div>
                    <div class="prompt-content">{{ prompt.content }}</div>
                </div>
            </div>
        </div>

        <!-- 聊天消息区域 -->
        <div class="chat-messages" ref="messagesContainer">
            <div
                v-for="message in messages"
                :key="message.id"
                :class="[
                    'message',
                    message.role === 'user' ? 'user-message' : 'assistant-message',
                ]"
            >
                <div class="message-avatar">
                    <el-avatar
                        v-if="message.role === 'user'"
                        :icon="User"
                        :size="36"
                        style="background-color: #409eff"
                    />
                    <el-avatar v-else :size="36" style="background-color: #67c23a">
                        AI
                    </el-avatar>
                </div>
                <div class="message-content">
                    <div class="message-bubble">
                        <div
                            v-if="message.status === 'sending'"
                            class="typing-indicator"
                        >
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                        <div v-else v-html="formatMessage(message.content)"></div>
                    </div>
                    <div class="message-time">
                        {{ formatTime(message.timestamp) }}
                    </div>
                </div>
                <div
                    v-if="message.role === 'assistant' && message.status !== 'sending'"
                    class="message-actions"
                >
                    <el-button-group size="small">
                        <el-button :icon="Like" @click="likeMessage(message.id)">
                            赞
                        </el-button>
                        <el-button :icon="DisLike" @click="dislikeMessage(message.id)">
                            踩
                        </el-button>
                        <el-button
                            :icon="CopyDocument"
                            @click="copyMessage(message.content)"
                        >
                            复制
                        </el-button>
                    </el-button-group>
                </div>
            </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input">
            <div class="input-toolbar">
                <el-select
                    v-model="chatContext.subject"
                    placeholder="选择科目"
                    size="small"
                    style="width: 120px"
                >
                    <el-option label="数学" value="math" />
                    <el-option label="物理" value="physics" />
                    <el-option label="英语" value="english" />
                    <el-option label="化学" value="chemistry" />
                </el-select>
                <el-select
                    v-model="chatContext.difficulty_level"
                    placeholder="难度级别"
                    size="small"
                    style="width: 120px"
                >
                    <el-option label="基础" value="beginner" />
                    <el-option label="中等" value="intermediate" />
                    <el-option label="高级" value="advanced" />
                </el-select>
            </div>
            <div class="input-area">
                <el-input
                    v-model="currentInput"
                    type="textarea"
                    :rows="3"
                    placeholder="输入您的问题，AI将为您提供详细的解答..."
                    @keydown.ctrl.enter="sendMessage"
                    :disabled="isLoading"
                    resize="none"
                />
                <div class="input-actions">
                    <el-button
                        type="primary"
                        @click="sendMessage"
                        :loading="isLoading"
                        :disabled="!currentInput.trim()"
                        :icon="Position"
                    >
                        发送 (Ctrl+Enter)
                    </el-button>
                </div>
            </div>
        </div>

        <!-- 设置对话框 -->
        <el-dialog v-model="showSettings" title="聊天设置" width="500px">
            <el-form :model="chatSettings" label-width="120px">
                <el-form-item label="AI服务商">
                    <el-radio-group v-model="chatSettings.provider">
                        <el-radio label="qwen">通义千问</el-radio>
                        <el-radio label="kimi">Kimi AI</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="模型选择">
                    <el-select v-model="chatSettings.model" placeholder="选择模型">
                        <el-option
                            v-if="chatSettings.provider === 'qwen'"
                            label="qwen-plus"
                            value="qwen-plus"
                        />
                        <el-option
                            v-if="chatSettings.provider === 'qwen'"
                            label="qwen-max"
                            value="qwen-max"
                        />
                        <el-option
                            v-if="chatSettings.provider === 'kimi'"
                            label="moonshot-v1-8k"
                            value="moonshot-v1-8k"
                        />
                        <el-option
                            v-if="chatSettings.provider === 'kimi'"
                            label="moonshot-v1-32k"
                            value="moonshot-v1-32k"
                        />
                    </el-select>
                </el-form-item>
                <el-form-item label="温度参数">
                    <el-slider
                        v-model="chatSettings.temperature"
                        :min="0"
                        :max="1"
                        :step="0.1"
                        show-input
                    />
                </el-form-item>
                <el-form-item label="回答长度">
                    <el-input-number
                        v-model="chatSettings.max_tokens"
                        :min="100"
                        :max="4000"
                        :step="100"
                    />
                    <div class="setting-help">限制AI回答的最大字数</div>
                </el-form-item>
                <el-form-item label="自动保存">
                    <el-switch v-model="chatSettings.auto_save" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showSettings = false">取消</el-button>
                <el-button type="primary" @click="saveSettings">保存设置</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
    User,
    Delete,
    Setting,
    Position,
    CircleCheck,
    CircleClose,
    CopyDocument,
} from "@element-plus/icons-vue";

// 使用正确的图标名称
const Like = CircleCheck;
const DisLike = CircleClose;
import { chatService } from "@/services/api";
import type {
    ChatMessage,
    ChatRequest,
    ChatContext,
    ChatSettings,
    QuickPrompt,
} from "@/types/chat";

// 响应式数据
const messages = ref<ChatMessage[]>([]);
const currentInput = ref("");
const isLoading = ref(false);
const showSettings = ref(false);
const messagesContainer = ref<HTMLElement>();

// 聊天上下文
const chatContext = reactive<ChatContext>({
    student_id: 1, // TODO: 从用户状态获取
    subject: "math",
    difficulty_level: "intermediate",
});

// 聊天设置
const chatSettings = reactive<ChatSettings>({
    provider: "qwen",
    model: "qwen-plus",
    temperature: 0.7,
    max_tokens: 2000,
    auto_save: true,
    show_thinking_process: false,
});

// 当前AI服务商
const currentProvider = ref<"qwen" | "kimi">("qwen");

// 快捷提示
const quickPrompts = ref<QuickPrompt[]>([
    {
        id: "1",
        title: "作业辅导",
        content: "我有一道数学题不会做，请帮我分析解题思路",
        category: "homework_help",
        subject: "math",
        usage_count: 0,
    },
    {
        id: "2",
        title: "概念解释",
        content: "请详细解释一下这个物理概念的原理和应用",
        category: "concept_explanation",
        subject: "physics",
        usage_count: 0,
    },
    {
        id: "3",
        title: "练习题目",
        content: "请给我出几道相关的练习题来巩固知识点",
        category: "practice_problems",
        usage_count: 0,
    },
    {
        id: "4",
        title: "学习建议",
        content: "请给我一些关于这个学科的学习方法和技巧",
        category: "study_tips",
        usage_count: 0,
    },
]);

// 生成消息ID
const generateMessageId = () => {
    return "msg_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);
};

// 发送消息
const sendMessage = async () => {
    if (!currentInput.value.trim() || isLoading.value) return;

    const userMessage: ChatMessage = {
        id: generateMessageId(),
        role: "user",
        content: currentInput.value.trim(),
        timestamp: new Date().toISOString(),
        status: "sent",
    };

    messages.value.push(userMessage);

    // 创建AI回复占位消息
    const assistantMessage: ChatMessage = {
        id: generateMessageId(),
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
        status: "sending",
    };

    messages.value.push(assistantMessage);

    // 滚动到底部
    await nextTick();
    scrollToBottom();

    // 清空输入
    currentInput.value = "";
    isLoading.value = true;

    try {
        // 准备请求数据
        const request: ChatRequest = {
            messages: messages.value
                .filter((msg) => msg.status !== "sending")
                .map((msg) => ({
                    role: msg.role,
                    content: msg.content,
                    id: msg.id,
                    timestamp: msg.timestamp,
                })),
            provider: chatSettings.provider,
            model: chatSettings.model,
            temperature: chatSettings.temperature,
            max_tokens: chatSettings.max_tokens,
            context: chatContext,
        };

        // 调用AI服务
        const response = await chatService.sendMessage(request);

        if (response.success && response.data) {
            // 更新AI回复
            assistantMessage.content = response.data.response;
            assistantMessage.status = "sent";
        } else {
            throw new Error(response.message || "AI回复失败");
        }
    } catch (error) {
        console.error("发送消息失败:", error);
        assistantMessage.content = "抱歉，AI服务暂时不可用，请稍后重试。";
        assistantMessage.status = "failed";
        ElMessage.error("消息发送失败，请重试");
    } finally {
        isLoading.value = false;
        await nextTick();
        scrollToBottom();
    }
};

// 选择快捷提示
const selectPrompt = (prompt: QuickPrompt) => {
    currentInput.value = prompt.content;
    if (prompt.subject) {
        chatContext.subject = prompt.subject;
    }
    prompt.usage_count++;
};

// 切换AI服务商
const switchProvider = (provider: "qwen" | "kimi") => {
    currentProvider.value = provider;
    chatSettings.provider = provider;
    // 切换相应的默认模型
    if (provider === "qwen") {
        chatSettings.model = "qwen-plus";
    } else if (provider === "kimi") {
        chatSettings.model = "moonshot-v1-8k";
    }
    ElMessage.success(`已切换到${provider === "qwen" ? "通义千问" : "Kimi AI"}`);
};

// 清空聊天
const clearChat = async () => {
    try {
        await ElMessageBox.confirm(
            "确定要清空所有对话记录吗？此操作不可恢复。",
            "确认清空",
            {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning",
            },
        );
        messages.value = [];
        ElMessage.success("对话已清空");
    } catch {
        // 用户取消
    }
};

// 保存设置
const saveSettings = () => {
    currentProvider.value = chatSettings.provider;
    showSettings.value = false;
    ElMessage.success("设置已保存");
};

// 点赞消息
const likeMessage = (_messageId: string) => {
    ElMessage.success("感谢您的反馈！");
};

// 点踩消息
const dislikeMessage = (_messageId: string) => {
    ElMessage.info("我们会继续改进AI的回答质量");
};

// 复制消息
const copyMessage = async (content: string) => {
    try {
        await navigator.clipboard.writeText(content);
        ElMessage.success("已复制到剪贴板");
    } catch {
        ElMessage.error("复制失败");
    }
};

// 格式化消息内容
const formatMessage = (content: string) => {
    return content
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/`(.*?)`/g, "<code>$1</code>");
};

// 格式化时间
const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) {
        return "刚刚";
    } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`;
    } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}小时前`;
    } else {
        return date.toLocaleDateString() + " " + date.toLocaleTimeString().slice(0, 5);
    }
};

// 滚动到底部
const scrollToBottom = () => {
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
};

// 组件挂载
onMounted(() => {
    // 加载设置
    const savedSettings = localStorage.getItem("ai_chat_settings");
    if (savedSettings) {
        Object.assign(chatSettings, JSON.parse(savedSettings));
        currentProvider.value = chatSettings.provider;
    }

    // 欢迎消息
    messages.value.push({
        id: generateMessageId(),
        role: "assistant",
        content:
            "您好！我是AI学习助手，可以帮助您解答学习问题、分析题目、制定学习计划。请告诉我您需要什么帮助？",
        timestamp: new Date().toISOString(),
        status: "sent",
    });
});
</script>

<style scoped>
.ai-chat-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: #f5f7fa;
}

.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    background: white;
    border-bottom: 1px solid #e4e7ed;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.header-left h2 {
    margin: 0;
    color: #303133;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 8px;
}

.quick-prompts {
    padding: 24px;
    background: white;
    margin-bottom: 16px;
}

.quick-prompts h4 {
    margin: 0 0 16px 0;
    color: #606266;
}

.prompt-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
}

.prompt-card {
    padding: 16px;
    background: #f8f9fa;
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
}

.prompt-card:hover {
    background: #ecf5ff;
    border-color: #409eff;
    transform: translateY(-2px);
}

.prompt-title {
    font-weight: 500;
    color: #303133;
    margin-bottom: 8px;
}

.prompt-content {
    color: #606266;
    font-size: 14px;
    line-height: 1.4;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px 24px;
    scroll-behavior: smooth;
}

.message {
    display: flex;
    margin-bottom: 20px;
    animation: fadeIn 0.3s ease-in;
}

.message.user-message {
    flex-direction: row-reverse;
}

.message.user-message .message-content {
    align-items: flex-end;
}

.message.user-message .message-bubble {
    background: #409eff;
    color: white;
    border-radius: 20px 20px 6px 20px;
}

.message.assistant-message .message-bubble {
    background: white;
    color: #303133;
    border: 1px solid #e4e7ed;
    border-radius: 20px 20px 20px 6px;
}

.message-avatar {
    margin: 0 12px;
}

.message-content {
    display: flex;
    flex-direction: column;
    max-width: 70%;
}

.message-bubble {
    padding: 12px 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    word-wrap: break-word;
    line-height: 1.4;
}

.message-time {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    text-align: center;
}

.message-actions {
    display: flex;
    align-items: center;
    margin-left: 12px;
    opacity: 0;
    transition: opacity 0.3s;
}

.message:hover .message-actions {
    opacity: 1;
}

.typing-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #409eff;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
    animation-delay: -0.32s;
}
.typing-indicator span:nth-child(2) {
    animation-delay: -0.16s;
}

@keyframes typing {
    0%,
    80%,
    100% {
        transform: scale(0);
    }
    40% {
        transform: scale(1);
    }
}

.chat-input {
    background: white;
    border-top: 1px solid #e4e7ed;
    padding: 16px 24px;
}

.input-toolbar {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
}

.input-area {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.input-actions {
    display: flex;
    justify-content: flex-end;
}

.setting-help {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .chat-header {
        padding: 12px 16px;
    }

    .header-right {
        flex-direction: column;
        gap: 4px;
    }

    .quick-prompts {
        padding: 16px;
    }

    .prompt-grid {
        grid-template-columns: 1fr;
    }

    .chat-messages {
        padding: 12px 16px;
    }

    .message-content {
        max-width: 85%;
    }

    .chat-input {
        padding: 12px 16px;
    }

    .input-toolbar {
        flex-direction: column;
        gap: 8px;
    }
}
</style>
