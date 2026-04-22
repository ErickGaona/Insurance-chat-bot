import { appState } from '../state/app-state.js';
import { findElement, createElement } from '../utils/dom-utils.js';
import { fadeIn, fadeOut, shakeElement } from '../utils/animation-utils.js';
import { formatRelativeTime } from '../utils/format-utils.js';

/**
 * Error Component
 * Handles error display, error history, and user-friendly error formatting
 */
export class ErrorComponent {
    constructor() {
        this.elements = {};
        this.isInitialized = false;
        this.activeErrors = new Map();
        
        this.initializeElements();
        this.setupStateSubscriptions();
        this.setupGlobalErrorHandling();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.elements = {
            errorToast: findElement('#errorToast'),
            errorMessage: findElement('#errorMessage'),
            errorContainer: findElement('.error-container'),
            errorHistory: findElement('#errorHistory')
        };

        // Create error container if it doesn't exist
        if (!this.elements.errorContainer) {
            this.elements.errorContainer = this.createErrorContainer();
        }

        this.isInitialized = true;
    }

    /**
     * Setup state subscriptions
     */
    setupStateSubscriptions() {
        // Subscribe to error state changes
        appState.subscribe('lastError', (error) => {
            if (error) {
                this.showError(error);
            }
        });

        appState.subscribe('errorHistory', (errorHistory) => {
            this.updateErrorHistoryDisplay(errorHistory);
        });
    }

