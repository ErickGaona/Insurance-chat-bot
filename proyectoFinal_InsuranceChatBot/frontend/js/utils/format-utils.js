/**
 * Format Utilities
 * Text formatting, time formatting, and data formatting functions
 */

/**
 * Format message content with markdown-like syntax
 * @param {string} content - Raw message content
 * @returns {string} Formatted HTML content
 */
export function formatMessage(content) {
    if (!content) return '';
    
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold text
        .replace(/\*(.*?)\*/g, '<em>$1</em>')             // Italic text
        .replace(/`(.*?)`/g, '<code>$1</code>')           // Inline code
        .replace(/\n/g, '<br>')                           // Line breaks
        .replace(/- (.*?)(?=\n|$)/g, '• $1');            // Bullet points
}

/**
 * Format response time in a human-readable format
 * @param {number} milliseconds - Time in milliseconds
 * @returns {string} Formatted time string
 */
export function formatResponseTime(milliseconds) {
    if (milliseconds < 1000) {
        return `${Math.round(milliseconds)}ms`;
    } else {
        const seconds = Math.round(milliseconds / 100) / 10;
        return `${seconds}s`;
    }
}

/**
 * Format file size in human-readable format
 * @param {number} bytes - Size in bytes
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted size string
 */
export function formatFileSize(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Format number with thousands separators
 * @param {number} num - Number to format
 * @param {string} locale - Locale for formatting
 * @returns {string} Formatted number string
 */
export function formatNumber(num, locale = 'es-ES') {
    return new Intl.NumberFormat(locale).format(num);
}

/**
 * Format date in a human-readable format
 * @param {Date|string} date - Date to format
 * @param {string} locale - Locale for formatting
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export function formatDate(date, locale = 'es-ES', options = {}) {
    const dateObj = date instanceof Date ? date : new Date(date);
    
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        ...options
    };
    
    return new Intl.DateTimeFormat(locale, defaultOptions).format(dateObj);
}

/**
 * Format time relative to now (e.g., "2 hours ago")
 * @param {Date|string} date - Date to format
 * @param {string} locale - Locale for formatting
 * @returns {string} Relative time string
 */
export function formatRelativeTime(date, locale = 'es-ES') {
    const dateObj = date instanceof Date ? date : new Date(date);
    const now = new Date();
    const diffInSeconds = Math.floor((now - dateObj) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Hace un momento';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
    } else if (diffInSeconds < 604800) {
        const days = Math.floor(diffInSeconds / 86400);
        return `Hace ${days} día${days > 1 ? 's' : ''}`;
    } else {
        return formatDate(dateObj, locale);
    }
}

/**
 * Truncate text to a specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @param {string} suffix - Suffix to add when truncated
 * @returns {string} Truncated text
 */
export function truncateText(text, maxLength, suffix = '...') {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + suffix;
}

/**
 * Capitalize first letter of a string
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
export function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Convert string to title case
 * @param {string} str - String to convert
 * @returns {string} Title case string
 */
export function toTitleCase(str) {
    if (!str) return '';
    return str.replace(/\w\S*/g, (txt) => 
        txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    );
}

/**
 * Clean and normalize text
 * @param {string} text - Text to clean
 * @returns {string} Cleaned text
 */
export function cleanText(text) {
    if (!text) return '';
    
    return text
        .trim()                           // Remove leading/trailing whitespace
        .replace(/\s+/g, ' ')            // Replace multiple spaces with single space
        .replace(/\n\s*\n/g, '\n\n');    // Normalize line breaks
}

/**
 * Extract keywords from text
 * @param {string} text - Text to extract keywords from
 * @param {number} maxWords - Maximum number of words
 * @returns {Array} Array of keywords
 */
export function extractKeywords(text, maxWords = 10) {
    if (!text) return [];
    
    // Common Spanish stop words
    const stopWords = new Set([
        'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se',
        'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para',
        'del', 'las', 'una', 'al', 'me', 'si', 'ya', 'todo', 'esta',
        'pero', 'más', 'hay', 'muy', 'fue', 'ser', 'han', 'donde'
    ]);
    
    return text
        .toLowerCase()
        .replace(/[^\w\s]/g, '')         // Remove punctuation
        .split(/\s+/)                    // Split by whitespace
        .filter(word => word.length > 2 && !stopWords.has(word))  // Filter short words and stop words
        .slice(0, maxWords);             // Limit number of words
}

/**
 * Highlight keywords in text
 * @param {string} text - Text to highlight
 * @param {Array|string} keywords - Keywords to highlight
 * @param {string} className - CSS class for highlighting
 * @returns {string} Text with highlighted keywords
 */
export function highlightKeywords(text, keywords, className = 'highlight') {
    if (!text || !keywords) return text;
    
    const keywordArray = Array.isArray(keywords) ? keywords : [keywords];
    let highlightedText = text;
    
    keywordArray.forEach(keyword => {
        const regex = new RegExp(`(${keyword})`, 'gi');
        highlightedText = highlightedText.replace(
            regex, 
            `<span class="${className}">$1</span>`
        );
    });
    
    return highlightedText;
}

/**
 * Convert HTML to plain text
 * @param {string} html - HTML string
 * @returns {string} Plain text
 */
export function htmlToText(html) {
    if (!html) return '';
    
    const temp = document.createElement('div');
    temp.innerHTML = html;
    return temp.textContent || temp.innerText || '';
}

/**
 * Format percentage
 * @param {number} value - Value to format as percentage
 * @param {number} total - Total value
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage
 */
export function formatPercentage(value, total, decimals = 1) {
    if (total === 0) return '0%';
    const percentage = (value / total) * 100;
    return `${percentage.toFixed(decimals)}%`;
}

/**
 * Format document metadata for display
 * @param {Object} metadata - Document metadata
 * @returns {Object} Formatted metadata
 */
export function formatDocumentMetadata(metadata) {
    if (!metadata) return {};
    
    return {
        title: metadata.title || metadata.article_title || metadata.file_name || 'Sin título',
        source: metadata.source || 'unknown',
        type: metadata.document_type || 'general',
        date: metadata.created_date ? formatDate(metadata.created_date) : '',
        size: metadata.length ? `${formatNumber(metadata.length)} caracteres` : ''
    };
}

/**
 * Format search strategy display text
 * @param {string} strategy - Search strategy
 * @returns {string} Formatted strategy text
 */
export function formatSearchStrategy(strategy) {
    const strategies = {
        'local_only': 'Solo Local',
        'web_only': 'Solo Web',
        'hybrid': 'Híbrido',
        'fallback': 'Respaldo'
    };
    
    return strategies[strategy] || strategy;
}

/**
 * Format chat message metadata
 * @param {Object} metadata - Message metadata
 * @returns {string} Formatted metadata HTML
 */
export function formatMessageMetadata(metadata) {
    if (!metadata) return '';
    
    let metaHtml = '';
    
    if (metadata.sources) {
        if (metadata.searchStrategy === 'hybrid' && metadata.webSources > 0) {
            metaHtml += `
                <span class="sources-info hybrid-sources">
                    <i class="fas fa-database"></i> ${metadata.localSources} local + 
                    <i class="fas fa-globe"></i> ${metadata.webSources} web
                </span>
            `;
        } else {
            metaHtml += `
                <span class="sources-info">
                    <i class="fas fa-file-alt"></i> ${metadata.sources} fuentes
                </span>
            `;
        }
    }
    
    if (metadata.chatbotType) {
        metaHtml += `
            <span class="chatbot-type">
                ${metadata.chatbotType === 'hybrid' ? 
                    '<i class="fas fa-magic"></i> Híbrido' : 
                    '<i class="fas fa-database"></i> Estándar'}
            </span>
        `;
    }
    
    if (metadata.responseTime) {
        metaHtml += `
            <span class="response-time">
                <i class="fas fa-clock"></i> ${metadata.responseTime}s
            </span>
        `;
    }
    
    return metaHtml;
}