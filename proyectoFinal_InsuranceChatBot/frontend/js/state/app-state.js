import { getStorageItem, setStorageItem } from '../utils/storage-utils.js';
import { APP_CONSTANTS } from '../config/api-config.js';

/**
 * Application State Management
 * Centralized state management for the application
 */
export class AppState {
    constructor() {
        this.state = {
            // UI State
            isLoading: false,
            currentView: 'chat',
            sidebarOpen: false,
            
            // Chat State
            chatHistory: [],
            currentMessage: '',
            isTyping: false,
            
            // Document State
            documents: [],
            documentFilters: {
                source: '',
                document_type: '',
                file_name: ''
            },
            documentPagination: {
                currentPage: 1,
                hasMore: false,
                totalReturned: 0
            },
            
            // Statistics State
            statistics: {
                totalQuestions: 0,
                totalSources: 0,
                totalResponseTime: 0,
                totalWebSources: 0,
                hybridSearches: 0
            },
            
            // Server State
            serverHealth: null,
            serverCapabilities: {
                hybridMode: false,
                chatbotType: 'standard'
            },
            
            // Error State
            lastError: null,
            errorHistory: []
        };
        
        this.subscribers = new Map();
        this.loadPersistedState();
    }

    /**
     * Subscribe to state changes
     * @param {string} key - State key to watch
     * @param {Function} callback - Callback function
     * @returns {Function} Unsubscribe function
     */
    subscribe(key, callback) {
        if (!this.subscribers.has(key)) {
            this.subscribers.set(key, new Set());
        }
        
        this.subscribers.get(key).add(callback);
        
        // Return unsubscribe function
        return () => {
            const callbacks = this.subscribers.get(key);
            if (callbacks) {
                callbacks.delete(callback);
            }
        };
    }

    /**
     * Get state value
     * @param {string} key - State key
     * @returns {*} State value
     */
    get(key) {
        return this.getNestedValue(this.state, key);
    }

    /**
     * Set state value
     * @param {string} key - State key
     * @param {*} value - New value
     * @param {boolean} persist - Whether to persist to localStorage
     */
    set(key, value, persist = false) {
        const oldValue = this.get(key);
        this.setNestedValue(this.state, key, value);
        
        // Notify subscribers
        this.notifySubscribers(key, value, oldValue);
        
        // Persist if requested
        if (persist) {
            this.persistState(key, value);
        }
    }

    /**
     * Update state with partial object
     * @param {Object} updates - Updates to apply
     * @param {boolean} persist - Whether to persist to localStorage
     */
    update(updates, persist = false) {
        Object.keys(updates).forEach(key => {
            this.set(key, updates[key], persist);
        });
    }

    /**
     * Reset state to initial values
     * @param {Array} keys - Keys to reset (all if empty)
     */
    reset(keys = []) {
        const initialState = this.getInitialState();
        
        if (keys.length === 0) {
            this.state = initialState;
            this.notifyAllSubscribers();
        } else {
            keys.forEach(key => {
                const initialValue = this.getNestedValue(initialState, key);
                this.set(key, initialValue);
            });
        }
    }

    /**
     * Get entire state (read-only)
     * @returns {Object} Current state
     */
    getState() {
        return { ...this.state };
    }

    /**
     * Load persisted state from localStorage
     */
    loadPersistedState() {
        // Load chat history
        const chatHistory = getStorageItem(APP_CONSTANTS.chatHistoryKey, []);
        this.set('chatHistory', chatHistory);
        
        // Load statistics
        const statistics = getStorageItem(APP_CONSTANTS.statisticsKey, this.state.statistics);
        this.set('statistics', statistics);
        
        // Load document filters
        const documentFilters = getStorageItem('documentFilters', this.state.documentFilters);
        this.set('documentFilters', documentFilters);
    }

    /**
     * Persist specific state to localStorage
     * @param {string} key - State key
     * @param {*} value - Value to persist
     */
    persistState(key, value) {
        const persistableKeys = {
            'chatHistory': APP_CONSTANTS.chatHistoryKey,
            'statistics': APP_CONSTANTS.statisticsKey,
            'documentFilters': 'documentFilters'
        };
        
        const storageKey = persistableKeys[key];
        if (storageKey) {
            setStorageItem(storageKey, value);
        }
    }

    /**
     * Get initial state
     * @returns {Object} Initial state object
     */
    getInitialState() {
        return {
            isLoading: false,
            currentView: 'chat',
            sidebarOpen: false,
            chatHistory: [],
            currentMessage: '',
            isTyping: false,
            documents: [],
            documentFilters: {
                source: '',
                document_type: '',
                file_name: ''
            },
            documentPagination: {
                currentPage: 1,
                hasMore: false,
                totalReturned: 0
            },
            statistics: {
                totalQuestions: 0,
                totalSources: 0,
                totalResponseTime: 0,
                totalWebSources: 0,
                hybridSearches: 0
            },
            serverHealth: null,
            serverCapabilities: {
                hybridMode: false,
                chatbotType: 'standard'
            },
            lastError: null,
            errorHistory: []
        };
    }

