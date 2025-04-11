document.addEventListener('DOMContentLoaded', function() {
    const sidebarPlaceholder = document.getElementById('sidebar-placeholder');
    const sidebarPath = '../common/sidebar.html'; // Adjusted path relative to files in subdirectories

    if (sidebarPlaceholder) {
        fetch(sidebarPath)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(data => {
                sidebarPlaceholder.innerHTML = data;
                highlightCurrentLink();
            })
            .catch(error => {
                console.error('Error loading sidebar:', error);
                sidebarPlaceholder.innerHTML = '<p class="text-red-500 p-4">Error loading sidebar.</p>';
            });
    }
});

function highlightCurrentLink() {
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('#sidebar-placeholder .sidebar-link');

    sidebarLinks.forEach(link => {
        const linkPath = link.getAttribute('href');

        // Normalize paths for comparison (remove ../ and ensure consistency)
        // This basic normalization works for the current structure.
        // More complex routing might need a more robust solution.
        const cleanLinkPath = linkPath.startsWith('../') ? linkPath.substring(2) : linkPath;
        const cleanCurrentPath = currentPath.substring(currentPath.indexOf('/web/') + 4); // Get path relative to /web/

        // Check if the cleaned current path ends with the cleaned link path
        if (cleanCurrentPath.endsWith(cleanLinkPath)) {
            link.classList.add('active');
        }
         // Special case for strategy detail page highlighting the parent '选股策略' link
        else if (cleanCurrentPath.includes('/strategies/strategy_detail.html') && cleanLinkPath.endsWith('/strategies/stock_selection_strategies.html')) {
             link.classList.add('active');
        }
        // Special case for edit model page highlighting the parent '选股策略' link (assuming models relate to strategies for now)
        else if (cleanCurrentPath.includes('/models/edit_model.html') && cleanLinkPath.endsWith('/strategies/stock_selection_strategies.html')) {
             link.classList.add('active');
        }
         // Add more special cases if needed (e.g., settings, login)
         else if (cleanCurrentPath.includes('/common/settings.html') && cleanLinkPath.endsWith('/common/settings.html')) {
              link.classList.add('active');
         }
         else if (cleanCurrentPath.includes('/common/login.html') && cleanLinkPath.endsWith('/common/login.html')) {
              // Technically login might not have the sidebar, but included for completeness if it did
              link.classList.add('active');
         }
    });
} 