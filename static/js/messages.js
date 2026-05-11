/**
 * Messages Interface - Enhanced messaging functionality for SitBuddy
 * Handles real-time messaging between parents and babysitters
 */

// Global state variables
let currentBookingId = null;
let currentOtherUserId = null;
let currentBookingStatus = null;
let currentUserRole = null;
let isLoading = false;
let confirmationModal = null;

/**
 * Get CSRF token from meta tag for secure API requests
 * @returns {string} CSRF token
 */
function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

/**
 * Initialize the messaging interface when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap modal
    const modalElement = document.getElementById('confirmationModal');
    if (modalElement) {
        confirmationModal = new bootstrap.Modal(modalElement);
    }
    
    // Setup auto-resize textarea and keyboard shortcuts
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('input', autoResizeTextarea);
        messageInput.addEventListener('keydown', handleEnterKey);
    }
    
    // Load initial conversations and setup refresh interval
    loadConversations();
    setInterval(loadConversations, 30000); // Refresh every 30 seconds
    
    // Check for user_id parameter to auto-open conversation
    checkForAutoOpenConversation();
});

/**
 * Auto-resize textarea based on content
 */
function autoResizeTextarea() {
    const textarea = document.getElementById('message-input');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

/**
 * Handle Enter key for sending messages (Shift+Enter for new line)
 * @param {KeyboardEvent} e - Keyboard event
 */
function handleEnterKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('send-message-form').dispatchEvent(new Event('submit'));
    }
}

/**
 * Load and display all conversations for the current user
 */
