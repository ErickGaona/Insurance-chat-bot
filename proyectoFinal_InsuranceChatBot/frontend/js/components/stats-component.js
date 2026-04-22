import { statsService } from '../services/stats-service.js';
import { appState } from '../state/app-state.js';
import { findElement } from '../utils/dom-utils.js';
import { formatNumber, formatPercentage } from '../utils/format-utils.js';
import { animateCounter } from '../utils/animation-utils.js';

/**
 * Statistics Component
 * Handles statistics display and real-time updates
 */
export class StatsComponent {
    constructor() {
        this.elements = {};
        this.isInitialized = false;
        this.lastStats = {};
        
        this.initializeElements();
        this.setupStateSubscriptions();
        this.loadInitialStats();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.elements = {
            totalQuestions: findElement('#totalQuestions'),
            totalSources: findElement('#totalSources'),
            avgResponseTime: findElement('#avgResponseTime'),
            docCount: findElement('#doc-count'),
            hybridIndicator: findElement('.hybrid-indicator'),
            statsContainer: findElement('.header-stats')
        };

        this.isInitialized = true;
    }

    /**
     * Setup state subscriptions
     */
    setupStateSubscriptions() {
        // Subscribe to statistics changes
        appState.subscribe('statistics', (statistics) => {
            this.updateStatisticsDisplay(statistics);
        });

        // Subscribe to server health changes
        appState.subscribe('serverHealth', (health) => {
            this.updateServerStats(health);
        });

        appState.subscribe('serverCapabilities', (capabilities) => {
            this.updateCapabilitiesDisplay(capabilities);
        });
    }

    /**
     * Load initial statistics
     */
    async loadInitialStats() {
        try {
            // Load local statistics
            const localStats = statsService.getCalculatedStats();
            this.updateStatisticsDisplay(localStats);

            // Load backend statistics
            await this.loadBackendStats();

        } catch (error) {
            console.warn('Error loading initial stats:', error);
        }
    }

    /**
     * Update statistics display
     * @param {Object} statistics - Statistics object
     */
    updateStatisticsDisplay(statistics) {
        if (!this.isInitialized) return;

        // Animate counter changes
        if (this.elements.totalQuestions) {
            const oldValue = this.lastStats.totalQuestions || 0;
            const newValue = statistics.totalQuestions || 0;
            
            if (oldValue !== newValue) {
                animateCounter(this.elements.totalQuestions, oldValue, newValue, 500, formatNumber);
            }
        }

        if (this.elements.totalSources) {
            const oldValue = this.lastStats.totalSources || 0;
            const newValue = statistics.totalSources || 0;
            
            if (oldValue !== newValue) {
                animateCounter(this.elements.totalSources, oldValue, newValue, 500, formatNumber);
            }
        }

        if (this.elements.avgResponseTime) {
            const avgTime = statistics.avgResponseTime || 0;
            this.elements.avgResponseTime.textContent = `${avgTime}s`;
            
            // Add performance indicator classes
            this.elements.avgResponseTime.className = 'stat-value';
            if (avgTime < 2) {
                this.elements.avgResponseTime.classList.add('performance-good');
            } else if (avgTime < 5) {
                this.elements.avgResponseTime.classList.add('performance-ok');
            } else {
                this.elements.avgResponseTime.classList.add('performance-poor');
            }
        }

        // Store current stats for next comparison
        this.lastStats = { ...statistics };
    }

    /**
     * Load backend statistics
     */
    async loadBackendStats() {
        try {
            const backendStats = await statsService.loadBackendStats();
            
            if (backendStats && this.elements.docCount) {
                const docCount = backendStats.totalDocuments || 0;
                this.elements.docCount.textContent = `${formatNumber(docCount)} Documentos`;
            }

            return backendStats;
        } catch (error) {
            console.warn('Could not load backend stats:', error);
            return null;
        }
    }

    /**
     * Update server statistics
     * @param {Object} health - Server health object
     */
    updateServerStats(health) {
        if (!health) return;

        // Update hybrid mode indicator
        if (health.hybrid_chatbot_ready) {
            this.showHybridModeIndicator();
        }

        // Update other server-specific stats if available
        if (health.stats) {
            // Handle additional server statistics
            console.log('Server stats:', health.stats);
        }
    }

    /**
     * Update capabilities display
     * @param {Object} capabilities - Server capabilities
     */
    updateCapabilitiesDisplay(capabilities) {
        if (capabilities.hybridMode) {
            this.showHybridModeIndicator();
        } else {
            this.hideHybridModeIndicator();
        }
    }

    /**
     * Show hybrid mode indicator
     */
    showHybridModeIndicator() {
        if (this.elements.statsContainer && !this.elements.hybridIndicator) {
            const hybridDiv = document.createElement('div');
            hybridDiv.className = 'stat-item hybrid-indicator';
            hybridDiv.innerHTML = `
                <i class="fas fa-magic"></i>
                <span class="stat-label">Búsqueda Híbrida</span>
                <span class="stat-value active">Activo</span>
            `;
            
            this.elements.statsContainer.appendChild(hybridDiv);
            this.elements.hybridIndicator = hybridDiv;
        }
    }

