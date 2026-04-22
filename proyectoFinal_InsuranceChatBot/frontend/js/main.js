/**
 * Main Application Entry Point
 * Initializes and bootstraps the modular Insurance Chatbot application
 */

// Import services
import { apiService } from './services/api-service.js';
import { chatService } from './services/chat-service.js';
import { documentService } from './services/document-service.js';
import { statsService } from './services/stats-service.js';

// Import components
import { chatComponent } from './components/chat-component.js';
import { documentComponent } from './components/document-component.js';
import { statsComponent } from './components/stats-component.js';
import { uiComponent } from './components/ui-component.js';
import { errorComponent } from './components/error-component.js';

// Import state management
import { appState } from './state/app-state.js';

// Import configuration
import { API_CONFIG } from './config/api-config.js';

/**
 * Main Application Class
 * Coordinates all components and manages application lifecycle
 */
class InsuranceChatbotApp {
    constructor() {
        this.isInitialized = false;
        this.components = new Map();
        this.services = new Map();
        this.healthCheckInterval = null;
    }

    /**
     * Initialize the application
     */
    async initialize() {
        try {
            console.log('🚀 Initializing Insurance Chatbot Application...');

            // Initialize services
            this.initializeServices();

            // Initialize components
            this.initializeComponents();

            // Setup global event listeners
            this.setupGlobalEventListeners();

            // Check server health
            await this.checkServerHealth();

            // Load initial data
            await this.loadInitialData();

            // Start real-time updates
            this.startRealTimeUpdates();

            this.isInitialized = true;
            console.log('✅ Application initialized successfully');

            // Trigger application ready event
            this.onApplicationReady();

        } catch (error) {
            console.error('❌ Failed to initialize application:', error);
            this.handleInitializationError(error);
        }
    }

    /**
     * Initialize services
     */
    initializeServices() {
        console.log('📡 Initializing services...');

        this.services.set('api', apiService);
        this.services.set('chat', chatService);
        this.services.set('document', documentService);
        this.services.set('stats', statsService);

        console.log('✅ Services initialized');
    }

    /**
     * Initialize components
     */
    initializeComponents() {
        console.log('🧩 Initializing components...');

        // Initialize UI component first as others may depend on it
        uiComponent.initialize();
        this.components.set('ui', uiComponent);

        // Initialize error component early for error handling
        this.components.set('error', errorComponent);

        // Initialize other components
        this.components.set('chat', chatComponent);
        this.components.set('document', documentComponent);
        this.components.set('stats', statsComponent);

        console.log('✅ Components initialized');
    }

