import { API_CONFIG } from '../config/api-config.js';

/**
 * Centralized API Service
 * Handles all HTTP communication with the backend
 */
export class ApiService {
    constructor() {
        this.baseUrl = API_CONFIG.baseUrl;
        this.timeout = API_CONFIG.timeout;
        this.defaultHeaders = API_CONFIG.headers;
    }

    /**
     * Generic HTTP request method
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise} Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            timeout: this.timeout,
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        console.log('API Request:', {
            url,
            method: config.method || 'GET',
            headers: config.headers,
            body: config.body
        });

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(url, {
                ...config,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            console.log('API Response status:', response.status);
            console.log('API Response headers:', response.headers);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('API Error response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}, response: ${errorText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    /**
     * GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} headers - Additional headers
     * @returns {Promise} Response data
     */
    async get(endpoint, headers = {}) {
        return this.request(endpoint, {
            method: 'GET',
            headers
        });
    }

    /**
     * POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request payload
     * @param {Object} headers - Additional headers
     * @returns {Promise} Response data
     */
    async post(endpoint, data = {}, headers = {}) {
        return this.request(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...headers
            },
            body: JSON.stringify(data)
        });
    }

    /**
     * POST request with FormData (for file uploads)
     * @param {string} endpoint - API endpoint
     * @param {FormData} formData - Form data
     * @param {Object} headers - Additional headers
     * @returns {Promise} Response data
     */
    async postFormData(endpoint, formData, headers = {}) {
        // Don't set Content-Type for FormData, let browser set it with boundary
        const { 'Content-Type': _, ...restHeaders } = { ...this.defaultHeaders, ...headers };
        
        return this.request(endpoint, {
            method: 'POST',
            headers: restHeaders,
            body: formData
        });
    }

    /**
     * Health check
     * @returns {Promise} Health status
     */
    async healthCheck() {
        return this.get(API_CONFIG.endpoints.health);
    }

    /**
     * Get server statistics
     * @returns {Promise} Server statistics
     */
    async getStats() {
        return this.get(API_CONFIG.endpoints.stats);
    }
}

// Export singleton instance
export const apiService = new ApiService();