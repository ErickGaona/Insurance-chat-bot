/**
 * API Configuration
 * Centralized configuration for all API endpoints and settings
 */
export const API_CONFIG = {
    baseUrl: 'http://localhost:5000',
    endpoints: {
        chat: '/api/v1/chat',
        health: '/api/v1/health',
        stats: '/api/v1/stats',
        documents: '/api/v1/documents',
        documentsUpload: '/api/v1/documents/'
    },
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json; charset=utf-8'
    },
    // Request configuration
    retryAttempts: 3,
    retryDelay: 1000,
    // Upload configuration
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedFileTypes: ['.pdf', '.txt', '.doc', '.docx']
};

/**
 * Application Constants
 */
export const APP_CONSTANTS = {
    maxChatInputLength: 1000,
    chatHistoryKey: 'chatHistory',
    statisticsKey: 'statistics',
    autoResizeMaxHeight: 200,
    errorToastDuration: 5000,
    loadingSpinnerDelay: 500
};

/**
 * UI Configuration
 */
export const UI_CONFIG = {
    animations: {
        fadeIn: 'fadeIn 0.3s ease-in',
        slideUp: 'slideUp 0.3s ease-out',
        pulse: 'pulse 1s infinite'
    },
    themes: {
        default: 'light',
        available: ['light', 'dark']
    }
};