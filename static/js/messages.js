// Global variables
let currentBookingId = null;
let currentOtherUserId = null;
let currentBookingStatus = null;

// Load conversation list when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadConversations();
    // Refresh conversation list every 30 seconds
    setInterval(loadConversations, 30000);
});

// Load conversation list
async function loadConversations() {
    try {
        const response = await fetch('/messages/api/conversations');
        const conversations = await response.json();
        
        const conversationsList = document.getElementById('conversations-list');
        
        if (conversations.length === 0) {
            conversationsList.innerHTML = `
                <div class="text-center text-muted py-5">
                    <p>No conversations yet</p>
                    <small>Start by booking a babysitter or accepting a booking request</small>
                </div>
            `;
            return;
        }

        conversationsList.innerHTML = conversations.map(conv => {
            const lastMsg = conv.last_message;
            const timeAgo = lastMsg ? formatTimeAgo(new Date(lastMsg.created_at)) : 'No messages';
            const unreadBadge = conv.unread_count > 0 ? 
                `<span class="badge bg-primary rounded-pill">${conv.unread_count}</span>` : '';
            
            const statusColor = getStatusColor(conv.booking_status);
            
            return `
                <div class="conversation-item p-3 border-bottom ${currentBookingId === conv.booking_id ? 'bg-light' : ''}" 
                     style="cursor: pointer;"
                     onclick="loadConversation(${conv.booking_id})">
                    <div class="d-flex align-items-start">
                        <div class="avatar-circle bg-primary me-3" style="width:42px;height:42px;font-size:1.1rem;">
                            ${conv.other_user.username[0].toUpperCase()}
                        </div>
                        <div class="flex-grow-1 overflow-hidden">
                            <div class="d-flex justify-content-between align-items-start">
                                <h6 class="mb-0">${conv.other_user.username}</h6>
                                ${unreadBadge}
                            </div>
                            <small class="text-muted d-block">
                                <span class="badge ${statusColor} me-1">${conv.booking_status}</span>
                                ${conv.booking_date} ${conv.booking_time}
                            </small>
                            <p class="mb-0 text-muted small text-truncate">
                                ${lastMsg ? lastMsg.content : 'No messages yet'}
                            </p>
                            <small class="text-muted">${timeAgo}</small>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error loading conversations:', error);
        document.getElementById('conversations-list').innerHTML = `
            <div class="alert alert-danger">Failed to load conversations</div>
        `;
    }
}

// Load specific conversation
async function loadConversation(bookingId) {
    currentBookingId = bookingId;
    
    try {
        const response = await fetch(`/messages/api/conversation/${bookingId}`);
        const data = await response.json();
        
        currentOtherUserId = data.other_user.id;
        currentBookingStatus = data.booking.status;
        
        // Show conversation view
        document.getElementById('no-conversation-selected').classList.add('d-none');
        document.getElementById('conversation-view').classList.remove('d-none');
        
        // Update header info
        document.getElementById('other-user-initial').textContent = data.other_user.username[0].toUpperCase();
        document.getElementById('other-user-name').textContent = data.other_user.username;
        document.getElementById('booking-info').textContent = `${data.booking.date} ${data.booking.time}`;
        
        const statusBadge = document.getElementById('booking-status-badge');
        statusBadge.textContent = data.booking.status;
        statusBadge.className = `badge ${getStatusColor(data.booking.status)}`;
        
        // Show accept/reject buttons (only when status is pending and current user is babysitter)
        const bookingActions = document.getElementById('booking-actions');
        if (data.booking.status === 'pending') {
            // Since we already verify on backend, simply show buttons here
            bookingActions.classList.remove('d-none');
        } else {
            bookingActions.classList.add('d-none');
        }
        
        // Display messages
        displayMessages(data.messages);
        
        // Refresh conversation list to update unread count
        loadConversations();
        
    } catch (error) {
        console.error('Error loading conversation:', error);
        alert('Failed to load conversation');
    }
}

// Display message list
function displayMessages(messages) {
    const container = document.getElementById('messages-container');
    
    if (messages.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <p>No messages yet. Start the conversation!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = messages.map(msg => {
        const isCurrentUser = msg.sender_id !== currentOtherUserId;
        const alignment = isCurrentUser ? 'text-end' : 'text-start';
        const bgColor = isCurrentUser ? 'bg-primary text-white' : 'bg-light';
        const timeAgo = formatTimeAgo(new Date(msg.created_at));
        
        return `
            <div class="mb-3 ${alignment}">
                <div class="d-inline-block ${bgColor} rounded px-3 py-2" style="max-width: 70%;">
                    <div class="small fw-bold mb-1">${msg.sender_username}</div>
                    <div>${escapeHtml(msg.content)}</div>
                    <div class="small opacity-75 mt-1">${timeAgo}</div>
                </div>
            </div>
        `;
    }).join('');
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// Send message
document.getElementById('send-message-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    
    if (!content || !currentBookingId) return;
    
    try {
        const response = await fetch('/messages/api/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                booking_id: currentBookingId,
                content: content
            })
        });
        
        if (response.ok) {
            input.value = '';
            // Reload conversation
            loadConversation(currentBookingId);
        } else {
            alert('Failed to send message');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        alert('Failed to send message');
    }
});

// Update booking status
async function updateBookingStatus(status) {
    if (!currentBookingId) return;
    
    if (!confirm(`Are you sure you want to ${status} this booking?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/messages/api/booking/${currentBookingId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: status })
        });
        
        if (response.ok) {
            // Reload conversation
            loadConversation(currentBookingId);
            loadConversations();
        } else {
            alert('Failed to update booking status');
        }
    } catch (error) {
        console.error('Error updating booking status:', error);
        alert('Failed to update booking status');
    }
}

// Utility function: Format time
function formatTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
}

// Utility function: Get status color
function getStatusColor(status) {
    const colors = {
        'pending': 'bg-warning',
        'accepted': 'bg-success',
        'rejected': 'bg-danger',
        'completed': 'bg-secondary'
    };
    return colors[status] || 'bg-secondary';
}

// Utility function: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
