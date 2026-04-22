/**
 * Animation Utilities
 * CSS animation helpers and transition management
 */

/**
 * Predefined animation configurations
 */
export const ANIMATIONS = {
    fadeIn: {
        keyframes: [
            { opacity: 0 },
            { opacity: 1 }
        ],
        options: { duration: 300, easing: 'ease-in' }
    },
    fadeOut: {
        keyframes: [
            { opacity: 1 },
            { opacity: 0 }
        ],
        options: { duration: 300, easing: 'ease-out' }
    },
    slideUp: {
        keyframes: [
            { transform: 'translateY(20px)', opacity: 0 },
            { transform: 'translateY(0)', opacity: 1 }
        ],
        options: { duration: 400, easing: 'ease-out' }
    },
    slideDown: {
        keyframes: [
            { transform: 'translateY(-20px)', opacity: 0 },
            { transform: 'translateY(0)', opacity: 1 }
        ],
        options: { duration: 400, easing: 'ease-out' }
    },
    slideLeft: {
        keyframes: [
            { transform: 'translateX(20px)', opacity: 0 },
            { transform: 'translateX(0)', opacity: 1 }
        ],
        options: { duration: 400, easing: 'ease-out' }
    },
    slideRight: {
        keyframes: [
            { transform: 'translateX(-20px)', opacity: 0 },
            { transform: 'translateX(0)', opacity: 1 }
        ],
        options: { duration: 400, easing: 'ease-out' }
    },
    pulse: {
        keyframes: [
            { transform: 'scale(1)' },
            { transform: 'scale(1.05)' },
            { transform: 'scale(1)' }
        ],
        options: { duration: 1000, iterations: Infinity }
    },
    bounce: {
        keyframes: [
            { transform: 'translateY(0)' },
            { transform: 'translateY(-10px)' },
            { transform: 'translateY(0)' }
        ],
        options: { duration: 600, easing: 'ease-in-out' }
    },
    shake: {
        keyframes: [
            { transform: 'translateX(0)' },
            { transform: 'translateX(-10px)' },
            { transform: 'translateX(10px)' },
            { transform: 'translateX(-10px)' },
            { transform: 'translateX(0)' }
        ],
        options: { duration: 400, easing: 'ease-in-out' }
    }
};

/**
 * Animate element using Web Animations API
 * @param {HTMLElement} element - Element to animate
 * @param {Object} animation - Animation configuration
 * @returns {Animation} Animation instance
 */
export function animate(element, animation) {
    if (!element || !animation) return null;
    
    try {
        return element.animate(animation.keyframes, animation.options);
    } catch (error) {
        console.warn('Animation failed:', error);
        return null;
    }
}

/**
 * Animate element with predefined animation
 * @param {HTMLElement} element - Element to animate
 * @param {string} animationName - Name of predefined animation
 * @param {Object} customOptions - Custom animation options
 * @returns {Animation} Animation instance
 */
export function animateElement(element, animationName, customOptions = {}) {
    const animation = ANIMATIONS[animationName];
    if (!animation) {
        console.warn(`Animation "${animationName}" not found`);
        return null;
    }
    
    const mergedAnimation = {
        keyframes: animation.keyframes,
        options: { ...animation.options, ...customOptions }
    };
    
    return animate(element, mergedAnimation);
}

/**
 * Fade in element
 * @param {HTMLElement} element - Element to fade in
 * @param {number} duration - Animation duration in milliseconds
 * @returns {Promise} Animation completion promise
 */
export function fadeIn(element, duration = 300) {
    return new Promise((resolve) => {
        if (!element) {
            resolve();
            return;
        }
        
        const animation = animateElement(element, 'fadeIn', { duration });
        
        if (animation) {
            animation.onfinish = resolve;
        } else {
            // Fallback for browsers without Web Animations API
            element.style.transition = `opacity ${duration}ms ease-in`;
            element.style.opacity = '0';
            setTimeout(() => {
                element.style.opacity = '1';
                setTimeout(resolve, duration);
            }, 10);
        }
    });
}

/**
 * Fade out element
 * @param {HTMLElement} element - Element to fade out
 * @param {number} duration - Animation duration in milliseconds
 * @returns {Promise} Animation completion promise
 */
export function fadeOut(element, duration = 300) {
    return new Promise((resolve) => {
        if (!element) {
            resolve();
            return;
        }
        
        const animation = animateElement(element, 'fadeOut', { duration });
        
        if (animation) {
            animation.onfinish = resolve;
        } else {
            // Fallback
            element.style.transition = `opacity ${duration}ms ease-out`;
            element.style.opacity = '1';
            setTimeout(() => {
                element.style.opacity = '0';
                setTimeout(resolve, duration);
            }, 10);
        }
    });
}

/**
 * Slide element in from bottom
 * @param {HTMLElement} element - Element to slide in
 * @param {number} duration - Animation duration in milliseconds
 * @returns {Promise} Animation completion promise
 */
