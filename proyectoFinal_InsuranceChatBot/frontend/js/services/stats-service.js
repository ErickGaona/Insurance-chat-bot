import { apiService } from './api-service.js';
import { API_CONFIG, APP_CONSTANTS } from '../config/api-config.js';

/**
 * Statistics Service
 * Handles application statistics tracking and display
 */
export class StatsService {
    constructor() {
        this.statistics = {
            totalQuestions: 0,
            totalSources: 0,
            totalResponseTime: 0,
            totalWebSources: 0,
            hybridSearches: 0
        };
        
        this.loadStatistics();
    }

    /**
     * Update statistics with new chat data
     * @param {number} sources - Number of sources used
     * @param {number} responseTime - Response time in milliseconds
     * @param {number} webSources - Number of web sources used
     * @param {boolean} usedWebSearch - Whether web search was used
     */
    updateStats(sources, responseTime, webSources = 0, usedWebSearch = false) {
        this.statistics.totalQuestions++;
        this.statistics.totalSources += sources;
        this.statistics.totalResponseTime += responseTime;
        this.statistics.totalWebSources += webSources;
        
        if (usedWebSearch) {
            this.statistics.hybridSearches++;
        }
        
        this.saveStatistics();
        return this.getCalculatedStats();
    }

    /**
     * Get calculated statistics
     * @returns {Object} Calculated statistics
     */
    getCalculatedStats() {
        const avgResponseTime = this.statistics.totalQuestions > 0 
            ? Math.round(this.statistics.totalResponseTime / this.statistics.totalQuestions / 100) / 10
            : 0;

        const hybridUsagePercent = this.statistics.totalQuestions > 0
            ? Math.round((this.statistics.hybridSearches / this.statistics.totalQuestions) * 100)
            : 0;

        const avgSourcesPerQuery = this.statistics.totalQuestions > 0
            ? Math.round((this.statistics.totalSources / this.statistics.totalQuestions) * 10) / 10
            : 0;

        return {
            ...this.statistics,
            avgResponseTime,
            hybridUsagePercent,
            avgSourcesPerQuery
        };
    }

    /**
     * Load backend statistics
     * @returns {Promise} Backend statistics
     */
    async loadBackendStats() {
        try {
            const response = await apiService.get(API_CONFIG.endpoints.stats);
            
            if (response && response.stats) {
                return {
                    totalDocuments: response.stats.total_documents || 0,
                    documentTypes: response.stats.document_types || [],
                    sources: response.stats.sources || [],
                    lastUpdated: response.stats.last_updated || null,
                    dbSize: response.stats.db_size || null,
                    averageDocumentLength: response.stats.average_document_length || 0
                };
            }
            
            return null;
        } catch (error) {
            console.warn('Could not load backend stats:', error);
            return null;
        }
    }

    /**
     * Get comprehensive statistics combining local and backend data
     * @returns {Promise} Combined statistics
     */
    async getComprehensiveStats() {
        const localStats = this.getCalculatedStats();
        const backendStats = await this.loadBackendStats();
        
        return {
            local: localStats,
            backend: backendStats,
            combined: {
                ...localStats,
                ...backendStats
            }
        };
    }

    /**
     * Reset local statistics
     */
    resetStatistics() {
        this.statistics = {
            totalQuestions: 0,
            totalSources: 0,
            totalResponseTime: 0,
            totalWebSources: 0,
            hybridSearches: 0
        };
        
        this.saveStatistics();
    }

    /**
     * Load statistics from localStorage
     */
    loadStatistics() {
        try {
            const saved = localStorage.getItem(APP_CONSTANTS.statisticsKey);
            if (saved) {
                this.statistics = { ...this.statistics, ...JSON.parse(saved) };
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
            this.statistics = {
                totalQuestions: 0,
                totalSources: 0,
                totalResponseTime: 0,
                totalWebSources: 0,
                hybridSearches: 0
            };
        }
    }

    /**
     * Save statistics to localStorage
     */
    saveStatistics() {
        try {
            localStorage.setItem(APP_CONSTANTS.statisticsKey, JSON.stringify(this.statistics));
        } catch (error) {
            console.error('Error saving statistics:', error);
        }
    }

    /**
     * Export statistics data
     * @returns {Object} Statistics data for export
     */
    exportStatistics() {
        return {
            statistics: this.statistics,
            calculated: this.getCalculatedStats(),
            exportDate: new Date().toISOString(),
            version: '1.0'
        };
    }

    /**
     * Import statistics data
     * @param {Object} data - Statistics data to import
     * @returns {boolean} Success status
     */
    importStatistics(data) {
        try {
            if (data.statistics && typeof data.statistics === 'object') {
                this.statistics = { ...this.statistics, ...data.statistics };
                this.saveStatistics();
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error importing statistics:', error);
            return false;
        }
    }

    /**
     * Get performance metrics
     * @returns {Object} Performance metrics
     */
    getPerformanceMetrics() {
        const stats = this.getCalculatedStats();
        
        return {
            efficiency: {
                avgResponseTime: stats.avgResponseTime,
                avgSourcesPerQuery: stats.avgSourcesPerQuery,
                hybridUsage: stats.hybridUsagePercent
            },
            usage: {
                totalQueries: stats.totalQuestions,
                totalSources: stats.totalSources,
                hybridQueries: stats.hybridSearches
            },
            trends: this.calculateTrends()
        };
    }

    /**
     * Calculate usage trends (placeholder for future implementation)
     * @returns {Object} Usage trends
     */
    calculateTrends() {
        // This could be expanded to track daily/weekly/monthly trends
        // For now, return basic trend indicators
        return {
            totalQuestionsGrowth: 0,
            avgResponseTimeChange: 0,
            hybridUsageChange: 0
        };
    }

    /**
     * Check if statistics indicate good performance
     * @returns {Object} Performance indicators
     */
    getPerformanceIndicators() {
        const stats = this.getCalculatedStats();
        
        return {
            responseTimeGood: stats.avgResponseTime < 3.0, // Less than 3 seconds is good
            sourcesUtilizationGood: stats.avgSourcesPerQuery >= 2, // At least 2 sources per query
            hybridUsageHealthy: stats.hybridUsagePercent >= 10, // At least 10% hybrid usage
            overallHealth: this.calculateOverallHealth(stats)
        };
    }

    /**
     * Calculate overall health score
     * @param {Object} stats - Calculated statistics
     * @returns {number} Health score (0-100)
     */
    calculateOverallHealth(stats) {
        let score = 100;
        
        // Penalize slow response times
        if (stats.avgResponseTime > 5) score -= 30;
        else if (stats.avgResponseTime > 3) score -= 15;
        
        // Penalize low source utilization
        if (stats.avgSourcesPerQuery < 1) score -= 25;
        else if (stats.avgSourcesPerQuery < 2) score -= 10;
        
        // Penalize very low hybrid usage (if available)
        if (stats.hybridUsagePercent < 5) score -= 15;
        
        return Math.max(0, score);
    }
}

// Export singleton instance
export const statsService = new StatsService();