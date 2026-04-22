import { chatService } from '../services/chat-service.js';
import { statsService } from '../services/stats-service.js';
import { appState } from '../state/app-state.js';
import { findElement, autoResizeTextarea, scrollToBottom, addFadeInAnimation } from '../utils/dom-utils.js';
import { formatMessage, formatMessageMetadata } from '../utils/format-utils.js';
import { fadeIn, createTypingIndicator } from '../utils/animation-utils.js';
import { APP_CONSTANTS } from '../config/api-config.js';

/**
 * Chat Component
 * Handles chat interface, message rendering, and user interactions
 */
export class ChatComponent {
    constructor() {
        this.elements = {};
        this.isInitialized = false;
        this.currentLoadingId = null;
        
        this.initializeElements();
        this.setupEventListeners();
        this.setupStateSubscriptions();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.elements = {
            chatMessages: findElement('#chatMessages'),
            chatInput: findElement('#chatInput'),
            sendButton: findElement('#sendButton'),
            charCount: findElement('#charCount'),
            chatContainer: findElement('.chat-container')
        };

        // Validate required elements
        const requiredElements = ['chatMessages', 'chatInput', 'sendButton'];
        const missingElements = requiredElements.filter(key => !this.elements[key]);
        
        if (missingElements.length > 0) {
            console.error('Missing required chat elements:', missingElements);
            return;
        }

        this.isInitialized = true;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        if (!this.isInitialized) return;

        // Chat input events
        this.elements.chatInput.addEventListener('input', this.handleInputChange.bind(this));
        this.elements.chatInput.addEventListener('keydown', this.handleKeyDown.bind(this));

        // Send button
        this.elements.sendButton.addEventListener('click', this.sendMessage.bind(this));

        // Auto-resize textarea
        this.elements.chatInput.addEventListener('input', () => {
            autoResizeTextarea(this.elements.chatInput);
        });
    }

    /**
     * Setup state subscriptions
     */
    setupStateSubscriptions() {
        // Subscribe to loading state changes
        appState.subscribe('isLoading', (isLoading) => {
            this.updateSendButton(!isLoading);
        });

        // Subscribe to chat history changes
        appState.subscribe('chatHistory', (chatHistory) => {
            this.updateChatHistoryDisplay(chatHistory);
        });
    }

    /**
     * Handle input change events
     * @param {Event} event - Input event
     */
    handleInputChange(event) {
        const value = event.target.value;
        const length = value.length;
        
        // Update character count
        if (this.elements.charCount) {
            this.elements.charCount.textContent = length;
            
            // Add warning class if approaching limit
            if (length > APP_CONSTANTS.maxChatInputLength * 0.8) {
                this.elements.charCount.classList.add('warning');
            } else {
                this.elements.charCount.classList.remove('warning');
            }
        }

        // Update send button state
        this.updateSendButton(length > 0 && length <= APP_CONSTANTS.maxChatInputLength);
        
        // Update state
        appState.set('currentMessage', value);
    }

