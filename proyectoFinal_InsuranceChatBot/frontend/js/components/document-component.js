import { documentService } from '../services/document-service.js';
import { statsService } from '../services/stats-service.js';
import { appState } from '../state/app-state.js';
import { findElement, createElement, createLoadingElement, createEmptyState } from '../utils/dom-utils.js';
import { formatFileSize, formatDate, formatDocumentMetadata } from '../utils/format-utils.js';
import { fadeIn, fadeOut, animateProgress } from '../utils/animation-utils.js';

/**
 * Document Component
 * Handles document management interface and operations
 */
export class DocumentComponent {
    constructor() {
        this.elements = {};
        this.isInitialized = false;
        this.dragCounter = 0;
        
        this.initializeElements();
        this.setupEventListeners();
        this.setupStateSubscriptions();
        this.setupDragAndDrop();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.elements = {
            // Document manager elements
            documentManagerModal: findElement('#documentManagerModal'),
            documentManagerContent: findElement('#documentManagerContent'),
            documentPagination: findElement('#documentPagination'),
            
            // Upload elements
            pdfFileInput: findElement('#pdfFileInput'),
            textUploadModal: findElement('#textUploadModal'),
            textUploadForm: findElement('#textUploadForm'),
            
            // Filter elements
            documentFilters: findElement('#documentFilters'),
            
            // Drag and drop zone
            dropZone: findElement('.drop-zone') || findElement('body')
        };

        this.isInitialized = true;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        if (!this.isInitialized) return;

        // File input change
        if (this.elements.pdfFileInput) {
            this.elements.pdfFileInput.addEventListener('change', this.handleFileInputChange.bind(this));
        }

        // Text upload form
        if (this.elements.textUploadForm) {
            this.elements.textUploadForm.addEventListener('submit', this.handleTextUpload.bind(this));
        }

        // Modal close events
        document.addEventListener('click', this.handleModalClick.bind(this));
    }

    /**
     * Setup state subscriptions
     */
    setupStateSubscriptions() {
        // Subscribe to document state changes
        appState.subscribe('documents', (documents) => {
            this.renderDocumentList(documents);
        });

        appState.subscribe('documentPagination', (pagination) => {
            this.renderPagination(pagination);
        });

        appState.subscribe('documentFilters', (filters) => {
            this.updateFilterDisplay(filters);
        });
    }

    /**
     * Setup drag and drop functionality
     */
    setupDragAndDrop() {
        if (!this.elements.dropZone) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.elements.dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.elements.dropZone.addEventListener(eventName, this.handleDragEnter.bind(this), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.elements.dropZone.addEventListener(eventName, this.handleDragLeave.bind(this), false);
        });