async function loadConversations() {
    if (isLoading) return;
    
    try {
        isLoading = true;
        const response = await fetch('/messages/api/conversations');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const conversations = await response.json();
        const conversationsList = document.getElementById('conversations-list');
        
        if (conversations.length === 0) {
            conversationsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <div class="empty-state-title">No conversations yet</div>
                    <div class="empty-state-text">Start by booking a babysitter or accepting a booking request</div>
                </div>
            `;
            return;
        }

        conversationsList.innerHTML = conversations.map(conv => {
            const lastMsg = conv.last_message;
            const timeAgo = lastMsg ? formatTimeAgo(new Date(lastMsg.created_at)) : 'No messages';
            const unreadBadge = conv.unread_count > 0 ? 
                `<div class="unread-badge">${conv.unread_count}</div>` : '';
            
            const statusClass = getStatusClass(conv.booking_status);
            const isActive = currentBookingId === conv.booking_id ? 'active' : '';
            
            return `
                <div class="conversation-item ${isActive}" onclick="loadConversation(${conv.booking_id})">
                    <div class="p-3 d-flex align-items-start">
                        <div class="conversation-avatar bg-primary me-3">
                            ${conv.other_user.name[0].toUpperCase()}
                        </div>
                        <div class="conversation-content">
                            <div class="d-flex justify-content-between align-items-start mb-1">
                                <div class="conversation-name">${escapeHtml(conv.other_user.name)}</div>
                                ${unreadBadge}
                            </div>
                            <div class="conversation-meta mb-2">
                                <span class="status-badge ${statusClass}">${conv.booking_status}</span>
                                <span class="ms-2">${conv.booking_date} ${conv.booking_time}</span>
                            </div>
                            <div class="conversation-preview">
                                ${lastMsg ? escapeHtml(lastMsg.content) : 'No messages yet'}
                            </div>
                            <div class="conversation-meta mt-1">${timeAgo}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Update navbar unread badge
        updateNavbarUnreadBadge(conversations);
        
        // Check if we need to auto-open a conversation with specific user
        autoOpenConversationWithUser(conversations);
        
    } catch (error) {
        console.error('Error loading conversations:', error);
        const conversationsList = document.getElementById('conversations-list');
        if (conversationsList) {
            conversationsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <div class="empty-state-title">Failed to load conversations</div>
                    <div class="empty-state-text">Please check your connection and try again</div>
                    <button class="btn btn-primary btn-sm mt-2" onclick="loadConversations()">Retry</button>
                </div>
            `;
        }
    } finally {
        isLoading = false;
    }
}

// Refresh only messages without reloading entire conversation
async function refreshMessages() {
    if (!currentBookingId) return;
    
    try {
        const response = await fetch(`/messages/api/conversation/${currentBookingId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Only update messages, keep other UI elements unchanged
        displayMessages(data.messages);
        
        // Also refresh conversation list to update unread counts
        loadConversations();
        
    } catch (error) {
        console.error('Error refreshing messages:', error);
    }
}

// Load specific conversation with enhanced role-specific UI
async function loadConversation(bookingId, forceReload = false) {
    if (currentBookingId === bookingId && !forceReload) return; // Already loaded
    
    currentBookingId = bookingId;
    
    try {
        showLoadingState();
        
        const response = await fetch(`/messages/api/conversation/${bookingId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        currentOtherUserId = data.other_user.id;
        currentBookingStatus = data.booking.status;
        currentUserRole = data.user_role; // This should be added to the API response
        
        // Show conversation view
        document.getElementById('no-conversation-selected').classList.add('d-none');
        document.getElementById('conversation-view').classList.remove('d-none');
        
        // Update header info with enhanced styling
        document.getElementById('other-user-initial').textContent = data.other_user.name[0].toUpperCase();
        document.getElementById('other-user-name').textContent = data.other_user.name;
        document.getElementById('booking-info').textContent = `${data.booking.date} ${data.booking.time}`;
        
        const statusBadge = document.getElementById('booking-status-badge');
        statusBadge.textContent = data.booking.status.toUpperCase();
        statusBadge.className = `status-badge ${getStatusClass(data.booking.status)}`;
        
        // Show role-specific UI
        setupRoleSpecificUI(data);
        
        // Display messages with enhanced formatting
        displayMessages(data.messages);
        
        // Update conversation list to show active state (but don't reload if we're already loading)
        if (!isLoading) {
            loadConversations();
        }
        
        // Clear loading state after content is loaded
        hideLoadingState();
        
    } catch (error) {
        console.error('Error loading conversation:', error);
        showErrorMessage('Failed to load conversation. Please try again.');
        hideLoadingState();
    }
}

// Setup role-specific UI elements
function setupRoleSpecificUI(data) {
    const parentView = document.getElementById('parent-view');
    const babysitterActions = document.getElementById('babysitter-actions');
    const parentStatusText = document.getElementById('parent-status-text');
    
    // Hide both initially
    parentView.classList.add('d-none');
    babysitterActions.classList.add('d-none');
    
    // Determine user role from the data
    const isParent = data.is_parent; // This should be added to the API response
    
    if (isParent) {
        // Parent view - read-only with status information
        parentView.classList.remove('d-none');
        
        const statusMessages = {
            'pending': 'Waiting for babysitter response',
            'accepted': 'Booking confirmed!',
            'rejected': 'Booking declined',
            'completed': 'Booking completed'
        };
        
        parentStatusText.textContent = statusMessages[data.booking.status] || data.booking.status;
        
    } else {
        // Babysitter view - show action buttons for pending requests
        if (data.booking.status === 'pending') {
            babysitterActions.classList.remove('d-none');
            
            // Enable/disable buttons based on current state
            const acceptBtn = document.getElementById('accept-btn');
            const rejectBtn = document.getElementById('reject-btn');
            const pendingBtn = document.getElementById('pending-btn');
            
            acceptBtn.disabled = false;
            rejectBtn.disabled = false;
            pendingBtn.disabled = false;
        }
    }
}

// Display message list with enhanced styling and system messages
function displayMessages(messages) {
    const container = document.getElementById('messages-container');
    
    if (messages.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <div class="empty-state-title">No messages yet</div>
                <div class="empty-state-text">Start the conversation!</div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = messages.map(msg => {
        const isCurrentUser = msg.sender_id !== currentOtherUserId;
        const isSystemMessage = msg.is_system || msg.content.includes('Booking has been');
        
        if (isSystemMessage) {
            return createSystemMessage(msg);
        }
        
        return createUserMessage(msg, isCurrentUser);
    }).join('');
    
    // Scroll to bottom smoothly
    container.scrollTop = container.scrollHeight;
}

// Create system message HTML
function createSystemMessage(msg) {
    const timeAgo = formatTimeAgo(new Date(msg.created_at));
    
    return `
        <div class="message-bubble message-system">
            <div class="message-content">
                <strong>System:</strong> ${escapeHtml(msg.content)}
            </div>
            <div class="message-time">${timeAgo}</div>
        </div>
    `;
}

// Create user message HTML
function createUserMessage(msg, isCurrentUser) {
    const messageClass = isCurrentUser ? 'message-sent' : 'message-received';
    const timeAgo = formatTimeAgo(new Date(msg.created_at));
    
    return `
        <div class="message-bubble ${messageClass}">
            <div class="message-header">${escapeHtml(msg.sender_name)}</div>
            <div class="message-content">${escapeHtml(msg.content)}</div>
            <div class="message-time">${timeAgo}</div>
        </div>
    `;
}

// Enhanced send message with loading states
document.getElementById('send-message-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const content = input.value.trim();
    
    if (!content || !currentBookingId || isLoading) return;
    
    try {
        isLoading = true;
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<div class="loading-spinner"></div>';
        
        // Optimistic update - show message immediately
        const tempMessage = {
            id: 'temp-' + Date.now(),
            sender_id: 'current-user', // Will be treated as current user
            sender_name: 'You',
            content: content,
            created_at: new Date().toISOString(),
            is_system: false
        };
        
        // Add temporary message to display
        addMessageToDisplay(tempMessage);
        
        // Clear input immediately for better UX
        input.value = '';
        input.style.height = 'auto';
        
        const response = await fetch('/messages/api/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                booking_id: currentBookingId,
                content: content
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Refresh messages to get the real message from server
        await refreshMessages();
        
    } catch (error) {
        console.error('Error sending message:', error);
        showErrorMessage('Failed to send message. Please try again.');
        // Refresh to remove temporary message on error
        await refreshMessages();
    } finally {
        isLoading = false;
        sendBtn.disabled = false;
        sendBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576zm6.787-8.201L1.591 6.602l4.339 2.76z"/>
            </svg>
        `;
    }
});

// Add a single message to the display (for optimistic updates)
function addMessageToDisplay(message) {
    const container = document.getElementById('messages-container');
    const isCurrentUser = message.sender_id === 'current-user' || message.sender_id !== currentOtherUserId;
    const isSystemMessage = message.is_system;
    
    let messageHtml;
    if (isSystemMessage) {
        messageHtml = createSystemMessage(message);
    } else {
        messageHtml = createUserMessage(message, isCurrentUser);
    }
    
    container.insertAdjacentHTML('beforeend', messageHtml);
    container.scrollTop = container.scrollHeight;
}

// Enhanced booking status update with confirmation
async function updateBookingStatus(status) {
    if (!currentBookingId || isLoading) return;
    
    const statusMessages = {
        'accepted': {
            title: 'Accept Booking',
            message: 'Are you sure you want to accept this booking request? This will confirm your availability for the requested time.',
            confirmText: 'Accept Booking',
            confirmClass: 'btn-success'
        },
        'rejected': {
            title: 'Reject Booking',
            message: 'Are you sure you want to reject this booking request? The parent will be notified of your decision.',
            confirmText: 'Reject Booking',
            confirmClass: 'btn-danger'
        }
    };
    
    const config = statusMessages[status];
    if (!config) return;
    
    // Show confirmation modal
    document.getElementById('confirmationModalLabel').textContent = config.title;
    document.getElementById('confirmationModalBody').textContent = config.message;
    
    const confirmBtn = document.getElementById('confirmActionBtn');
    confirmBtn.textContent = config.confirmText;
    confirmBtn.className = `btn ${config.confirmClass}`;
    
    // Set up confirmation handler
    confirmBtn.onclick = () => performStatusUpdate(status);
    
    confirmationModal.show();
}

// Perform the actual status update
async function performStatusUpdate(status) {
    try {
        isLoading = true;
        confirmationModal.hide();
        
        // Show loading state on all action buttons
        const buttons = document.querySelectorAll('.action-btn');
        buttons.forEach(btn => {
            btn.disabled = true;
            if (!btn.dataset.originalText) {
                btn.dataset.originalText = btn.textContent;
            }
            btn.innerHTML = '<div class="loading-spinner"></div> Processing...';
        });
        
        const response = await fetch(`/messages/api/booking/${currentBookingId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ status: status })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        await response.json(); // Consume response but don't store unused result
        
        // Update current booking status
        currentBookingStatus = status;
        
        // Show success message
        showSuccessMessage(`Booking ${status} successfully!`);
        
        // Update UI to show only the selected action
        updateButtonsAfterStatusChange(status);
        
        // Update navbar pending bookings badge (if function exists from navbar-unread.js)
        if (typeof updateNavbarPendingCount === 'function') {
            updateNavbarPendingCount();
        }
        
        // Refresh messages to show the system message (but don't reload entire conversation)
        setTimeout(async () => {
            await refreshMessages();
        }, 500); // Small delay to ensure server has processed the status change
        
    } catch (error) {
        console.error('Error updating booking status:', error);
        showErrorMessage(`Failed to ${status} booking. Please try again.`);
        
        // Re-enable buttons on error
        const buttons = document.querySelectorAll('.action-btn');
        buttons.forEach(btn => {
            btn.disabled = false;
            btn.innerHTML = btn.dataset.originalText || btn.textContent;
        });
    } finally {
        isLoading = false;
    }
}

// Update button display after status change
function updateButtonsAfterStatusChange(newStatus) {
    const babysitterActions = document.getElementById('babysitter-actions');
    
    if (newStatus === 'accepted') {
        // Show only accepted state
        babysitterActions.innerHTML = `
            <div class="alert alert-success mb-0">
                <strong>✅ Booking Accepted</strong><br>
                You have accepted this booking request. The parent has been notified.
            </div>
        `;
    } else if (newStatus === 'rejected') {
        // Show only rejected state
        babysitterActions.innerHTML = `
            <div class="alert alert-danger mb-0">
                <strong>❌ Booking Rejected</strong><br>
                You have declined this booking request. The parent has been notified.
            </div>
        `;
    }
    
    // Update the status badge in the header
    const statusBadge = document.getElementById('booking-status-badge');
    if (statusBadge) {
        statusBadge.textContent = newStatus.toUpperCase();
        statusBadge.className = `status-badge ${getStatusClass(newStatus)}`;
    }
}

// Keep pending function (new feature)
function keepPending() {
    showSuccessMessage('Booking kept as pending. You can decide later.');
    
    // Hide action buttons temporarily
    document.getElementById('babysitter-actions').classList.add('d-none');
    
    // Show them again after 3 seconds
    setTimeout(() => {
        document.getElementById('babysitter-actions').classList.remove('d-none');
    }, 3000);
}

// Utility functions
function formatTimeAgo(date) {
    // Ensure we're working with a proper Date object
    // If date is a string (ISO format), convert it properly
    let messageDate;
    if (typeof date === 'string') {
        // Handle ISO string from server (should be UTC time)
        // JavaScript Date constructor automatically converts UTC to local time
        messageDate = new Date(date);
    } else {
        messageDate = date;
    }
    
    const now = new Date();
    const diffMs = now - messageDate;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    // For older messages, show local date and time
    return messageDate.toLocaleString();
}

function getStatusClass(status) {
    const classes = {
        'pending': 'pending',
        'accepted': 'accepted',
        'rejected': 'rejected',
        'completed': 'completed'
    };
    return classes[status] || 'pending';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoadingState() {
    const container = document.getElementById('messages-container');
    container.innerHTML = `
        <div class="empty-state">
            <div class="loading-spinner"></div>
            <div class="empty-state-title mt-3">Loading messages...</div>
        </div>
    `;
}

function hideLoadingState() {
    // Simply remove loading state - don't trigger additional loads
    // The calling function will handle content updates
    const container = document.getElementById('messages-container');
    
    // Only clear loading if container currently shows loading
    const loadingElement = container.querySelector('.loading-spinner');
    if (loadingElement) {
        // If no conversation is selected, show the default state
        if (!currentBookingId) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">💬</div>
                    <div class="empty-state-title">Select a conversation</div>
                    <div class="empty-state-text">Choose a conversation from the left to start messaging</div>
                </div>
            `;
        }
        // If conversation is selected, the calling function will populate content
    }
}

function showErrorMessage(message) {
    // Create a temporary toast notification
    const toast = document.createElement('div');
    toast.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

function showSuccessMessage(message) {
    // Create a temporary toast notification
    const toast = document.createElement('div');
    toast.className = 'alert alert-success alert-dismissible fade show position-fixed';
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

/**
 * Update the navbar unread message badge (local version for messages page)
 * @param {Array} conversations - Array of conversation objects
 */
function updateNavbarUnreadBadge(conversations) {
    const navbarBadge = document.getElementById('navbar-unread-badge');
    if (!navbarBadge) return; // Badge element doesn't exist
    
    // Calculate total unread messages across all conversations
    const totalUnread = conversations.reduce((total, conv) => total + (conv.unread_count || 0), 0);
    
    if (totalUnread > 0) {
        navbarBadge.textContent = totalUnread > 99 ? '99+' : totalUnread.toString();
        navbarBadge.classList.remove('d-none');
    } else {
        navbarBadge.classList.add('d-none');
    }
}

/**
 * Check URL parameters for auto-opening conversations
 */
function checkForAutoOpenConversation() {
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id');
    
    if (userId) {
        // Store the target user ID to open conversation once conversations are loaded
        window.targetUserId = parseInt(userId);
        
        // Clean up URL without refreshing page
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
    }
}

/**
 * Auto-open conversation with specific user (called after conversations are loaded)
 * @param {Array} conversations - Array of conversation objects
 */
function autoOpenConversationWithUser(conversations) {
    if (!window.targetUserId) return;
    
    // Find conversation with the target user
    const targetConversation = conversations.find(conv => 
        conv.other_user.id === window.targetUserId
    );
    
    if (targetConversation) {
        // Open the conversation
        loadConversation(targetConversation.booking_id);
        // Clear the target user ID
        window.targetUserId = null;
    } else {
        // Show message if no conversation exists with this user
        showErrorMessage('No conversation found with this user. You may need to create a booking first.');
        window.targetUserId = null;
    }
}