    /**
     * Handle key down events
     * @param {Event} event - Keyboard event
     */
    handleKeyDown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }

    /**
     * Send message
     */
    async sendMessage() {
        console.log('ChatComponent.sendMessage called');
        const message = this.elements.chatInput.value.trim();
        console.log('Message to send:', message);
        
        if (!message) {
            console.warn('Empty message, aborting');
            return;
        }

        try {
            console.log('Starting message processing...');
            // Clear input and update UI
            this.clearInput();

            // Remove welcome message if exists
            this.removeWelcomeMessage();

            // Add user message
            this.addMessage(message, 'user');

            // Show loading indicator (just the chat dots, not global loading)
            this.currentLoadingId = this.showChatLoading();

            console.log('Calling chatService.processMessage...');
            // Process message through chat service
            const response = await chatService.processMessage(message);
            console.log('Chat service response received:', response);

            // Hide loading indicator
            this.hideChatLoading();

            // Add bot response
            this.addMessage(response.answer, 'bot', response.metadata);

            // Update statistics
            statsService.updateStats(
                response.metadata.sources,
                response.metadata.responseTime * 1000, // Convert to milliseconds
                response.metadata.webSources,
                response.metadata.usedWebSearch
            );

        } catch (error) {
            console.error('ChatComponent.sendMessage error:', error);
            this.hideChatLoading();
            appState.addError(error);
            this.showError(`Error al comunicarse con el servidor: ${error.message}`);
        }
    }

    /**
     * Add message to chat
     * @param {string} content - Message content
     * @param {string} type - Message type ('user' or 'bot')
     * @param {Object} metadata - Message metadata
     */
    addMessage(content, type, metadata = {}) {
        if (!this.elements.chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';

        const avatar = document.createElement('div');
        avatar.className = `message-avatar ${type}`;
        avatar.innerHTML = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const messageContent = document.createElement('div');
        messageContent.className = `message-content ${type}`;
        messageContent.innerHTML = formatMessage(content);

        const messageWrapper = document.createElement('div');
        messageWrapper.className = `message-${type}`;

        if (type === 'user') {
            messageWrapper.appendChild(messageContent);
            messageWrapper.appendChild(avatar);
        } else {
            messageWrapper.appendChild(avatar);
            messageWrapper.appendChild(messageContent);

            // Add metadata for bot messages
            if (Object.keys(metadata).length > 0) {
                const metaDiv = document.createElement('div');
                metaDiv.className = 'message-meta';
                metaDiv.innerHTML = formatMessageMetadata(metadata);
                messageWrapper.appendChild(metaDiv);
            }
        }

        messageDiv.appendChild(messageWrapper);
        this.elements.chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        scrollToBottom(this.elements.chatMessages);

        // Add fade-in animation
        addFadeInAnimation(messageDiv);
    }

    /**
     * Show chat loading indicator
     * @returns {string} Loading ID
     */
    showChatLoading() {
        const loadingId = `loading-${Date.now()}`;
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        messageDiv.id = loadingId;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar bot';
        avatar.innerHTML = '<i class="fas fa-robot"></i>';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content bot loading-message';
        
        // Create typing indicator
        const typingIndicator = createTypingIndicator();
        
        const loadingText = document.createElement('span');
        loadingText.className = 'loading-text';
        loadingText.textContent = 'Pensando...';
        
        messageContent.appendChild(typingIndicator);
        messageContent.appendChild(loadingText);

        const messageWrapper = document.createElement('div');
        messageWrapper.className = 'message-bot';
        messageWrapper.appendChild(avatar);
        messageWrapper.appendChild(messageContent);

        messageDiv.appendChild(messageWrapper);
        this.elements.chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        scrollToBottom(this.elements.chatMessages);

        return loadingId;
    }

    /**
     * Hide chat loading indicator
     */
    hideChatLoading() {
        if (this.currentLoadingId) {
            const loadingElement = findElement(`#${this.currentLoadingId}`);
            if (loadingElement) {
                loadingElement.remove();
            }
            this.currentLoadingId = null;
        }
    }

    /**
     * Clear chat input
     */
    clearInput() {
        if (this.elements.chatInput) {
            this.elements.chatInput.value = '';
            if (this.elements.charCount) {
                this.elements.charCount.textContent = '0';
            }
            autoResizeTextarea(this.elements.chatInput);
            appState.set('currentMessage', '');
        }
    }

    /**
     * Update send button state
     * @param {boolean} enabled - Whether button should be enabled
     */
    updateSendButton(enabled) {
        if (this.elements.sendButton) {
            this.elements.sendButton.disabled = !enabled;
        }
    }

    /**
     * Remove welcome message
     */
    removeWelcomeMessage() {
        const welcomeMessage = this.elements.chatMessages?.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.animation = 'fadeOut 0.3s ease-out forwards';
            setTimeout(() => welcomeMessage.remove(), 300);
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        // This could be handled by a separate error component
        // For now, add error message to chat
        this.addMessage(`❌ ${message}`, 'bot');
    }

    /**
     * Load chat message from history
     * @param {string} chatId - Chat ID
     */
    loadChatFromHistory(chatId) {
        const chatHistory = appState.get('chatHistory');
        const chat = chatHistory.find(c => c.id.toString() === chatId.toString());
        
        if (chat && this.elements.chatInput) {
            this.elements.chatInput.value = chat.fullQuestion || chat.userMessage;
            this.handleInputChange({ target: this.elements.chatInput });
            autoResizeTextarea(this.elements.chatInput);
        }
    }

    /**
     * Update chat history display
     * @param {Array} chatHistory - Chat history array
     */
    updateChatHistoryDisplay(chatHistory) {
        const chatHistoryElement = findElement('#chatHistory');
        if (!chatHistoryElement) return;

        if (chatHistory.length === 0) {
            chatHistoryElement.innerHTML = `
                <div class="empty-history">
                    <i class="fas fa-comments"></i>
                    <p>No hay conversaciones anteriores</p>
                </div>
            `;
            return;
        }

        chatHistoryElement.innerHTML = chatHistory.map(chat => `
            <div class="history-item" onclick="chatComponent.loadChatFromHistory('${chat.id}')">
                <div class="history-question">${chat.question || chat.userMessage.substring(0, 50) + '...'}</div>
                <div class="history-date">${chat.date}</div>
            </div>
        `).join('');
    }

    /**
     * Clear chat messages
     */
    clearChatMessages() {
        if (this.elements.chatMessages) {
            this.elements.chatMessages.innerHTML = '';
        }
    }

    /**
     * Focus on input
     */
    focusInput() {
        if (this.elements.chatInput) {
            this.elements.chatInput.focus();
        }
    }

    /**
     * Set input value
     * @param {string} value - Input value
     */
    setInputValue(value) {
        if (this.elements.chatInput) {
            this.elements.chatInput.value = value;
            this.handleInputChange({ target: this.elements.chatInput });
        }
    }

    /**
     * Get input value
     * @returns {string} Current input value
     */
    getInputValue() {
        return this.elements.chatInput?.value || '';
    }

    /**
     * Enable/disable chat interface
     * @param {boolean} enabled - Whether interface should be enabled
     */
    setEnabled(enabled) {
        if (this.elements.chatInput) {
            this.elements.chatInput.disabled = !enabled;
        }
        if (this.elements.sendButton) {
            this.elements.sendButton.disabled = !enabled;
        }
    }

    /**
     * Destroy component and cleanup
     */
    destroy() {
        // Remove event listeners
        if (this.elements.chatInput) {
            this.elements.chatInput.removeEventListener('input', this.handleInputChange);
            this.elements.chatInput.removeEventListener('keydown', this.handleKeyDown);
        }
        if (this.elements.sendButton) {
            this.elements.sendButton.removeEventListener('click', this.sendMessage);
        }

        // Clear elements
        this.elements = {};
        this.isInitialized = false;
    }
}

// Export singleton instance
export const chatComponent = new ChatComponent();