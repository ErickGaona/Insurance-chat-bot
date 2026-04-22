import { appState } from '../state/app-state.js';
import { findElement, toggleVisibility } from '../utils/dom-utils.js';
import { fadeIn, fadeOut } from '../utils/animation-utils.js';
import { APP_CONSTANTS } from '../config/api-config.js';

/**
 * UI Component
 * Handles general UI management, loading states, modals, and layout
 */
export class UIComponent {
    constructor() {
        this.elements = {};
        this.isInitialized = false;
        this.activeModals = new Set();
        
        this.initializeElements();
        this.setupEventListeners();
        this.setupStateSubscriptions();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.elements = {
            // Loading elements
            loadingOverlay: findElement('#loadingOverlay'),
            
            // Layout elements
            sidebar: findElement('.sidebar'),
            sidebarToggle: findElement('.sidebar-toggle'),
            mainContent: findElement('.main-content'),
            
            // Modal elements
            modalOverlays: document.querySelectorAll('.modal-overlay'),
            
            // Navigation elements
            navItems: document.querySelectorAll('.nav-item'),
            
            // Theme elements
            themeToggle: findElement('.theme-toggle')
        };

        this.isInitialized = true;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        if (!this.isInitialized) return;

        // Sidebar toggle
        if (this.elements.sidebarToggle) {
            this.elements.sidebarToggle.addEventListener('click', this.toggleSidebar.bind(this));
        }

        // Navigation items
        this.elements.navItems.forEach(item => {
            item.addEventListener('click', this.handleNavigation.bind(this));
        });

        // Theme toggle
        if (this.elements.themeToggle) {
            this.elements.themeToggle.addEventListener('click', this.toggleTheme.bind(this));
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));

        // Window resize
        window.addEventListener('resize', this.handleResize.bind(this));

