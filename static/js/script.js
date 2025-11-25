document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const topMenu = document.getElementById('top-menu');
    const menuItems = document.querySelectorAll('#top-menu .menu-item');

    // Toggle mobile menu
    menuToggle.addEventListener('click', function() {
        topMenu.classList.toggle('active');
    });

    // Toggle dropdowns in mobile menu
    menuItems.forEach(item => {
        item.addEventListener('click', function(event) {
            // Verifica se o menu mobile está visível antes de interceptar o clique
            const isMobileMenuVisible = menuToggle.offsetParent !== null;

            if (isMobileMenuVisible && this.querySelector('.dropdown')) {
                // Impede que o link seja seguido, para apenas abrir/fechar o dropdown
                event.preventDefault();
                this.classList.toggle('active'); // Adiciona/remove a classe para mostrar/esconder o submenu
            }
        });
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!topMenu.contains(event.target) && !menuToggle.contains(event.target)) {
            topMenu.classList.remove('active');
            menuItems.forEach(item => item.classList.remove('active')); // Close all dropdowns
        }
    });
});