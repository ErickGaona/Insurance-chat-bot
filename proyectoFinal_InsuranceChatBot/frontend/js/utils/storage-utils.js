/**
 * Storage Utilities
 * LocalStorage operations with error handling and data validation
 */

/**
 * Get item from localStorage with JSON parsing
 * @param {string} key - Storage key
 * @param {*} defaultValue - Default value if key doesn't exist
 * @returns {*} Parsed value or default
 */
export function getStorageItem(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.warn(`Error reading from localStorage key "${key}":`, error);
        return defaultValue;
    }
}

/**
 * Set item in localStorage with JSON stringification
 * @param {string} key - Storage key
 * @param {*} value - Value to store
 * @returns {boolean} Success status
 */
export function setStorageItem(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (error) {
        console.warn(`Error writing to localStorage key "${key}":`, error);
        return false;
    }
}

/**
 * Remove item from localStorage
 * @param {string} key - Storage key
 * @returns {boolean} Success status
 */
export function removeStorageItem(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (error) {
        console.warn(`Error removing from localStorage key "${key}":`, error);
        return false;
    }
}

/**
 * Check if localStorage is available
 * @returns {boolean} Availability status
 */
export function isStorageAvailable() {
    try {
        const test = '__storage_test__';
        localStorage.setItem(test, test);
        localStorage.removeItem(test);
        return true;
    } catch (error) {
        return false;
    }
}

/**
 * Get storage quota information
 * @returns {Object} Storage quota info
 */
export async function getStorageQuota() {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
        try {
            const estimate = await navigator.storage.estimate();
            return {
                quota: estimate.quota,
                usage: estimate.usage,
                available: estimate.quota - estimate.usage,
                usagePercentage: Math.round((estimate.usage / estimate.quota) * 100)
            };
        } catch (error) {
            console.warn('Error getting storage quota:', error);
        }
    }
    
    return {
        quota: null,
        usage: null,
        available: null,
        usagePercentage: null
    };
}

/**
 * Clear all app-related localStorage items
 * @param {Array} keys - Array of keys to clear
 * @returns {number} Number of items cleared
 */
export function clearAppStorage(keys = []) {
    let cleared = 0;
    
    if (keys.length === 0) {
        // Clear all if no specific keys provided
        try {
            const allKeys = Object.keys(localStorage);
            allKeys.forEach(key => {
                localStorage.removeItem(key);
                cleared++;
            });
        } catch (error) {
            console.warn('Error clearing all localStorage:', error);
        }
    } else {
        // Clear specific keys
        keys.forEach(key => {
            if (removeStorageItem(key)) {
                cleared++;
            }
        });
    }
    
    return cleared;
}

/**
 * Export localStorage data
 * @param {Array} keys - Keys to export (all if empty)
 * @returns {Object} Exported data
 */
export function exportStorageData(keys = []) {
    const exportData = {
        timestamp: new Date().toISOString(),
        data: {}
    };
    
    try {
        const keysToExport = keys.length > 0 ? keys : Object.keys(localStorage);
        
        keysToExport.forEach(key => {
            const value = getStorageItem(key);
            if (value !== null) {
                exportData.data[key] = value;
            }
        });
        
        return exportData;
    } catch (error) {
        console.warn('Error exporting storage data:', error);
        return exportData;
    }
}

/**
 * Import localStorage data
 * @param {Object} data - Data to import
 * @param {boolean} overwrite - Whether to overwrite existing data
 * @returns {Object} Import result
 */
export function importStorageData(data, overwrite = false) {
    const result = {
        success: 0,
        failed: 0,
        skipped: 0,
        errors: []
    };
    
    if (!data || !data.data) {
        result.errors.push('Invalid import data format');
        return result;
    }
    
    Object.keys(data.data).forEach(key => {
        try {
            const existingValue = getStorageItem(key);
            
            if (existingValue !== null && !overwrite) {
                result.skipped++;
                return;
            }
            
            if (setStorageItem(key, data.data[key])) {
                result.success++;
            } else {
                result.failed++;
                result.errors.push(`Failed to import key: ${key}`);
            }
        } catch (error) {
            result.failed++;
            result.errors.push(`Error importing key "${key}": ${error.message}`);
        }
    });
    
    return result;
}