        // Modal close on outside click
        this.elements.modalOverlays.forEach(overlay => {
            overlay.addEventListener('click', this.handleModalOverlayClick.bind(this));
        });
    }

    /**
     * Setup state subscriptions
     */
    setupStateSubscriptions() {
        // Subscribe to loading state
        appState.subscribe('isLoading', (isLoading) => {
            this.setLoadingState(isLoading);
        });

        // Subscribe to current view
        appState.subscribe('currentView', (view) => {
            this.setActiveView(view);
        });

        // Subscribe to sidebar state
        appState.subscribe('sidebarOpen', (isOpen) => {
            this.setSidebarState(isOpen);
        });

        // Subscribe to errors
        appState.subscribe('lastError', (error) => {
            if (error) {
                this.showError(error.message);
            }
        });
    }

    /**
     * Set loading state
     * @param {boolean} isLoading - Loading state
     */
    setLoadingState(isLoading) {
        if (this.elements.loadingOverlay) {
            toggleVisibility(this.elements.loadingOverlay, isLoading, 'show');
        }

        // Disable/enable interactive elements
        this.setInteractiveElementsState(!isLoading);
    }

    /**
     * Enable/disable interactive elements
     * @param {boolean} enabled - Whether elements should be enabled
     */
    setInteractiveElementsState(enabled) {
        const selectors = [
            'button:not(.loading-exempt)',
            'input:not(.loading-exempt)',
            'textarea:not(.loading-exempt)',
            'select:not(.loading-exempt)'
        ];

        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(element => {
                element.disabled = !enabled;
            });
        });
    }

    /**
     * Toggle sidebar
     */
    toggleSidebar() {
        const isOpen = !appState.get('sidebarOpen');
        appState.setSidebarOpen(isOpen);
    }

    /**
     * Set sidebar state
     * @param {boolean} isOpen - Whether sidebar should be open
     */
    setSidebarState(isOpen) {
        if (this.elements.sidebar) {
            toggleVisibility(this.elements.sidebar, isOpen, 'open');
        }

        // Update main content margin on desktop
        if (this.elements.mainContent && window.innerWidth > 768) {
            this.elements.mainContent.style.marginLeft = isOpen ? '300px' : '0';
        }

        // Update toggle button state
        if (this.elements.sidebarToggle) {
            this.elements.sidebarToggle.classList.toggle('active', isOpen);
        }
    }

    /**
     * Handle navigation
     * @param {Event} event - Click event
     */
    handleNavigation(event) {
        const navItem = event.currentTarget;
        const view = navItem.dataset.view;

        if (view) {
            this.setActiveNavItem(navItem);
            appState.setCurrentView(view);
        }
    }

    /**
     * Set active navigation item
     * @param {HTMLElement} activeItem - Active navigation item
     */
    setActiveNavItem(activeItem) {
        // Remove active class from all nav items
        this.elements.navItems.forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to selected item
        activeItem.classList.add('active');
    }

    /**
     * Set active view
     * @param {string} view - View name
     */
    setActiveView(view) {
        // Hide all view containers
        const viewContainers = document.querySelectorAll('.view-container');
        viewContainers.forEach(container => {
            container.style.display = 'none';
        });

        // Show active view container
        const activeContainer = findElement(`#${view}View, .${view}-view, [data-view="${view}"]`);
        if (activeContainer) {
            activeContainer.style.display = 'block';
            fadeIn(activeContainer, 200);
        }

        // Update navigation
        const navItem = findElement(`[data-view="${view}"]`);
        if (navItem) {
            this.setActiveNavItem(navItem);
        }
    }

    /**
     * Toggle theme
     */
    toggleTheme() {
        const currentTheme = document.body.dataset.theme || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.body.dataset.theme = newTheme;
        localStorage.setItem('theme', newTheme);

        // Update theme toggle icon
        if (this.elements.themeToggle) {
            const icon = this.elements.themeToggle.querySelector('i');
            if (icon) {
                icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
    }

    /**
     * Handle keyboard shortcuts
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + K: Focus search
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            const searchInput = findElement('#chatInput, .search-input');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape: Close modals
        if (event.key === 'Escape') {
            this.closeAllModals();
        }

        // Ctrl/Cmd + /: Toggle sidebar
        if ((event.ctrlKey || event.metaKey) && event.key === '/') {
            event.preventDefault();
            this.toggleSidebar();
        }
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Close sidebar on mobile when resizing to larger screen
        if (window.innerWidth <= 768 && appState.get('sidebarOpen')) {
            appState.setSidebarOpen(false);
        }

        // Update layout
        this.updateLayout();
    }

    /**
     * Update layout based on screen size
     */
    updateLayout() {
        const isMobile = window.innerWidth <= 768;
        
        // Update sidebar behavior
        if (this.elements.sidebar) {
            if (isMobile) {
                this.elements.sidebar.classList.add('mobile');
            } else {
                this.elements.sidebar.classList.remove('mobile');
            }
        }

        // Update main content margin
        if (this.elements.mainContent && !isMobile) {
            const sidebarOpen = appState.get('sidebarOpen');
            this.elements.mainContent.style.marginLeft = sidebarOpen ? '300px' : '0';
        } else if (this.elements.mainContent) {
            this.elements.mainContent.style.marginLeft = '0';
        }
    }

    /**
     * Handle modal overlay clicks
     * @param {Event} event - Click event
     */
    handleModalOverlayClick(event) {
        if (event.target === event.currentTarget) {
            this.closeModal(event.currentTarget);
        }
    }

    /**
     * Show modal
     * @param {string|HTMLElement} modal - Modal selector or element
     */
    showModal(modal) {
        const modalElement = typeof modal === 'string' ? findElement(modal) : modal;
        if (!modalElement) return;

        modalElement.style.display = 'block';
        this.activeModals.add(modalElement);
        
        // Add modal-open class to body
        document.body.classList.add('modal-open');

        // Focus first focusable element
        const focusableElement = modalElement.querySelector('input, textarea, button, select, [tabindex]:not([tabindex="-1"])');
        if (focusableElement) {
            setTimeout(() => focusableElement.focus(), 100);
        }

        fadeIn(modalElement, 200);
    }

    /**
     * Close modal
     * @param {string|HTMLElement} modal - Modal selector or element
     */
    closeModal(modal) {
        const modalElement = typeof modal === 'string' ? findElement(modal) : modal;
        if (!modalElement) return;

        fadeOut(modalElement, 200).then(() => {
            modalElement.style.display = 'none';
            this.activeModals.delete(modalElement);

            // Remove modal-open class if no modals are active
            if (this.activeModals.size === 0) {
                document.body.classList.remove('modal-open');
            }
        });
    }

    /**
     * Close all modals
     */
    closeAllModals() {
        this.activeModals.forEach(modal => {
            this.closeModal(modal);
        });
    }

    /**
     * Show error toast
     * @param {string} message - Error message
     */
    showError(message) {
        this.showToast(message, 'error', APP_CONSTANTS.errorToastDuration);
    }

    /**
     * Show success toast
     * @param {string} message - Success message
     */
    showSuccess(message) {
        this.showToast(message, 'success', 3000);
    }

    /**
     * Show info toast
     * @param {string} message - Info message
     */
    showInfo(message) {
        this.showToast(message, 'info', 3000);
    }

    /**
     * Show toast notification
     * @param {string} message - Toast message
     * @param {string} type - Toast type (error, success, info, warning)
     * @param {number} duration - Display duration in milliseconds
     */
    showToast(message, type = 'info', duration = 3000) {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas ${this.getToastIcon(type)}"></i>
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add to container or body
        let toastContainer = findElement('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }

        toastContainer.appendChild(toast);

        // Animate in
        fadeIn(toast, 200);

        // Auto-remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                fadeOut(toast, 200).then(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                });
            }
        }, duration);
    }

    /**
     * Get icon for toast type
     * @param {string} type - Toast type
     * @returns {string} Font Awesome icon class
     */
    getToastIcon(type) {
        const icons = {
            error: 'fa-exclamation-circle',
            success: 'fa-check-circle',
            info: 'fa-info-circle',
            warning: 'fa-exclamation-triangle'
        };
        return icons[type] || icons.info;
    }

    /**
     * Initialize theme from localStorage
     */
    initializeTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.dataset.theme = savedTheme;

        if (this.elements.themeToggle) {
            const icon = this.elements.themeToggle.querySelector('i');
            if (icon) {
                icon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
    }

    /**
     * Show loading in specific container
     * @param {string|HTMLElement} container - Container selector or element
     * @param {string} message - Loading message
     */
    showLoadingInContainer(container, message = 'Cargando...') {
        const containerElement = typeof container === 'string' ? findElement(container) : container;
        if (!containerElement) return;

        containerElement.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner">
                    <div class="spinner"></div>
                </div>
                <div class="loading-message">${message}</div>
            </div>
        `;
    }

    /**
     * Set full screen mode
     * @param {boolean} fullscreen - Whether to enable fullscreen
     */
    setFullScreen(fullscreen) {
        if (fullscreen) {
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }

    /**
     * Initialize UI
     */
    initialize() {
        this.initializeTheme();
        this.updateLayout();
        
        // Set initial view
        appState.setCurrentView('chat');
    }

    /**
     * Destroy component and cleanup
     */
    destroy() {
        // Remove event listeners
        window.removeEventListener('resize', this.handleResize);
        document.removeEventListener('keydown', this.handleKeyboardShortcuts);

        // Close all modals
        this.closeAllModals();

        // Reset state
        this.elements = {};
        this.isInitialized = false;
    }
}

// Export singleton instance
export const uiComponent = new UIComponent();