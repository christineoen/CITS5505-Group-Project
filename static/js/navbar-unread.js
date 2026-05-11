/**
 * Global navbar badge counters
 * This script runs on all pages to show unread message count and pending bookings count in navbar
 */

/**
 * Update navbar unread messages badge from any page
 */
async function updateNavbarUnreadCount() {
    const navbarBadge = document.getElementById('navbar-unread-badge');
    if (!navbarBadge) return; // Badge element doesn't exist (not logged in)
    
    try {
        const response = await fetch('/messages/api/conversations');
        if (!response.ok) return; // Silently fail if API is not available
        
        const conversations = await response.json();
        
        // Calculate total unread messages across all conversations
        const totalUnread = conversations.reduce((total, conv) => total + (conv.unread_count || 0), 0);
        
        if (totalUnread > 0) {
            navbarBadge.textContent = totalUnread > 99 ? '99+' : totalUnread.toString();
            navbarBadge.classList.remove('d-none');
        } else {
            navbarBadge.classList.add('d-none');
        }
    } catch (error) {
        // Silently fail - don't show errors for this background feature
        console.debug('Could not update navbar unread count:', error);
    }
}

/**
 * Update navbar pending bookings badge from any page
 */
async function updateNavbarPendingCount() {
    const navbarBadge = document.getElementById('navbar-pending-badge');
    if (!navbarBadge) return; // Badge element doesn't exist (not logged in)
    
    try {
        const response = await fetch('/api/pending-bookings-count');
        if (!response.ok) return; // Silently fail if API is not available
        
        const data = await response.json();
        const pendingCount = data.count || 0;
        
        if (pendingCount > 0) {
            navbarBadge.textContent = pendingCount > 99 ? '99+' : pendingCount.toString();
            navbarBadge.classList.remove('d-none');
        } else {
            navbarBadge.classList.add('d-none');
        }
    } catch (error) {
        // Silently fail - don't show errors for this background feature
        console.debug('Could not update navbar pending count:', error);
    }
}

/**
 * Update all navbar badges
 */
async function updateAllNavbarBadges() {
    await Promise.all([
        updateNavbarUnreadCount(),
        updateNavbarPendingCount()
    ]);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Only run if user is logged in (navbar badges exist)
    if (document.getElementById('navbar-unread-badge') || document.getElementById('navbar-pending-badge')) {
        updateAllNavbarBadges();
        
        // Update every 60 seconds
        setInterval(updateAllNavbarBadges, 60000);
    }
});