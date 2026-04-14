// src/utils/logger.js
const isDev = import.meta.env.MODE === 'development'

class Logger {
  static levels = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3,
  }

  static currentLevel = isDev ? this.levels.DEBUG : this.levels.ERROR

  static setLevel(level) {
    this.currentLevel = level
  }

  static debug(...args) {
    if (this.currentLevel <= this.levels.DEBUG) {
      console.debug('[DEBUG]', ...args)
    }
  }

  static info(...args) {
    if (this.currentLevel <= this.levels.INFO) {
      console.info('[INFO]', ...args)
    }
  }

  static warn(...args) {
    if (this.currentLevel <= this.levels.WARN) {
      console.warn('[WARN]', ...args)
    }
  }

  static error(...args) {
    if (this.currentLevel <= this.levels.ERROR) {
      console.error('[ERROR]', ...args)
    }
  }

  static http(method, url, data) {
    if (this.currentLevel <= this.levels.DEBUG) {
      console.debug(`[HTTP ${method}] ${url}`, data || '')
    }
  }
}

export default Logger