export function slideInUp(element, duration = 400) {
    return new Promise((resolve) => {
        if (!element) {
            resolve();
            return;
        }
        
        const animation = animateElement(element, 'slideUp', { duration });
        
        if (animation) {
            animation.onfinish = resolve;
        } else {
            // Fallback
            element.style.transition = `all ${duration}ms ease-out`;
            element.style.transform = 'translateY(20px)';
            element.style.opacity = '0';
            setTimeout(() => {
                element.style.transform = 'translateY(0)';
                element.style.opacity = '1';
                setTimeout(resolve, duration);
            }, 10);
        }
    });
}

/**
 * Create typing indicator animation
 * @param {HTMLElement} container - Container element
 * @returns {HTMLElement} Typing indicator element
 */
export function createTypingIndicator(container) {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        dot.style.animationDelay = `${i * 0.2}s`;
        typingDiv.appendChild(dot);
    }
    
    if (container) {
        container.appendChild(typingDiv);
    }
    
    return typingDiv;
}

/**
 * Create loading spinner
 * @param {HTMLElement} container - Container element
 * @param {string} className - CSS class name
 * @returns {HTMLElement} Spinner element
 */
export function createLoadingSpinner(container, className = 'loading-spinner') {
    const spinnerDiv = document.createElement('div');
    spinnerDiv.className = className;
    
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinnerDiv.appendChild(spinner);
    
    if (container) {
        container.appendChild(spinnerDiv);
    }
    
    return spinnerDiv;
}

/**
 * Animate counter from start to end value
 * @param {HTMLElement} element - Element to update with count
 * @param {number} start - Start value
 * @param {number} end - End value
 * @param {number} duration - Animation duration in milliseconds
 * @param {Function} formatter - Value formatter function
 */
export function animateCounter(element, start, end, duration = 1000, formatter = null) {
    if (!element) return;
    
    const startTime = performance.now();
    const startValue = parseFloat(start) || 0;
    const endValue = parseFloat(end) || 0;
    const difference = endValue - startValue;
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Use easing function for smoother animation
        const easedProgress = easeOutCubic(progress);
        const currentValue = startValue + (difference * easedProgress);
        
        const displayValue = formatter ? formatter(currentValue) : Math.round(currentValue);
        element.textContent = displayValue;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            const finalValue = formatter ? formatter(endValue) : Math.round(endValue);
            element.textContent = finalValue;
        }
    }
    
    requestAnimationFrame(updateCounter);
}

/**
 * Easing function: ease-out-cubic
 * @param {number} t - Progress (0-1)
 * @returns {number} Eased value
 */
function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
}

/**
 * Animate progress bar
 * @param {HTMLElement} progressBar - Progress bar element
 * @param {number} targetPercent - Target percentage (0-100)
 * @param {number} duration - Animation duration in milliseconds
 */
export function animateProgress(progressBar, targetPercent, duration = 1000) {
    if (!progressBar) return;
    
    const startTime = performance.now();
    const startPercent = parseFloat(progressBar.style.width) || 0;
    const difference = targetPercent - startPercent;
    
    function updateProgress(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const easedProgress = easeOutCubic(progress);
        const currentPercent = startPercent + (difference * easedProgress);
        
        progressBar.style.width = `${currentPercent}%`;
        
        if (progress < 1) {
            requestAnimationFrame(updateProgress);
        } else {
            progressBar.style.width = `${targetPercent}%`;
        }
    }
    
    requestAnimationFrame(updateProgress);
}

/**
 * Stagger animation for multiple elements
 * @param {NodeList|Array} elements - Elements to animate
 * @param {string} animationName - Animation name
 * @param {number} staggerDelay - Delay between elements in milliseconds
 * @param {Object} options - Animation options
 */
export function staggerAnimation(elements, animationName, staggerDelay = 100, options = {}) {
    if (!elements || elements.length === 0) return;
    
    elements.forEach((element, index) => {
        setTimeout(() => {
            animateElement(element, animationName, options);
        }, index * staggerDelay);
    });
}

/**
 * Create pulse animation for element
 * @param {HTMLElement} element - Element to pulse
 * @param {number} duration - Pulse duration
 * @param {number} iterations - Number of iterations (Infinity for continuous)
 */
export function pulseElement(element, duration = 1000, iterations = Infinity) {
    if (!element) return null;
    
    return animateElement(element, 'pulse', { duration, iterations });
}

/**
 * Shake element (for error indication)
 * @param {HTMLElement} element - Element to shake
 * @param {number} duration - Shake duration
 */
export function shakeElement(element, duration = 400) {
    if (!element) return null;
    
    return animateElement(element, 'shake', { duration });
}

/**
 * Check if element supports Web Animations API
 * @returns {boolean} Support status
 */
export function supportsWebAnimations() {
    return 'animate' in HTMLElement.prototype;
}

/**
 * Add CSS transition to element
 * @param {HTMLElement} element - Element to add transition
 * @param {string} property - CSS property to transition
 * @param {number} duration - Transition duration in milliseconds
 * @param {string} easing - Transition easing function
 */
export function addTransition(element, property = 'all', duration = 300, easing = 'ease') {
    if (!element) return;
    
    element.style.transition = `${property} ${duration}ms ${easing}`;
}

/**
 * Remove all transitions from element
 * @param {HTMLElement} element - Element to remove transitions from
 */
export function removeTransitions(element) {
    if (!element) return;
    
    element.style.transition = 'none';
}