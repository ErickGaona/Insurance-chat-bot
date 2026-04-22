import { apiService } from './api-service.js';
import { API_CONFIG } from '../config/api-config.js';

/**
 * Document Service
 * Handles document upload, management, and retrieval
 */
export class DocumentService {
    constructor() {
        this.currentDocuments = [];
        this.currentPage = 1;
        this.perPage = 20;
        this.totalPages = 1;
        this.filters = {
            source: '',
            document_type: '',
            file_name: ''
        };
    }

    /**
     * Upload a file document
     * @param {File} file - File to upload
     * @param {Function} onProgress - Progress callback
     * @returns {Promise} Upload result
     */
    async uploadFile(file, onProgress = null) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            // If we need progress tracking, we'll need to use XMLHttpRequest
            if (onProgress) {
                return this.uploadFileWithProgress(formData, onProgress);
            }

            const response = await apiService.postFormData(
                API_CONFIG.endpoints.documentsUpload,
                formData
            );

            return response;
        } catch (error) {
            console.error('File upload error:', error);
            throw error;
        }
    }

    /**
     * Upload file with progress tracking
     * @param {FormData} formData - Form data with file
     * @param {Function} onProgress - Progress callback
     * @returns {Promise} Upload result
     */
    uploadFileWithProgress(formData, onProgress) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    onProgress(percentComplete);
                }
            };

            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (error) {
                        reject(new Error('Invalid JSON response'));
                    }
                } else {
                    reject(new Error(`HTTP error! status: ${xhr.status}`));
                }
            };

            xhr.onerror = () => {
                reject(new Error('Network error during upload'));
            };

            xhr.open('POST', `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.documentsUpload}`);
            xhr.send(formData);
        });
    }

    /**
     * Upload text document
     * @param {Object} documentData - Document data
     * @returns {Promise} Upload result
     */
    async uploadTextDocument(documentData) {
        try {
            const response = await apiService.post(
                API_CONFIG.endpoints.documentsUpload,
                documentData
            );

            return response;
        } catch (error) {
            console.error('Text document upload error:', error);
            throw error;
        }
    }

    /**
     * Load documents with pagination and filters
     * @param {number} page - Page number
     * @param {Object} filters - Filter options
     * @returns {Promise} Documents data
     */
    async loadDocuments(page = 1, filters = {}) {
        try {
            const params = new URLSearchParams({
                limit: this.perPage,
                offset: (page - 1) * this.perPage
            });

            // Merge with instance filters
            const combinedFilters = { ...this.filters, ...filters };
            
            // Add filters if set
            Object.keys(combinedFilters).forEach(key => {
                if (combinedFilters[key]) {
                    params.append(key, combinedFilters[key]);
                }
            });

            const response = await apiService.get(`${API_CONFIG.endpoints.documents}/?${params}`);

            if (response.status === 'success') {
                this.currentDocuments = response.documents;
                this.currentPage = page;
                
                // Calculate pagination info
                const totalReturned = response.total_returned;
                const hasMore = totalReturned === this.perPage;
                
                return {
                    documents: response.documents,
                    pagination: {
                        currentPage: page,
                        hasMore,
                        totalReturned
                    }
                };
            } else {
                throw new Error(response.error || 'Failed to load documents');
            }
        } catch (error) {
            console.error('Error loading documents:', error);
            throw error;
        }
    }

    /**
     * Delete a document
     * @param {string} documentId - Document ID
     * @returns {Promise} Delete result
     */
    async deleteDocument(documentId) {
        try {
            const response = await apiService.request(`${API_CONFIG.endpoints.documents}/${documentId}`, {
                method: 'DELETE'
            });

            return response;
        } catch (error) {
            console.error('Error deleting document:', error);
            throw error;
        }
    }

    /**
     * Delete multiple documents
     * @param {Array} documentIds - Array of document IDs
     * @returns {Promise} Delete results
     */
    async deleteMultipleDocuments(documentIds) {
        try {
            const results = await Promise.allSettled(
                documentIds.map(id => this.deleteDocument(id))
            );

            const successful = results.filter(r => r.status === 'fulfilled').length;
            const failed = results.filter(r => r.status === 'rejected').length;

            return {
                successful,
                failed,
                total: documentIds.length,
                results
            };
        } catch (error) {
            console.error('Error deleting multiple documents:', error);
            throw error;
        }
    }

    /**
     * Get document by ID
     * @param {string} documentId - Document ID
     * @returns {Promise} Document data
     */
    async getDocument(documentId) {
        try {
            const response = await apiService.get(`${API_CONFIG.endpoints.documents}/${documentId}`);
            return response;
        } catch (error) {
            console.error('Error getting document:', error);
            throw error;
        }
    }

    /**
     * Update document
     * @param {string} documentId - Document ID
     * @param {Object} updateData - Update data
     * @returns {Promise} Update result
     */
    async updateDocument(documentId, updateData) {
        try {
            const response = await apiService.request(`${API_CONFIG.endpoints.documents}/${documentId}`, {
                method: 'PUT',
                body: JSON.stringify(updateData)
            });

            return response;
        } catch (error) {
            console.error('Error updating document:', error);
            throw error;
        }
    }

    /**
     * Validate file before upload
     * @param {File} file - File to validate
     * @returns {Object} Validation result
     */
    validateFile(file) {
        const maxSize = API_CONFIG.maxFileSize;
        const allowedTypes = API_CONFIG.allowedFileTypes;
        
        const errors = [];
        
        // Check file size
        if (file.size > maxSize) {
            errors.push(`El archivo es demasiado grande. Tamaño máximo: ${maxSize / (1024 * 1024)}MB`);
        }
        
        // Check file type
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExtension)) {
            errors.push(`Tipo de archivo no permitido. Tipos permitidos: ${allowedTypes.join(', ')}`);
        }

        return {
            isValid: errors.length === 0,
            errors,
            file: {
                name: file.name,
                size: file.size,
                type: file.type,
                extension: fileExtension
            }
        };
    }

    /**
     * Set filters
     * @param {Object} filters - Filter options
     */
    setFilters(filters) {
        this.filters = { ...this.filters, ...filters };
    }

    /**
     * Clear filters
     */
    clearFilters() {
        this.filters = {
            source: '',
            document_type: '',
            file_name: ''
        };
    }

    /**
     * Get current filters
     * @returns {Object} Current filters
     */
    getFilters() {
        return { ...this.filters };
    }

    /**
     * Get current documents
     * @returns {Array} Current documents
     */
    getCurrentDocuments() {
        return this.currentDocuments;
    }

    /**
     * Get document statistics
     * @returns {Promise} Document statistics
     */
    async getDocumentStatistics() {
        try {
            // This could be a separate endpoint or derived from documents list
            const response = await this.loadDocuments(1);
            
            return {
                totalDocuments: response.documents.length,
                documentTypes: [...new Set(response.documents.map(doc => doc.metadata?.document_type).filter(Boolean))],
                sources: [...new Set(response.documents.map(doc => doc.metadata?.source).filter(Boolean))]
            };
        } catch (error) {
            console.error('Error getting document statistics:', error);
            throw error;
        }
    }
}

// Export singleton instance
export const documentService = new DocumentService();