// src/composables/useDeleteConfirmation.js
import { ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'

export function useDeleteConfirmation() {
  /**
   * 显示带倒计时的删除确认对话框
   * @param {Object} options - 配置选项
   * @param {string} options.title - 对话框标题
   * @param {string} options.message - 对话框消息
   * @param {number} options.countdown - 倒计时秒数，默认3秒
   * @param {Function} options.onConfirm - 确认回调函数
   * @param {Function} options.onCancel - 取消回调函数
   */
  const showDeleteConfirmation = (options = {}) => {
    const {
      title = '系统提示',
      message = '此操作不可撤销！',
      countdown = 3,
      onConfirm,
      onCancel,
    } = options

    return new Promise((resolve, reject) => {
      let remainingTime = countdown
      let confirmButtonText = `确定 (${remainingTime}s)`

      // 创建消息框实例
      const messageBoxInstance = ElMessageBox.confirm(message, title, {
        confirmButtonText,
        cancelButtonText: '取消',
        type: 'warning',
        distinguishCancelAndClose: true,
        beforeClose: (action, instance, done) => {
          if (action === 'confirm' && remainingTime > 0) {
            // 如果还在倒计时中，阻止关闭
            return false
          }
          done()
        },
      })

      // 立即设置按钮为禁用状态
      setTimeout(() => {
        const confirmBtn = document.querySelector('.el-message-box__btns .el-button--primary')
        if (confirmBtn) {
          confirmBtn.disabled = true
          confirmBtn.classList.add('is-disabled')
          confirmBtn.style.opacity = '0.5'
          confirmBtn.style.cursor = 'not-allowed'
        }
      }, 0)

      // 倒计时逻辑
      const timer = setInterval(() => {
        remainingTime--

        if (remainingTime > 0) {
          confirmButtonText = `确定 (${remainingTime}s)`
          // 更新按钮状态
          const confirmBtn = document.querySelector('.el-message-box__btns .el-button--primary')
          if (confirmBtn) {
            confirmBtn.textContent = confirmButtonText
            confirmBtn.disabled = true
            confirmBtn.classList.add('is-disabled')
            confirmBtn.style.opacity = '0.5'
            confirmBtn.style.cursor = 'not-allowed'
          }
        } else {
          // 倒计时结束，启用确认按钮
          clearInterval(timer)
          const confirmBtn = document.querySelector('.el-message-box__btns .el-button--primary')
          if (confirmBtn) {
            confirmBtn.textContent = '确定'
            confirmBtn.disabled = false
            confirmBtn.classList.remove('is-disabled')
            confirmBtn.style.opacity = ''
            confirmBtn.style.cursor = ''
          }
        }
      }, 1000)

      // 处理确认和取消
      messageBoxInstance
        .then(() => {
          clearInterval(timer)
          if (onConfirm) {
            onConfirm()
          }
          resolve(true)
        })
        .catch((action) => {
          clearInterval(timer)
          if (action === 'cancel' && onCancel) {
            onCancel()
          }
          reject(action)
        })
    })
  }

  return {
    showDeleteConfirmation,
  }
}