/**
 * Get localStorage size for a specific key
 * @param {string} key - Storage key
 * @returns {number} Size in bytes
 */
export function getStorageSize(key) {
    try {
        const value = localStorage.getItem(key);
        return value ? new Blob([value]).size : 0;
    } catch (error) {
        console.warn(`Error getting size for key "${key}":`, error);
        return 0;
    }
}

/**
 * Get total localStorage size
 * @returns {number} Total size in bytes
 */
export function getTotalStorageSize() {
    let totalSize = 0;
    
    try {
        Object.keys(localStorage).forEach(key => {
            totalSize += getStorageSize(key);
        });
    } catch (error) {
        console.warn('Error calculating total storage size:', error);
    }
    
    return totalSize;
}

/**
 * Watch for storage changes
 * @param {Function} callback - Callback function
 * @param {Array} keys - Keys to watch (all if empty)
 * @returns {Function} Cleanup function
 */
export function watchStorage(callback, keys = []) {
    const handler = (event) => {
        if (keys.length === 0 || keys.includes(event.key)) {
            callback({
                key: event.key,
                oldValue: event.oldValue,
                newValue: event.newValue,
                url: event.url
            });
        }
    };
    
    window.addEventListener('storage', handler);
    
    // Return cleanup function
    return () => {
        window.removeEventListener('storage', handler);
    };
}

/**
 * Cache manager for temporary data
 */
export class CacheManager {
    constructor(keyPrefix = 'cache_', defaultTTL = 3600000) { // 1 hour default TTL
        this.keyPrefix = keyPrefix;
        this.defaultTTL = defaultTTL;
    }
    
    /**
     * Set cached item with TTL
     * @param {string} key - Cache key
     * @param {*} value - Value to cache
     * @param {number} ttl - Time to live in milliseconds
     */
    set(key, value, ttl = this.defaultTTL) {
        const cacheKey = this.keyPrefix + key;
        const cacheData = {
            value,
            timestamp: Date.now(),
            ttl
        };
        
        setStorageItem(cacheKey, cacheData);
    }
    
    /**
     * Get cached item
     * @param {string} key - Cache key
     * @returns {*} Cached value or null if expired/not found
     */
    get(key) {
        const cacheKey = this.keyPrefix + key;
        const cacheData = getStorageItem(cacheKey);
        
        if (!cacheData) return null;
        
        const now = Date.now();
        const age = now - cacheData.timestamp;
        
        if (age > cacheData.ttl) {
            this.delete(key);
            return null;
        }
        
        return cacheData.value;
    }
    
    /**
     * Delete cached item
     * @param {string} key - Cache key
     */
    delete(key) {
        const cacheKey = this.keyPrefix + key;
        removeStorageItem(cacheKey);
    }
    
    /**
     * Clear all cached items
     */
    clear() {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith(this.keyPrefix)) {
                    localStorage.removeItem(key);
                }
            });
        } catch (error) {
            console.warn('Error clearing cache:', error);
        }
    }
    
    /**
     * Clean expired cache items
     */
    cleanExpired() {
        try {
            const keys = Object.keys(localStorage);
            const now = Date.now();
            
            keys.forEach(key => {
                if (key.startsWith(this.keyPrefix)) {
                    const cacheData = getStorageItem(key);
                    if (cacheData && (now - cacheData.timestamp) > cacheData.ttl) {
                        localStorage.removeItem(key);
                    }
                }
            });
        } catch (error) {
            console.warn('Error cleaning expired cache:', error);
        }
    }
}

// Default cache manager instance
export const cacheManager = new CacheManager();