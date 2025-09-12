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
  const saveReportBtn = document.getElementById('saveReportBtn');
  const saveOptions = document.getElementById('saveOptions');
  const savePdfBtn = document.getElementById('savePdfBtn');
  const saveHtmlBtn = document.getElementById('saveHtmlBtn');

  // 存储当前批改数据，用于保存报告
  let currentReportData = null;

  // 初始化时隐藏保存按钮
  if (saveReportBtn) {
    saveReportBtn.style.display = 'none';
  }

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
    // 保存当前数据用于报告生成
    currentReportData = data;

    // 生成结果HTML
    const resultHTML = generateResultHTML(data);
    resultContent.innerHTML = resultHTML;

    // 显示结果区域和保存按钮
    resultSection.style.display = 'block';
    if (saveReportBtn) {
      saveReportBtn.style.display = 'inline-flex';
    }

    // 平滑滚动到结果
    resultSection.scrollIntoView({ behavior: 'smooth' });
  }

  // 隐藏结果
  function hideResult() {
    resultSection.style.display = 'none';
    if (saveReportBtn) {
      saveReportBtn.style.display = 'none';
    }
    if (saveOptions) {
      saveOptions.style.display = 'none';
    }
    currentReportData = null;
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

  // 保存报告相关事件处理
  if (saveReportBtn) {
    saveReportBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      saveOptions.style.display = saveOptions.style.display === 'block' ? 'none' : 'block';
    });
  }

  // 点击外部关闭保存选项
  document.addEventListener('click', function (e) {
    if (!saveReportBtn.contains(e.target) && !saveOptions.contains(e.target)) {
      saveOptions.style.display = 'none';
    }
  });

  // 保存为PDF
  if (savePdfBtn) {
    savePdfBtn.addEventListener('click', function () {
      saveOptions.style.display = 'none';
      if (currentReportData) {
        generatePdfReport(currentReportData);
      }
    });
  }

  // 保存为HTML
  if (saveHtmlBtn) {
    saveHtmlBtn.addEventListener('click', function () {
      saveOptions.style.display = 'none';
      if (currentReportData) {
        generateHtmlReport(currentReportData);
      }
    });
  }

  // 生成PDF报告
  function generatePdfReport(data) {
    try {
      showNotification('正在生成PDF报告...', 'info');

      // 创建PDF内容
      const reportContent = generateReportContent(data);
      const filename = `作业批改报告_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.pdf`;

      // 使用简单的方法：创建一个新窗口并打印
      const printWindow = window.open('', '_blank');
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>作业批改报告</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
            .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; }
            .section { margin-bottom: 25px; }
            .question-card { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 8px; }
            .correct { border-left: 4px solid #28a745; }
            .incorrect { border-left: 4px solid #dc3545; }
            .metadata { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 20px; }
            @media print { body { margin: 0; } }
          </style>
        </head>
        <body>${reportContent}</body>
        </html>
      `);
      printWindow.document.close();

      setTimeout(() => {
        printWindow.print();
        showNotification('PDF报告生成完成！请在打印对话框中选择"保存为PDF"', 'success');
      }, 500);

    } catch (error) {
      console.error('PDF生成失败:', error);
      showNotification('PDF生成失败，请稍后重试', 'error');
    }
  }

  // 生成HTML报告
  function generateHtmlReport(data) {
    try {
      const reportContent = generateReportContent(data);
      const filename = `作业批改报告_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.html`;

      const htmlContent = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>作业批改报告</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; line-height: 1.6; color: #333; }
    .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; }
    .section { margin-bottom: 25px; }
    .ocr-text { background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #ddd; font-family: 'Courier New', monospace; white-space: pre-wrap; }
    .question-card { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 8px; }
    .correct { border-left: 4px solid #28a745; background: #f8fff9; }
    .incorrect { border-left: 4px solid #dc3545; background: #fff8f8; }
    .question-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; font-weight: bold; }
    .question-status.correct { color: #28a745; }
    .question-status.incorrect { color: #dc3545; }
    .answer-section, .analysis-section { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 6px; }
    .knowledge-tag { display: inline-block; background: #007bff; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; margin: 2px; }
    .metadata { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 20px; font-size: 0.9rem; color: #6c757d; }
    .overall-score { text-align: center; font-size: 2rem; font-weight: bold; color: #007bff; margin: 20px 0; }
  </style>
</head>
<body>
  ${reportContent}
</body>
</html>`;

      // 创建下载链接
      const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      showNotification('HTML报告保存成功！', 'success');
    } catch (error) {
      console.error('HTML生成失败:', error);
      showNotification('HTML报告生成失败，请稍后重试', 'error');
    }
  }

  // 生成报告内容
  function generateReportContent(data) {
    const { ocr_text, correction, metadata } = data;
    const currentTime = new Date().toLocaleString('zh-CN');

    let content = `
      <div class="header">
        <h1>🎓 AI Tutor 作业批改报告</h1>
        <p>生成时间：${currentTime}</p>
        <p>科目：${metadata.subject || '数学'} | AI模型：${metadata.provider}</p>
      </div>
    `;

    // 总体得分
    if (correction.overall_score !== undefined) {
      content += `
        <div class="section">
          <h2>📊 总体得分</h2>
          <div class="overall-score">${correction.overall_score}分</div>
        </div>
      `;
    }

    // OCR识别结果
    content += `
      <div class="section">
        <h2>🔍 OCR识别结果</h2>
        <div class="ocr-text">${escapeHtml(ocr_text)}</div>
      </div>
    `;

    // 总体建议
    if (correction.overall_suggestions) {
      content += `
        <div class="section">
          <h2>📝 总体建议</h2>
          <p>${escapeHtml(correction.overall_suggestions)}</p>
        </div>
      `;
    }

    // 题目详情
    if (correction.questions && correction.questions.length > 0) {
      content += '<div class="section"><h2>📋 题目详情</h2>';

      correction.questions.forEach(question => {
        const correctClass = question.is_correct ? 'correct' : 'incorrect';
        const statusText = question.is_correct ? '✅ 正确' : '❌ 错误';

        content += `
          <div class="question-card ${correctClass}">
            <div class="question-header">
              <span>第 ${question.question_number || '?'} 题</span>
              <span class="question-status ${correctClass}">${statusText}</span>
              <span>${question.score || 0}/${question.max_score || 0} 分</span>
            </div>

            ${question.question_text ? `
              <div class="answer-section">
                <h4>📝 题目内容</h4>
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
              <div class="answer-section">
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
              <div style="margin-top: 15px;">
                <h4>🎯 涉及知识点</h4>
                ${question.knowledge_points.map(point =>
          `<span class="knowledge-tag">${escapeHtml(point)}</span>`
        ).join('')}
              </div>
            ` : ''}
          </div>
        `;
      });

      content += '</div>';
    }

    // 元数据信息
    content += `
      <div class="metadata">
        <h3>📋 处理信息</h3>
        <p><strong>文件名：</strong>${metadata.filename || '未知'}</p>
        <p><strong>处理时间：</strong>${metadata.processing_time}秒</p>
        <p><strong>文件大小：</strong>${(metadata.file_size / 1024 / 1024).toFixed(2)}MB</p>
        <p><strong>AI模型：</strong>${metadata.provider}</p>
        <p><strong>题目数量：</strong>${metadata.questions_parsed || 0}题</p>
        <p><strong>生成时间：</strong>${currentTime}</p>
      </div>
    `;

    return content;
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