    /**
     * Hide hybrid mode indicator
     */
    hideHybridModeIndicator() {
        if (this.elements.hybridIndicator) {
            this.elements.hybridIndicator.remove();
            this.elements.hybridIndicator = null;
        }
    }

    /**
     * Update statistics with new data
     * @param {number} sources - Number of sources
     * @param {number} responseTime - Response time in milliseconds
     * @param {number} webSources - Web sources count
     * @param {boolean} usedWebSearch - Whether web search was used
     */
    updateStats(sources, responseTime, webSources, usedWebSearch) {
        const updatedStats = statsService.updateStats(sources, responseTime, webSources, usedWebSearch);
        appState.updateStatistics(updatedStats);
        
        // Show achievement notifications for milestones
        this.checkMilestones(updatedStats);
    }

    /**
     * Check for achievement milestones
     * @param {Object} stats - Current statistics
     */
    checkMilestones(stats) {
        const milestones = [10, 25, 50, 100, 250, 500, 1000];
        
        milestones.forEach(milestone => {
            if (stats.totalQuestions === milestone) {
                this.showMilestoneNotification(milestone);
            }
        });
    }

    /**
     * Show milestone notification
     * @param {number} milestone - Milestone number
     */
    showMilestoneNotification(milestone) {
        // This could trigger a toast notification
        console.log(`🎉 ¡Milestone alcanzado! ${milestone} preguntas respondidas`);
    }

    /**
     * Get comprehensive statistics
     * @returns {Promise<Object>} Comprehensive statistics
     */
    async getComprehensiveStats() {
        return await statsService.getComprehensiveStats();
    }

    /**
     * Export statistics
     * @returns {Object} Exported statistics
     */
    exportStats() {
        return statsService.exportStatistics();
    }

    /**
     * Reset statistics
     */
    resetStats() {
        if (confirm('¿Está seguro de que desea restablecer todas las estadísticas?')) {
            statsService.resetStatistics();
            appState.updateStatistics(statsService.getCalculatedStats());
        }
    }

    /**
     * Get performance metrics
     * @returns {Object} Performance metrics
     */
    getPerformanceMetrics() {
        return statsService.getPerformanceMetrics();
    }

    /**
     * Get performance health indicators
     * @returns {Object} Performance indicators
     */
    getPerformanceHealth() {
        return statsService.getPerformanceIndicators();
    }

    /**
     * Create detailed stats view
     * @returns {string} HTML for detailed stats
     */
    createDetailedStatsView() {
        const stats = statsService.getCalculatedStats();
        const performance = this.getPerformanceHealth();
        
        return `
            <div class="detailed-stats">
                <h3>Estadísticas Detalladas</h3>
                
                <div class="stats-section">
                    <h4>Uso General</h4>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <span class="stat-label">Total de Preguntas</span>
                            <span class="stat-value">${formatNumber(stats.totalQuestions)}</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-label">Fuentes Consultadas</span>
                            <span class="stat-value">${formatNumber(stats.totalSources)}</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-label">Búsquedas Híbridas</span>
                            <span class="stat-value">${formatNumber(stats.hybridSearches)}</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-label">Fuentes Web</span>
                            <span class="stat-value">${formatNumber(stats.totalWebSources)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="stats-section">
                    <h4>Rendimiento</h4>
                    <div class="stats-grid">
                        <div class="stat-card ${performance.responseTimeGood ? 'good' : 'poor'}">
                            <span class="stat-label">Tiempo de Respuesta Promedio</span>
                            <span class="stat-value">${stats.avgResponseTime}s</span>
                        </div>
                        <div class="stat-card ${performance.sourcesUtilizationGood ? 'good' : 'poor'}">
                            <span class="stat-label">Fuentes por Consulta</span>
                            <span class="stat-value">${stats.avgSourcesPerQuery}</span>
                        </div>
                        <div class="stat-card ${performance.hybridUsageHealthy ? 'good' : 'warning'}">
                            <span class="stat-label">Uso de Búsqueda Híbrida</span>
                            <span class="stat-value">${stats.hybridUsagePercent}%</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-label">Salud General</span>
                            <span class="stat-value">${performance.overallHealth}%</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Refresh all statistics
     */
    async refresh() {
        await this.loadInitialStats();
        await this.loadBackendStats();
    }

    /**
     * Start real-time updates
     * @param {number} interval - Update interval in milliseconds
     */
    startRealTimeUpdates(interval = 30000) {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        this.updateInterval = setInterval(() => {
            this.loadBackendStats();
        }, interval);
    }

    /**
     * Stop real-time updates
     */
    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    /**
     * Destroy component and cleanup
     */
    destroy() {
        this.stopRealTimeUpdates();
        this.elements = {};
        this.isInitialized = false;
    }
}

// Export singleton instance
export const statsComponent = new StatsComponent();