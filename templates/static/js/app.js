function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('show');
    document.getElementById('sidebarOverlay').classList.toggle('show');
}

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts
    setTimeout(function () {
        document.querySelectorAll('.alert-dismissible').forEach(function (el) {
            try { bootstrap.Alert.getOrCreateInstance(el).close(); } catch (e) {}
        });
    }, 4500);

    // Meal selection highlight
    document.querySelectorAll('.meal-checkbox').forEach(function (cb) {
        cb.addEventListener('change', function () {
            var card = this.closest('.meal-card');
            if (card) card.classList.toggle('selected', this.checked);
        });
    });

    // Close sidebar on nav click (mobile)
    document.querySelectorAll('.sidebar-nav a').forEach(function (link) {
        link.addEventListener('click', function () {
            if (window.innerWidth < 992) {
                document.getElementById('sidebar').classList.remove('show');
                document.getElementById('sidebarOverlay').classList.remove('show');
            }
        });
    });
});