        this.elements.dropZone.addEventListener('drop', this.handleDrop.bind(this), false);
    }

    /**
     * Load documents
     * @param {number} page - Page number
     */
    async loadDocuments(page = 1) {
        try {
            this.showLoadingInModal();
            
            const filters = appState.get('documentFilters');
            const result = await documentService.loadDocuments(page, filters);
            
            appState.setDocuments(result.documents);
            appState.updateDocumentPagination({
                currentPage: page,
                hasMore: result.pagination.hasMore,
                totalReturned: result.pagination.totalReturned
            });

            // Render the updated document list
            this.renderDocumentList(result.documents);

        } catch (error) {
            this.showError('Error cargando documentos: ' + error.message);
            appState.addError(error);
        }
    }

    /**
     * Render document list
     * @param {Array} documents - Documents to render
     */
    renderDocumentList(documents = []) {
        if (!this.elements.documentManagerContent) return;

        if (documents.length === 0) {
            this.elements.documentManagerContent.innerHTML = createEmptyState(
                'fa-file-alt',
                'No se encontraron documentos',
                'No hay documentos que coincidan con los filtros aplicados.'
            ).outerHTML;
            return;
        }

        const documentsHtml = documents.map(doc => this.createDocumentItemHtml(doc)).join('');
        
        this.elements.documentManagerContent.innerHTML = `
            <div class="document-list">
                ${documentsHtml}
            </div>
        `;
    }

    /**
     * Create document item HTML
     * @param {Object} doc - Document object
     * @returns {string} Document item HTML
     */
    createDocumentItemHtml(doc) {
        const metadata = formatDocumentMetadata(doc.metadata);
        
        return `
            <div class="document-item" data-id="${doc.id}">
                <div class="document-header">
                    <div class="document-info">
                        <h4 class="document-title">${metadata.title}</h4>
                        <div class="document-meta">
                            <span class="meta-badge meta-source">${metadata.source}</span>
                            <span class="meta-badge meta-type">${metadata.type}</span>
                            <span class="meta-info">${metadata.size}</span>
                            ${metadata.date ? `<span class="meta-info">${metadata.date}</span>` : ''}
                        </div>
                    </div>
                    <div class="document-actions">
                        <button class="btn-icon" onclick="documentComponent.viewDocument('${doc.id}')" title="Ver documento">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-icon" onclick="documentComponent.editDocument('${doc.id}')" title="Editar documento">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-icon btn-danger" onclick="documentComponent.deleteDocument('${doc.id}')" title="Eliminar documento">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="document-preview">
                    ${doc.preview || ''}
                </div>
            </div>
        `;
    }

    /**
     * Render pagination
     * @param {Object} pagination - Pagination object
     */
    renderPagination(pagination) {
        if (!this.elements.documentPagination) return;

        const { currentPage, hasMore, totalReturned } = pagination;

        let paginationHtml = `
            <div class="pagination">
                <button class="pagination-btn" ${currentPage <= 1 ? 'disabled' : ''} 
                        onclick="documentComponent.loadDocuments(${currentPage - 1})">
                    <i class="fas fa-chevron-left"></i>
                </button>
                
                <span class="pagination-info">Página ${currentPage}</span>
                
                <button class="pagination-btn" ${!hasMore ? 'disabled' : ''} 
                        onclick="documentComponent.loadDocuments(${currentPage + 1})">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
            <div class="pagination-info">
                ${totalReturned} documentos encontrados
            </div>
        `;

        this.elements.documentPagination.innerHTML = paginationHtml;
    }

    /**
     * Handle file input change
     * @param {Event} event - Change event
     */
    handleFileInputChange(event) {
        const file = event.target.files[0];
        if (file) {
            this.handleFileUpload(file);
            // Clear the input so the same file can be selected again
            event.target.value = '';
        }
    }

    /**
     * Handle file upload
     * @param {File} file - File to upload
     */
    async handleFileUpload(file) {
        // Validate file
        const validation = documentService.validateFile(file);
        if (!validation.isValid) {
            this.showError(validation.errors.join(', '));
            return;
        }

        try {
            // Show upload status in header
            this.showUploadStatus('Subiendo archivo...', 'uploading');
            
            // Create progress indicator
            const progressElement = this.createProgressIndicator();
            
            // Upload with progress tracking
            const result = await documentService.uploadFile(file, (progress) => {
                this.updateProgress(progressElement, progress);
            });

            this.hideProgress(progressElement);

            if (result.status === 'success') {
                this.showUploadStatus('Archivo subido correctamente', 'success');
                this.showSuccess('Archivo subido exitosamente');
                // Reload documents to show the new one
                this.loadDocuments(appState.get('documentPagination.currentPage'));
                // Update stats to refresh document counter
                statsService.loadBackendStats();
            } else {
                this.showUploadStatus('Error al subir archivo', 'error');
                this.showError(result.error || 'Error al procesar archivo');
            }

        } catch (error) {
            this.showError('Error de conexión al subir archivo');
            console.error('File upload error:', error);
        }
    }

    /**
     * Handle text document upload
     * @param {Event} event - Form submit event
     */
    async handleTextUpload(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const documentData = {
            title: formData.get('title'),
            text: formData.get('content'),
            source: formData.get('source') || 'manual',
            document_type: formData.get('document_type') || 'text'
        };

        // Validate required fields
        if (!documentData.title || !documentData.text) {
            this.showError('Por favor complete todos los campos requeridos');
            return;
        }

        try {
            const result = await documentService.uploadTextDocument(documentData);

            if (result.status === 'success') {
                this.showSuccess('Documento agregado exitosamente');
                this.closeTextUploadModal();
                // Reset the form
                event.target.reset();
                // Reload documents
                this.loadDocuments(appState.get('documentPagination.currentPage'));
                // Update stats to refresh document counter
                statsService.loadBackendStats();
            } else {
                this.showError(result.error || 'Error al agregar documento');
            }

        } catch (error) {
            this.showError('Error de conexión al agregar documento');
            console.error('Text upload error:', error);
        }
    }

    /**
     * Delete document
     * @param {string} documentId - Document ID
     */
    async deleteDocument(documentId) {
        if (!confirm('¿Está seguro de que desea eliminar este documento?')) {
            return;
        }

        try {
            const result = await documentService.deleteDocument(documentId);
            
            if (result.status === 'success') {
                this.showSuccess('Documento eliminado exitosamente');
                // Reload current page
                this.loadDocuments(appState.get('documentPagination.currentPage'));
            } else {
                this.showError(result.error || 'Error al eliminar documento');
            }

        } catch (error) {
            this.showError('Error eliminando documento: ' + error.message);
            console.error('Delete error:', error);
        }
    }

    /**
     * View document
     * @param {string} documentId - Document ID
     */
    async viewDocument(documentId) {
        try {
            const document = await documentService.getDocument(documentId);
            console.log('Viewing document:', document);
            
            // Open the document viewer modal
            this.openDocumentViewer(document);
        } catch (error) {
            this.showError('Error cargando documento: ' + error.message);
        }
    }

    /**
     * Open document viewer modal
     * @param {Object} document - Document data
     */
    openDocumentViewer(document) {
        const modal = findElement('#documentViewModal');
        const titleElement = findElement('#viewDocumentTitle');
        const contentElement = findElement('#viewDocumentContent');
        
        if (modal && titleElement && contentElement) {
            // Set document title
            titleElement.textContent = document.metadata?.file_name || document.id || 'Document';
            
            // Set document content with proper formatting
            contentElement.textContent = document.content || 'No content available';
            
            // Show the modal
            modal.style.display = 'flex';
            modal.classList.add('active');
            
            // Add fade in animation
            fadeIn(modal);
        } else {
            this.showError('Error: Document viewer modal not found');
        }
    }

    /**
     * Edit document
     * @param {string} documentId - Document ID
     */
    async editDocument(documentId) {
        try {
            const document = await documentService.getDocument(documentId);
            console.log('Editing document:', document);
            
            // For now, just open the document viewer since editing extracted PDF content
            // would require re-processing. Show document for review instead.
            this.openDocumentViewer(document);
            
            // Show info about editing limitations
            setTimeout(() => {
                this.showInfo('Los documentos extraídos de PDF no son editables. Use "Agregar Texto" para crear documentos editables.');
            }, 1000);
            
        } catch (error) {
            this.showError('Error cargando documento para edición: ' + error.message);
        }
    }

    /**
     * Drag and drop event handlers
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDragEnter(e) {
        this.dragCounter++;
        this.elements.dropZone.classList.add('drag-over');
    }

    handleDragLeave(e) {
        this.dragCounter--;
        if (this.dragCounter === 0) {
            this.elements.dropZone.classList.remove('drag-over');
        }
    }

    handleDrop(e) {
        this.dragCounter = 0;
        this.elements.dropZone.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files);
        files.forEach(file => this.handleFileUpload(file));
    }

    /**
     * Modal event handlers
     */
    handleModalClick(event) {
        if (event.target.classList.contains('modal-overlay')) {
            this.closeTextUploadModal();
            this.closeDocumentManagerModal();
        }
    }

    /**
     * UI Helper methods
     */
    showLoadingInModal(text = 'Cargando documentos...') {
        if (this.elements.documentManagerContent) {
            this.elements.documentManagerContent.innerHTML = createLoadingElement(text).outerHTML;
        }
    }

    createProgressIndicator() {
        const progressElement = createElement('div', 
            { className: 'upload-progress' },
            `
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <span class="progress-text">0%</span>
            `
        );
        
        document.body.appendChild(progressElement);
        return progressElement;
    }

    updateProgress(progressElement, percent) {
        if (!progressElement) return;
        
        const progressFill = progressElement.querySelector('.progress-fill');
        const progressText = progressElement.querySelector('.progress-text');
        
        if (progressFill) {
            animateProgress(progressFill, percent);
        }
        if (progressText) {
            progressText.textContent = `${Math.round(percent)}%`;
        }
    }

    hideProgress(progressElement) {
        if (progressElement && progressElement.parentNode) {
            fadeOut(progressElement).then(() => {
                progressElement.parentNode.removeChild(progressElement);
            });
        }
    }

    updateFilterDisplay(filters) {
        // Update filter UI elements if they exist
        Object.keys(filters).forEach(key => {
            const filterElement = findElement(`[name="${key}"]`);
            if (filterElement) {
                filterElement.value = filters[key];
            }
        });
    }

    closeTextUploadModal() {
        if (this.elements.textUploadModal) {
            this.elements.textUploadModal.style.display = 'none';
        }
    }

    closeDocumentManagerModal() {
        if (this.elements.documentManagerModal) {
            this.elements.documentManagerModal.style.display = 'none';
        }
    }

    showError(message) {
        // This could be handled by a separate toast component
        console.error('Document error:', message);
        appState.addError(new Error(message));
    }

    showSuccess(message) {
        // Use the global UI component for success toasts
        if (window.insuranceChatbotApp) {
            const uiComponent = window.insuranceChatbotApp.components.get('ui');
            if (uiComponent) {
                uiComponent.showSuccess(message);
                return;
            }
        }
        // Fallback to console if UI component not available
        console.log('Document success:', message);
    }

    showInfo(message) {
        // Show info message as a toast notification
        this.showUploadStatus(message, 'info');
    }

    /**
     * Public API methods
     */
    openDocumentManager() {
        if (this.elements.documentManagerModal) {
            this.elements.documentManagerModal.style.display = 'block';
            this.loadDocuments(1);
        }
    }

    openTextUploadModal() {
        if (this.elements.textUploadModal) {
            this.elements.textUploadModal.style.display = 'block';
        }
    }

    setFilters(filters) {
        appState.updateDocumentFilters(filters);
        this.loadDocuments(1); // Reset to first page when filtering
    }

    clearFilters() {
        appState.updateDocumentFilters({
            source: '',
            document_type: '',
            file_name: ''
        });
        this.loadDocuments(1);
    }

    /**
     * Destroy component and cleanup
     */
    destroy() {
        // Remove event listeners
        if (this.elements.pdfFileInput) {
            this.elements.pdfFileInput.removeEventListener('change', this.handleFileInputChange);
        }

        // Remove drag and drop listeners
        if (this.elements.dropZone) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                this.elements.dropZone.removeEventListener(eventName, this.preventDefaults);
            });
        }

        this.elements = {};
        this.isInitialized = false;
    }

    /**
     * Show upload status in header
     * @param {string} message - Status message
     * @param {string} type - Status type (uploading, success, error)
     */
    showUploadStatus(message, type) {
        // Find or create status element in header
        let statusElement = document.querySelector('.upload-status');
        if (!statusElement) {
            statusElement = document.createElement('div');
            statusElement.className = 'upload-status';
            statusElement.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                z-index: 1000;
                transition: opacity 0.3s ease;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            `;
            document.body.appendChild(statusElement);
        }

        // Set message and styling based on type
        statusElement.textContent = message;
        statusElement.className = 'upload-status';
        
        if (type === 'uploading') {
            statusElement.style.backgroundColor = '#3498db';
            statusElement.style.color = 'white';
        } else if (type === 'success') {
            statusElement.style.backgroundColor = '#2ecc71';
            statusElement.style.color = 'white';
            // Auto-hide success message after 3 seconds
            setTimeout(() => this.hideUploadStatus(), 3000);
        } else if (type === 'error') {
            statusElement.style.backgroundColor = '#e74c3c';
            statusElement.style.color = 'white';
            // Auto-hide error message after 5 seconds
            setTimeout(() => this.hideUploadStatus(), 5000);
        } else if (type === 'info') {
            statusElement.style.backgroundColor = '#f39c12';
            statusElement.style.color = 'white';
            // Auto-hide info message after 4 seconds
            setTimeout(() => this.hideUploadStatus(), 4000);
        }

        statusElement.style.opacity = '1';
    }

    /**
     * Hide upload status
     */
    hideUploadStatus() {
        const statusElement = document.querySelector('.upload-status');
        if (statusElement) {
            statusElement.style.opacity = '0';
            setTimeout(() => statusElement.remove(), 300);
        }
    }
}

// Export singleton instance
export const documentComponent = new DocumentComponent();