    /**
     * Helper method to get nested value from object
     * @param {Object} obj - Object to search
     * @param {string} path - Dot-separated path
     * @returns {*} Value at path
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            return current && current[key] !== undefined ? current[key] : undefined;
        }, obj);
    }

    /**
     * Helper method to set nested value in object
     * @param {Object} obj - Object to modify
     * @param {string} path - Dot-separated path
     * @param {*} value - Value to set
     */
    setNestedValue(obj, path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        const target = keys.reduce((current, key) => {
            if (!current[key] || typeof current[key] !== 'object') {
                current[key] = {};
            }
            return current[key];
        }, obj);
        
        target[lastKey] = value;
    }

    /**
     * Notify subscribers of state changes
     * @param {string} key - Changed key
     * @param {*} newValue - New value
     * @param {*} oldValue - Old value
     */
    notifySubscribers(key, newValue, oldValue) {
        const callbacks = this.subscribers.get(key);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error('Error in state subscriber:', error);
                }
            });
        }
        
        // Also notify wildcard subscribers
        const wildcardCallbacks = this.subscribers.get('*');
        if (wildcardCallbacks) {
            wildcardCallbacks.forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error('Error in wildcard state subscriber:', error);
                }
            });
        }
    }

    /**
     * Notify all subscribers
     */
    notifyAllSubscribers() {
        this.subscribers.forEach((callbacks, key) => {
            if (key !== '*') {
                const value = this.get(key);
                callbacks.forEach(callback => {
                    try {
                        callback(value, undefined, key);
                    } catch (error) {
                        console.error('Error in state subscriber:', error);
                    }
                });
            }
        });
    }

    /**
     * Add error to error history
     * @param {Error|string} error - Error to add
     */
    addError(error) {
        const errorObj = {
            message: typeof error === 'string' ? error : error.message,
            timestamp: new Date().toISOString(),
            stack: error.stack || null
        };
        
        const errorHistory = [...this.get('errorHistory')];
        errorHistory.unshift(errorObj);
        
        // Keep only last 10 errors
        if (errorHistory.length > 10) {
            errorHistory.splice(10);
        }
        
        this.set('lastError', errorObj);
        this.set('errorHistory', errorHistory);
    }

    /**
     * Clear error state
     */
    clearError() {
        this.set('lastError', null);
    }

    /**
     * Clear all errors
     */
    clearAllErrors() {
        this.set('lastError', null);
        this.set('errorHistory', []);
    }

    /**
     * Toggle loading state
     * @param {boolean} isLoading - Loading state
     */
    setLoading(isLoading) {
        this.set('isLoading', isLoading);
    }

    /**
     * Set current view
     * @param {string} view - View name
     */
    setCurrentView(view) {
        this.set('currentView', view);
    }

    /**
     * Toggle sidebar
     * @param {boolean} open - Whether sidebar should be open
     */
    setSidebarOpen(open) {
        this.set('sidebarOpen', open);
    }

    /**
     * Add message to chat history
     * @param {Object} message - Message object
     */
    addChatMessage(message) {
        const chatHistory = [...this.get('chatHistory')];
        chatHistory.unshift(message);
        
        // Keep only last 100 messages
        if (chatHistory.length > 100) {
            chatHistory.splice(100);
        }
        
        this.set('chatHistory', chatHistory, true);
    }

    /**
     * Update statistics
     * @param {Object} stats - Statistics update
     */
    updateStatistics(stats) {
        const currentStats = this.get('statistics');
        const updatedStats = { ...currentStats, ...stats };
        this.set('statistics', updatedStats, true);
    }

    /**
     * Set documents
     * @param {Array} documents - Documents array
     */
    setDocuments(documents) {
        this.set('documents', documents);
    }

    /**
     * Update document filters
     * @param {Object} filters - Filter updates
     */
    updateDocumentFilters(filters) {
        const currentFilters = this.get('documentFilters');
        const updatedFilters = { ...currentFilters, ...filters };
        this.set('documentFilters', updatedFilters, true);
    }

    /**
     * Update document pagination
     * @param {Object} pagination - Pagination updates
     */
    updateDocumentPagination(pagination) {
        const currentPagination = this.get('documentPagination');
        const updatedPagination = { ...currentPagination, ...pagination };
        this.set('documentPagination', updatedPagination);
    }

    /**
     * Set server health
     * @param {Object} health - Server health data
     */
    setServerHealth(health) {
        this.set('serverHealth', health);
        
        if (health) {
            this.set('serverCapabilities', {
                hybridMode: health.hybrid_chatbot_ready || false,
                chatbotType: health.chatbot_type || 'standard'
            });
        }
    }
}

// Export singleton instance
export const appState = new AppState();