    /**
     * Setup global event listeners
     */
    setupGlobalEventListeners() {
        // Application state changes
        appState.subscribe('*', (value, oldValue, key) => {
            console.debug(`State changed: ${key}`, { oldValue, newValue: value });
        });

        // Window beforeunload
        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));

        // Page visibility change
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));

        // Online/offline detection
        window.addEventListener('online', this.handleOnline.bind(this));
        window.addEventListener('offline', this.handleOffline.bind(this));
    }

    /**
     * Check server health and capabilities
     */
    async checkServerHealth() {
        try {
            console.log('🔍 Checking server health...');
            
            const health = await apiService.healthCheck();
            appState.setServerHealth(health);

            console.log('✅ Server health check completed:', health);

            // Update UI based on server capabilities
            if (health.hybrid_chatbot_ready) {
                console.log('🔥 Hybrid chatbot mode available');
            }

        } catch (error) {
            console.warn('⚠️ Server health check failed:', error.message);
            appState.setServerHealth(null);
            appState.addError(error);
        }
    }

    /**
     * Load initial data
     */
    async loadInitialData() {
        console.log('📊 Loading initial data...');

        try {
            // Load statistics in parallel
            const promises = [
                statsComponent.loadBackendStats(),
                // Could load other initial data here
            ];

            await Promise.allSettled(promises);
            console.log('✅ Initial data loaded');

        } catch (error) {
            console.warn('⚠️ Some initial data failed to load:', error);
        }
    }

    /**
     * Start real-time updates
     */
    startRealTimeUpdates() {
        // Health check every 5 minutes
        this.healthCheckInterval = setInterval(() => {
            this.checkServerHealth();
        }, 5 * 60 * 1000);

        // Start stats real-time updates
        statsComponent.startRealTimeUpdates();

        console.log('🔄 Real-time updates started');
    }

    /**
     * Stop real-time updates
     */
    stopRealTimeUpdates() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }

        statsComponent.stopRealTimeUpdates();

        console.log('⏹️ Real-time updates stopped');
    }

    /**
     * Handle application ready
     */
    onApplicationReady() {
        // Focus chat input
        chatComponent.focusInput();

        // Show welcome message if no chat history
        const chatHistory = appState.get('chatHistory');
        if (chatHistory.length === 0) {
            this.showWelcomeMessage();
        }

        // Trigger custom event
        window.dispatchEvent(new CustomEvent('chatbotReady', {
            detail: { app: this }
        }));
    }

    /**
     * Show welcome message
     */
    showWelcomeMessage() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages && !chatMessages.querySelector('.welcome-message')) {
            const welcomeDiv = document.createElement('div');
            welcomeDiv.className = 'welcome-message';
            welcomeDiv.innerHTML = `
                <div class="welcome-content">
                    <h2>👋 ¡Bienvenido al Chatbot de Seguros!</h2>
                    <p>Estoy aquí para ayudarte con todas tus preguntas sobre seguros. Puedes preguntarme sobre:</p>
                    <ul>
                        <li>🏠 Seguros de hogar y propiedad</li>
                        <li>🚗 Seguros de vehículos</li>
                        <li>❤️ Seguros de vida y salud</li>
                        <li>💼 Seguros comerciales</li>
                        <li>📄 Pólizas y coberturas</li>
                    </ul>
                    <p>¡Escribe tu pregunta para comenzar!</p>
                </div>
            `;
            chatMessages.appendChild(welcomeDiv);
        }
    }

    /**
     * Handle initialization error
     * @param {Error} error - Initialization error
     */
    handleInitializationError(error) {
        // Show error message to user
        const errorMessage = `
            <div class="initialization-error">
                <h2>❌ Error de Inicialización</h2>
                <p>Ha ocurrido un error al inicializar la aplicación:</p>
                <p><strong>${error.message}</strong></p>
                <button onclick="window.location.reload()" class="btn btn-primary">
                    🔄 Recargar Página
                </button>
            </div>
        `;

        document.body.innerHTML = errorMessage;
    }

    /**
     * Event handlers
     */
    handleBeforeUnload(event) {
        // Save any pending data
        console.log('💾 Saving application state before unload...');
        
        // The state is automatically saved due to our persistent storage setup
        // but we could do additional cleanup here if needed
    }

    handleVisibilityChange() {
        if (document.hidden) {
            console.log('📱 Application hidden');
            // Pause real-time updates to save resources
            this.stopRealTimeUpdates();
        } else {
            console.log('📱 Application visible');
            // Resume real-time updates
            this.startRealTimeUpdates();
            // Refresh data
            this.checkServerHealth();
        }
    }

    handleOnline() {
        console.log('🌐 Connection restored');
        uiComponent.showSuccess('Conexión restaurada');
        this.checkServerHealth();
    }

    handleOffline() {
        console.log('📴 Connection lost');
        uiComponent.showError('Sin conexión a internet. Algunas funciones pueden no estar disponibles.');
    }

    /**
     * Public API methods
     */

    /**
     * Get component instance
     * @param {string} name - Component name
     * @returns {Object} Component instance
     */
    getComponent(name) {
        return this.components.get(name);
    }

    /**
     * Get service instance
     * @param {string} name - Service name
     * @returns {Object} Service instance
     */
    getService(name) {
        return this.services.get(name);
    }

    /**
     * Restart application
     */
    async restart() {
        console.log('🔄 Restarting application...');
        
        await this.shutdown();
        await this.initialize();
    }

    /**
     * Shutdown application
     */
    async shutdown() {
        console.log('🛑 Shutting down application...');

        this.stopRealTimeUpdates();

        // Destroy components
        this.components.forEach((component, name) => {
            if (component.destroy) {
                component.destroy();
            }
            console.log(`🗑️ Destroyed ${name} component`);
        });

        this.components.clear();
        this.services.clear();
        this.isInitialized = false;

        console.log('✅ Application shutdown complete');
    }

    /**
     * Get application status
     * @returns {Object} Application status
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            components: Array.from(this.components.keys()),
            services: Array.from(this.services.keys()),
            serverHealth: appState.get('serverHealth'),
            errorCount: appState.get('errorHistory').length
        };
    }

    /**
     * Enable debug mode
     */
    enableDebugMode() {
        window.chatbotApp = this;
        window.appState = appState;
        window.components = this.components;
        window.services = this.services;
        
        console.log('🐛 Debug mode enabled. Global objects available:');
        console.log('- window.chatbotApp: Main application instance');
        console.log('- window.appState: Application state');
        console.log('- window.components: Component instances');
        console.log('- window.services: Service instances');
    }
}

/**
 * Initialize application when DOM is ready
 */
function initializeWhenReady() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeApplication);
    } else {
        initializeApplication();
    }
}

/**
 * Initialize the application
 */
async function initializeApplication() {
    // Create and initialize the application
    const app = new InsuranceChatbotApp();
    
    // Enable debug mode in development
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        app.enableDebugMode();
    }

    // Make app globally available
    window.insuranceChatbotApp = app;

    // Initialize the application
    await app.initialize();
}

// Start the application
initializeWhenReady();

// Export for module usage
export { InsuranceChatbotApp };
export default InsuranceChatbotApp;