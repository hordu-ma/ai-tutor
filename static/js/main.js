// AI Tutor 主JavaScript文件

document.addEventListener('DOMContentLoaded', function () {
  const homeworkForm = document.getElementById('homeworkForm');
  const fileUploadArea = document.getElementById('fileUploadArea');
  const homeworkFile = document.getElementById('homeworkFile');
  const filePreview = document.getElementById('filePreview');
  const previewImage = document.getElementById('previewImage');
  const fileName = document.getElementById('fileName');
  const submitBtn = document.getElementById('submitBtn');
  const btnText = submitBtn.querySelector('.btn-text');
  const loadingSpinner = submitBtn.querySelector('.loading-spinner');
  const resultSection = document.getElementById('resultSection');
  const resultContent = document.getElementById('resultContent');

  // 文件拖拽上传功能
  fileUploadArea.addEventListener('dragover', function (e) {
    e.preventDefault();
    fileUploadArea.classList.add('dragover');
  });

  fileUploadArea.addEventListener('dragleave', function (e) {
    e.preventDefault();
    fileUploadArea.classList.remove('dragover');
  });

  fileUploadArea.addEventListener('drop', function (e) {
    e.preventDefault();
    fileUploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  });

  // 文件选择事件
  homeworkFile.addEventListener('change', function (e) {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  });

  // 处理文件选择
  function handleFileSelect(file) {
    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      showNotification('请选择有效的图片文件（JPG、PNG、WEBP）', 'error');
      return;
    }

    // 验证文件大小（10MB）
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      showNotification('文件大小不能超过 10MB', 'error');
      return;
    }

    // 关键修复：将拖拽选择的文件设置到input元素中
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    homeworkFile.files = dataTransfer.files;

    // 显示预览
    const reader = new FileReader();
    reader.onload = function (e) {
      previewImage.src = e.target.result;
      fileName.textContent = `文件名：${file.name}`;

      // 隐藏上传提示，显示预览
      document.querySelector('.upload-placeholder').style.display = 'none';
      filePreview.style.display = 'block';
    };
    reader.readAsDataURL(file);

    showNotification('文件选择成功！', 'success');
  }

  // 表单提交事件
  homeworkForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData(homeworkForm);

    // 验证表单
    if (!homeworkFile.files[0]) {
      showNotification('请选择作业图片', 'error');
      return;
    }

    // 设置加载状态
    setLoadingState(true);
    hideResult();

    try {
      const response = await fetch('/api/v1/homework/grade', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok && data.success) {
        showNotification('作业批改完成！', 'success');
        displayResult(data.data);
      } else {
        throw new Error(data.detail || data.message || '批改失败');
      }

    } catch (error) {
      console.error('批改失败:', error);
      showNotification(`批改失败: ${error.message}`, 'error');
    } finally {
      setLoadingState(false);
    }
  });

  // 设置加载状态
  function setLoadingState(loading) {
    if (loading) {
      submitBtn.disabled = true;
      btnText.style.display = 'none';
      loadingSpinner.style.display = 'block';
      submitBtn.classList.add('loading');
    } else {
      submitBtn.disabled = false;
      btnText.style.display = 'block';
      loadingSpinner.style.display = 'none';
      submitBtn.classList.remove('loading');
    }
  }

  // 显示结果
  function displayResult(data) {
    // 生成结果HTML
    const resultHTML = generateResultHTML(data);
    resultContent.innerHTML = resultHTML;

    // 显示结果区域
    resultSection.style.display = 'block';

    // 平滑滚动到结果
    resultSection.scrollIntoView({ behavior: 'smooth' });
  }

  // 隐藏结果
  function hideResult() {
    resultSection.style.display = 'none';
  }

  // 生成结果HTML
  function generateResultHTML(data) {
    const { ocr_text, correction, metadata } = data;

    let html = `
            <div class="ocr-section">
                <h3>🔍 OCR识别结果</h3>
                <div class="ocr-text">${escapeHtml(ocr_text)}</div>
            </div>

            <div class="correction-section">
                <h3>✅ AI批改结果</h3>
        `;

    // 总体得分
    if (correction.overall_score !== undefined) {
      html += `
                <div class="overall-score">
                    <h3>总体得分</h3>
                    <div class="score">${correction.overall_score}</div>
                    <p>使用 ${metadata.provider} 模型批改</p>
                </div>
            `;
    }

    // 总体建议
    if (correction.overall_suggestions) {
      html += `
                <div class="analysis-section">
                    <h4>📝 总体建议</h4>
                    <p>${escapeHtml(correction.overall_suggestions)}</p>
                </div>
            `;
    }

    // 题目详情
    if (correction.questions && correction.questions.length > 0) {
      html += '<div class="questions-list"><h3>📋 题目详情</h3>';

      correction.questions.forEach(question => {
        const correctClass = question.is_correct ? 'correct' : 'incorrect';
        const statusText = question.is_correct ? '✅ 正确' : '❌ 错误';

        html += `
                    <div class="question-card ${correctClass}">
                        <div class="question-header">
                            <span class="question-number">第 ${question.question_number || '?'} 题</span>
                            <span class="question-status ${correctClass}">${statusText}</span>
                            <span class="question-score">${question.score || 0}/${question.max_score || 0} 分</span>
                        </div>

                        <div class="question-content">
                            ${question.question_text ? `
                                <div class="answer-section">
                                    <h4>📖 题目</h4>
                                    <p>${escapeHtml(question.question_text)}</p>
                                </div>
                            ` : ''}

                            ${question.student_answer ? `
                                <div class="answer-section">
                                    <h4>✏️ 学生答案</h4>
                                    <p>${escapeHtml(question.student_answer)}</p>
                                </div>
                            ` : ''}

                            ${question.correct_answer ? `
                                <div class="correct-answer-section">
                                    <h4>✅ 正确答案</h4>
                                    <p>${escapeHtml(question.correct_answer)}</p>
                                </div>
                            ` : ''}

                            ${question.error_analysis ? `
                                <div class="analysis-section">
                                    <h4>🔍 错误分析</h4>
                                    <p>${escapeHtml(question.error_analysis)}</p>
                                </div>
                            ` : ''}

                            ${question.solution_steps && question.solution_steps.length > 0 ? `
                                <div class="analysis-section">
                                    <h4>📚 解题步骤</h4>
                                    <ol>
                                        ${question.solution_steps.map(step => `<li>${escapeHtml(step)}</li>`).join('')}
                                    </ol>
                                </div>
                            ` : ''}

                            ${question.knowledge_points && question.knowledge_points.length > 0 ? `
                                <div class="knowledge-points">
                                    <h4>🎯 涉及知识点</h4>
                                    ${question.knowledge_points.map(point =>
          `<span class="knowledge-tag">${escapeHtml(point)}</span>`
        ).join('')}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
      });

      html += '</div>';
    }

    html += `
            </div>
            <div class="metadata-section" style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; font-size: 0.9rem; color: #6c757d;">
                处理时间: ${metadata.processing_time}秒 | 文件大小: ${(metadata.file_size / 1024 / 1024).toFixed(2)}MB | AI模型: ${metadata.provider}
            </div>
        `;

    return html;
  }

  // HTML转义
  function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // 显示通知
  function showNotification(message, type = 'info') {
    // 移除现有通知
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
      existingNotification.remove();
    }

    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    // 添加样式
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: slideIn 0.3s ease;
        `;

    // 设置颜色
    switch (type) {
      case 'success':
        notification.style.background = '#2ecc71';
        break;
      case 'error':
        notification.style.background = '#e74c3c';
        break;
      case 'warning':
        notification.style.background = '#f39c12';
        break;
      default:
        notification.style.background = '#3498db';
    }

    // 添加到页面
    document.body.appendChild(notification);

    // 3秒后自动移除
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
      }
    }, 3000);
  }

  // 添加动画样式
  const style = document.createElement('style');
  style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
  document.head.appendChild(style);
});