    /**
     * Setup global error handling
     */
    setupGlobalErrorHandling() {
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.handleError(event.reason, 'Unhandled Promise Rejection');
        });

        // Handle JavaScript errors
        window.addEventListener('error', (event) => {
            console.error('JavaScript error:', event.error);
            this.handleError(event.error, 'JavaScript Error');
        });

        // Handle fetch errors globally
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch(...args);
                if (!response.ok && response.status >= 500) {
                    this.handleError(
                        new Error(`Server error: ${response.status} ${response.statusText}`),
                        'Server Error'
                    );
                }
                return response;
            } catch (error) {
                this.handleError(error, 'Network Error');
                throw error;
            }
        };
    }

    /**
     * Create error container
     * @returns {HTMLElement} Error container element
     */
    createErrorContainer() {
        const container = createElement('div', 
            { className: 'error-container' },
            ''
        );
        document.body.appendChild(container);
        return container;
    }

    /**
     * Handle error
     * @param {Error|string} error - Error to handle
     * @param {string} context - Error context
     */
    handleError(error, context = 'General Error') {
        const errorObj = {
            message: typeof error === 'string' ? error : error.message,
            stack: error.stack || null,
            context,
            timestamp: new Date().toISOString(),
            id: Date.now() + Math.random()
        };

        // Add to app state
        appState.addError(errorObj);

        // Log to console for debugging
        console.error(`[${context}]`, error);
    }

    /**
     * Show error
     * @param {Object} error - Error object
     */
    showError(error) {
        const userFriendlyMessage = this.getUserFriendlyMessage(error.message);
        
        // Show toast notification
        this.showErrorToast(userFriendlyMessage, error);

        // Update error display if element exists
        if (this.elements.errorMessage) {
            this.elements.errorMessage.textContent = userFriendlyMessage;
        }

        if (this.elements.errorToast) {
            this.elements.errorToast.classList.add('show');
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                this.hideError();
            }, 5000);
        }
    }

    /**
     * Show error toast
     * @param {string} message - Error message
     * @param {Object} errorObj - Full error object
     */
    showErrorToast(message, errorObj) {
        const toastId = `error-${errorObj.id}`;
        
        // Check if this error is already shown
        if (this.activeErrors.has(toastId)) {
            return;
        }

        const errorToast = createElement('div',
            { 
                className: 'error-toast',
                id: toastId
            },
            `
                <div class="error-toast-content">
                    <div class="error-icon">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                    <div class="error-details">
                        <div class="error-message">${message}</div>
                        <div class="error-context">${errorObj.context || ''}</div>
                        <div class="error-time">${formatRelativeTime(errorObj.timestamp)}</div>
                    </div>
                    <div class="error-actions">
                        <button class="error-retry" onclick="errorComponent.retryLastAction()" title="Reintentar">
                            <i class="fas fa-redo"></i>
                        </button>
                        <button class="error-details-btn" onclick="errorComponent.showErrorDetails('${toastId}')" title="Ver detalles">
                            <i class="fas fa-info-circle"></i>
                        </button>
                        <button class="error-close" onclick="errorComponent.closeErrorToast('${toastId}')" title="Cerrar">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `
        );

        this.elements.errorContainer.appendChild(errorToast);
        this.activeErrors.set(toastId, errorObj);

        // Animate in
        fadeIn(errorToast, 200);

        // Shake animation for critical errors
        if (this.isCriticalError(errorObj)) {
            shakeElement(errorToast);
        }

        // Auto-remove after 10 seconds for non-critical errors
        if (!this.isCriticalError(errorObj)) {
            setTimeout(() => {
                this.closeErrorToast(toastId);
            }, 10000);
        }
    }

    /**
     * Close error toast
     * @param {string} toastId - Toast ID
     */
    closeErrorToast(toastId) {
        const toastElement = findElement(`#${toastId}`);
        if (toastElement) {
            fadeOut(toastElement, 200).then(() => {
                if (toastElement.parentNode) {
                    toastElement.parentNode.removeChild(toastElement);
                }
                this.activeErrors.delete(toastId);
            });
        }
    }

    /**
     * Hide main error display
     */
    hideError() {
        if (this.elements.errorToast) {
            this.elements.errorToast.classList.remove('show');
        }
    }

    /**
     * Show error details modal
     * @param {string} toastId - Toast ID
     */
    showErrorDetails(toastId) {
        const errorObj = this.activeErrors.get(toastId);
        if (!errorObj) return;

        const modal = this.createErrorDetailsModal(errorObj);
        document.body.appendChild(modal);
        fadeIn(modal, 200);
    }

    /**
     * Create error details modal
     * @param {Object} errorObj - Error object
     * @returns {HTMLElement} Modal element
     */
    createErrorDetailsModal(errorObj) {
        const modal = createElement('div',
            { className: 'modal-overlay error-details-modal' },
            `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Detalles del Error</h3>
                        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="error-detail-section">
                            <h4>Mensaje</h4>
                            <p>${errorObj.message}</p>
                        </div>
                        <div class="error-detail-section">
                            <h4>Contexto</h4>
                            <p>${errorObj.context || 'No disponible'}</p>
                        </div>
                        <div class="error-detail-section">
                            <h4>Tiempo</h4>
                            <p>${formatRelativeTime(errorObj.timestamp)} (${new Date(errorObj.timestamp).toLocaleString()})</p>
                        </div>
                        ${errorObj.stack ? `
                            <div class="error-detail-section">
                                <h4>Stack Trace</h4>
                                <pre class="error-stack">${errorObj.stack}</pre>
                            </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="errorComponent.copyErrorDetails('${errorObj.id}')">
                            <i class="fas fa-copy"></i> Copiar Detalles
                        </button>
                        <button class="btn btn-primary" onclick="errorComponent.reportError('${errorObj.id}')">
                            <i class="fas fa-bug"></i> Reportar Error
                        </button>
                    </div>
                </div>
            `
        );

        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        return modal;
    }

    /**
     * Update error history display
     * @param {Array} errorHistory - Error history array
     */
    updateErrorHistoryDisplay(errorHistory) {
        if (!this.elements.errorHistory) return;

        if (errorHistory.length === 0) {
            this.elements.errorHistory.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-check-circle"></i>
                    <p>No hay errores recientes</p>
                </div>
            `;
            return;
        }

        const historyHtml = errorHistory.map(error => `
            <div class="error-history-item">
                <div class="error-icon ${this.getErrorSeverityClass(error)}">
                    <i class="fas ${this.getErrorIcon(error)}"></i>
                </div>
                <div class="error-content">
                    <div class="error-message">${this.getUserFriendlyMessage(error.message)}</div>
                    <div class="error-meta">
                        <span class="error-context">${error.context || 'General'}</span>
                        <span class="error-time">${formatRelativeTime(error.timestamp)}</span>
                    </div>
                </div>
                <div class="error-actions">
                    <button onclick="errorComponent.showErrorDetails('${error.id}')" title="Ver detalles">
                        <i class="fas fa-info-circle"></i>
                    </button>
                </div>
            </div>
        `).join('');

        this.elements.errorHistory.innerHTML = historyHtml;
    }

    /**
     * Get user-friendly error message
     * @param {string} message - Original error message
     * @returns {string} User-friendly message
     */
    getUserFriendlyMessage(message) {
        const errorMappings = {
            'Network error': 'Error de conexión. Por favor, verifica tu conexión a internet.',
            'Request timeout': 'La solicitud tardó demasiado. Por favor, inténtalo de nuevo.',
            'Server error': 'Error del servidor. Por favor, inténtalo más tarde.',
            'HTTP error! status: 500': 'Error interno del servidor. Por favor, inténtalo más tarde.',
            'HTTP error! status: 404': 'Recurso no encontrado. Por favor, verifica la URL.',
            'HTTP error! status: 403': 'Acceso denegado. No tienes permisos para realizar esta acción.',
            'HTTP error! status: 401': 'No autorizado. Por favor, verifica tus credenciales.',
            'Failed to fetch': 'Error de conexión. Por favor, verifica tu conexión a internet.'
        };

        // Check for exact matches
        if (errorMappings[message]) {
            return errorMappings[message];
        }

        // Check for partial matches
        for (const [key, value] of Object.entries(errorMappings)) {
            if (message.toLowerCase().includes(key.toLowerCase())) {
                return value;
            }
        }

        // Default fallback
        return message || 'Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo.';
    }

    /**
     * Check if error is critical
     * @param {Object} errorObj - Error object
     * @returns {boolean} Whether error is critical
     */
    isCriticalError(errorObj) {
        const criticalKeywords = [
            'server error',
            'internal error',
            'database error',
            'authentication error',
            'permission denied'
        ];

        return criticalKeywords.some(keyword => 
            errorObj.message.toLowerCase().includes(keyword)
        );
    }

    /**
     * Get error severity class
     * @param {Object} errorObj - Error object
     * @returns {string} CSS class for severity
     */
    getErrorSeverityClass(errorObj) {
        if (this.isCriticalError(errorObj)) {
            return 'error-critical';
        }
        
        if (errorObj.context?.includes('Network')) {
            return 'error-warning';
        }
        
        return 'error-normal';
    }

    /**
     * Get error icon
     * @param {Object} errorObj - Error object
     * @returns {string} Font Awesome icon class
     */
    getErrorIcon(errorObj) {
        if (this.isCriticalError(errorObj)) {
            return 'fa-exclamation-triangle';
        }
        
        if (errorObj.context?.includes('Network')) {
            return 'fa-wifi';
        }
        
        return 'fa-exclamation-circle';
    }

    /**
     * Retry last action
     */
    retryLastAction() {
        // This would depend on the application's architecture
        // For now, just refresh the page or clear the current error
        const lastError = appState.get('lastError');
        if (lastError) {
            appState.clearError();
            // Could trigger a retry mechanism here
            console.log('Retrying last action...');
        }
    }

    /**
     * Copy error details to clipboard
     * @param {string} errorId - Error ID
     */
    async copyErrorDetails(errorId) {
        const errorObj = this.activeErrors.get(`error-${errorId}`) || 
                       appState.get('errorHistory').find(e => e.id === errorId);
        
        if (!errorObj) return;

        const details = `
Error Details:
Message: ${errorObj.message}
Context: ${errorObj.context || 'N/A'}
Time: ${new Date(errorObj.timestamp).toLocaleString()}
${errorObj.stack ? `Stack: ${errorObj.stack}` : ''}
        `.trim();

        try {
            await navigator.clipboard.writeText(details);
            this.showSuccessToast('Detalles del error copiados al portapapeles');
        } catch (error) {
            console.error('Failed to copy error details:', error);
        }
    }

    /**
     * Report error
     * @param {string} errorId - Error ID
     */
    reportError(errorId) {
        // This would integrate with an error reporting service
        console.log(`Reporting error ${errorId}...`);
        this.showSuccessToast('Error reportado. Gracias por tu ayuda.');
    }

    /**
     * Show success toast
     * @param {string} message - Success message
     */
    showSuccessToast(message) {
        // This could use the UI component's toast functionality
        console.log('Success:', message);
    }

    /**
     * Clear all errors
     */
    clearAllErrors() {
        // Clear active error toasts
        this.activeErrors.forEach((_, toastId) => {
            this.closeErrorToast(toastId);
        });

        // Clear error state
        appState.clearAllErrors();
    }

    /**
     * Get error statistics
     * @returns {Object} Error statistics
     */
    getErrorStatistics() {
        const errorHistory = appState.get('errorHistory');
        const now = new Date();
        const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        
        const recentErrors = errorHistory.filter(error => 
            new Date(error.timestamp) > dayAgo
        );

        return {
            total: errorHistory.length,
            recentCount: recentErrors.length,
            criticalCount: errorHistory.filter(this.isCriticalError).length,
            mostCommonError: this.getMostCommonError(errorHistory)
        };
    }

    /**
     * Get most common error
     * @param {Array} errorHistory - Error history
     * @returns {string} Most common error message
     */
    getMostCommonError(errorHistory) {
        const errorCounts = {};
        
        errorHistory.forEach(error => {
            const key = error.message;
            errorCounts[key] = (errorCounts[key] || 0) + 1;
        });

        let mostCommon = '';
        let maxCount = 0;
        
        Object.entries(errorCounts).forEach(([message, count]) => {
            if (count > maxCount) {
                maxCount = count;
                mostCommon = message;
            }
        });

        return mostCommon;
    }

    /**
     * Destroy component and cleanup
     */
    destroy() {
        // Clear all active errors
        this.clearAllErrors();

        // Remove global error handlers
        window.removeEventListener('unhandledrejection', this.handleError);
        window.removeEventListener('error', this.handleError);

        this.elements = {};
        this.isInitialized = false;
    }
}

// Export singleton instance
export const errorComponent = new ErrorComponent();