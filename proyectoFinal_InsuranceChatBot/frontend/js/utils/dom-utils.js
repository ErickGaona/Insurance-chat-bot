import { APP_CONSTANTS } from '../config/api-config.js';

/**
 * DOM Utilities
 * Helper functions for DOM manipulation and element creation
 */

/**
 * Create an element with attributes and content
 * @param {string} tag - HTML tag name
 * @param {Object} attributes - Element attributes
 * @param {string} content - Element content
 * @returns {HTMLElement} Created element
 */
export function createElement(tag, attributes = {}, content = '') {
    const element = document.createElement(tag);
    
    Object.keys(attributes).forEach(key => {
        if (key === 'className') {
            element.className = attributes[key];
        } else {
            element.setAttribute(key, attributes[key]);
        }
    });
    
    if (content) {
        element.innerHTML = content;
    }
    
    return element;
}

/**
 * Find element by selector with error handling
 * @param {string} selector - CSS selector
 * @param {HTMLElement} context - Context element (default: document)
 * @returns {HTMLElement|null} Found element
 */
export function findElement(selector, context = document) {
    try {
        return context.querySelector(selector);
    } catch (error) {
        console.warn(`Element not found: ${selector}`, error);
        return null;
    }
}

/**
 * Find all elements by selector with error handling
 * @param {string} selector - CSS selector
 * @param {HTMLElement} context - Context element (default: document)
 * @returns {NodeList} Found elements
 */
export function findElements(selector, context = document) {
    try {
        return context.querySelectorAll(selector);
    } catch (error) {
        console.warn(`Elements not found: ${selector}`, error);
        return [];
    }
}

/**
 * Auto-resize textarea to fit content
 * @param {HTMLTextAreaElement} textarea - Textarea element
 * @param {number} maxHeight - Maximum height in pixels
 */
export function autoResizeTextarea(textarea, maxHeight = APP_CONSTANTS.autoResizeMaxHeight) {
    if (!textarea) return;
    
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, maxHeight) + 'px';
}

/**
 * Scroll element to bottom smoothly
 * @param {HTMLElement} element - Element to scroll
 * @param {boolean} smooth - Use smooth scrolling
 */
export function scrollToBottom(element, smooth = true) {
    if (!element) return;
    
    if (smooth) {
        element.scrollTo({
            top: element.scrollHeight,
            behavior: 'smooth'
        });
    } else {
        element.scrollTop = element.scrollHeight;
    }
}

/**
 * Add fade-in animation to element
 * @param {HTMLElement} element - Element to animate
 * @param {number} delay - Animation delay in milliseconds
 */
export function addFadeInAnimation(element, delay = 10) {
    if (!element) return;
    
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = 'all 0.4s ease-out';
    
    setTimeout(() => {
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, delay);
}

/**
 * Remove element with fade-out animation
 * @param {HTMLElement} element - Element to remove
 * @param {number} duration - Animation duration in milliseconds
 */
export function removeWithFadeOut(element, duration = 300) {
    if (!element) return;
    
    element.style.animation = `fadeOut ${duration}ms ease-out forwards`;
    
    setTimeout(() => {
        if (element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }, duration);
}

/**
 * Toggle element visibility with animation
 * @param {HTMLElement} element - Element to toggle
 * @param {boolean} show - Whether to show or hide
 * @param {string} className - CSS class to toggle
 */
export function toggleVisibility(element, show, className = 'show') {
    if (!element) return;
    
    if (show) {
        element.classList.add(className);
    } else {
        element.classList.remove(className);
    }
}

/**
 * Create loading spinner element
 * @param {string} text - Loading text
 * @returns {HTMLElement} Loading element
 */
export function createLoadingElement(text = 'Cargando...') {
    return createElement('div', 
        { className: 'loading-spinner' },
        `
            <div class="spinner"></div>
            <span class="loading-text">${text}</span>
        `
    );
}

/**
 * Create empty state element
 * @param {string} icon - Font Awesome icon class
 * @param {string} title - Empty state title
 * @param {string} message - Empty state message
 * @returns {HTMLElement} Empty state element
 */
export function createEmptyState(icon, title, message) {
    return createElement('div',
        { className: 'empty-state' },
        `
            <i class="fas ${icon}"></i>
            <h3>${title}</h3>
            <p>${message}</p>
        `
    );
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Limit in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Check if element is in viewport
 * @param {HTMLElement} element - Element to check
 * @returns {boolean} Whether element is visible
 */
export function isElementInViewport(element) {
    if (!element) return false;
    
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
export async function copyToClipboard(text) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            return true;
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            const success = document.execCommand('copy');
            document.body.removeChild(textArea);
            return success;
        }
    } catch (error) {
        console.error('Failed to copy text:', error);
        return false;
    }
}