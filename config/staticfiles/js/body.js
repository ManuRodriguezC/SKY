function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const texts = document.querySelectorAll('.sidebar-text');

    sidebar.classList.toggle('w-64');
    sidebar.classList.toggle('w-20');

    texts.forEach(el => {
        el.classList.toggle('hidden');
    });
}



function toggleUsersMenu() {
    const usersMenuBtn = document.getElementById('users-menu-btn');
    const usersMenu = document.getElementById('users-menu');
    const usersMenuIcon = document.getElementById('users-menu-icon');
    
    if (usersMenu.classList.contains('hidden')) {
        usersMenu.classList.remove('hidden');
        usersMenu.classList.add('flex');

        usersMenuIcon.classList.add('rotate-180');
    } else {
        usersMenu.classList.remove('flex');
        usersMenu.classList.add('hidden');

        usersMenuIcon.classList.remove('rotate-180');
    }
}
