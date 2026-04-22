import { apiService } from './api-service.js';
import { API_CONFIG, APP_CONSTANTS } from '../config/api-config.js';

/**
 * Chat Service
 * Handles chat functionality, history, and backend communication
 */
export class ChatService {
    constructor() {
        this.chatHistory = [];
        this.loadChatHistory();
    }

    /**
     * Send message to backend
     * @param {string} message - User message
     * @param {boolean} forceWebSearch - Force web search
     * @returns {Promise} Backend response
     */
    async sendToBackend(message, forceWebSearch = false) {
        try {
            console.log('Sending request to chat endpoint');
            const payload = {
                message: message,
                force_web_search: forceWebSearch
            };
            console.log('Request payload:', payload);
            
            const response = await apiService.post(API_CONFIG.endpoints.chat, payload);
            
            console.log('Chat response:', response);
            return response;
        } catch (error) {
            console.error('Chat service error:', error);
            throw error;
        }
    }

    /**
     * Process chat message with timing and metadata
     * @param {string} message - User message
     * @param {boolean} forceWebSearch - Force web search
     * @returns {Promise} Processed response with metadata
     */
    async processMessage(message, forceWebSearch = false) {
        const startTime = Date.now();
        const response = await this.sendToBackend(message, forceWebSearch);
        const responseTime = Date.now() - startTime;

        // Enhance response with metadata
        const processedResponse = {
            ...response,
            metadata: {
                sources: response.sources_used,
                localSources: response.local_sources || 0,
                webSources: response.web_sources || 0,
                searchStrategy: response.search_strategy || 'local_only',
                chatbotType: response.chatbot_type || 'standard',
                responseTime: Math.round(responseTime / 1000 * 10) / 10,
                usedWebSearch: response.used_web_search || false
            }
        };

        // Save to history
        this.saveChatToHistory(message, response.answer);

        return processedResponse;
    }

    /**
     * Save chat exchange to history
     * @param {string} userMessage - User message
     * @param {string} botResponse - Bot response
     */
    saveChatToHistory(userMessage, botResponse) {
        const chatEntry = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            userMessage,
            botResponse,
            date: new Date().toLocaleDateString()
        };

        this.chatHistory.unshift(chatEntry);
        
        // Limit history size (keep last 100 entries)
        if (this.chatHistory.length > 100) {
            this.chatHistory = this.chatHistory.slice(0, 100);
        }

        try {
            localStorage.setItem(APP_CONSTANTS.chatHistoryKey, JSON.stringify(this.chatHistory));
        } catch (error) {
            console.warn('Could not save chat history to localStorage:', error);
        }
    }

    /**
     * Load chat history from localStorage
     */
    loadChatHistory() {
        try {
            const stored = localStorage.getItem(APP_CONSTANTS.chatHistoryKey);
            if (stored) {
                this.chatHistory = JSON.parse(stored);
            }
        } catch (error) {
            console.warn('Could not load chat history from localStorage:', error);
            this.chatHistory = [];
        }
    }

    /**
     * Clear chat history
     */
    clearChatHistory() {
        this.chatHistory = [];
        try {
            localStorage.removeItem(APP_CONSTANTS.chatHistoryKey);
        } catch (error) {
            console.warn('Could not clear chat history from localStorage:', error);
        }
    }

    /**
     * Get chat history
     * @returns {Array} Chat history entries
     */
    getChatHistory() {
        return this.chatHistory;
    }

    /**
     * Search chat history
     * @param {string} query - Search query
     * @returns {Array} Filtered chat history
     */
    searchChatHistory(query) {
        if (!query) return this.chatHistory;
        
        const lowerQuery = query.toLowerCase();
        return this.chatHistory.filter(entry => 
            entry.userMessage.toLowerCase().includes(lowerQuery) ||
            entry.botResponse.toLowerCase().includes(lowerQuery)
        );
    }

    /**
     * Get chat statistics
     * @returns {Object} Chat statistics
     */
    getChatStatistics() {
        return {
            totalChats: this.chatHistory.length,
            latestChat: this.chatHistory.length > 0 ? this.chatHistory[0].timestamp : null,
            oldestChat: this.chatHistory.length > 0 ? this.chatHistory[this.chatHistory.length - 1].timestamp : null
        };
    }
}

// Export singleton instance
export const chatService = new ChatService();