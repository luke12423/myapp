function makeAdmin(userId) {
    if (!confirm('Назначить этого пользователя администратором?')) {
        return;
    }

    fetch(`/admin/users/make_admin/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Обновляем интерфейс
            const badge = document.getElementById(`admin-badge-${userId}`);
            const button = document.getElementById(`admin-btn-${userId}`);
            updateStats();

            badge.className = 'badge badge-admin ms-2';
            badge.textContent = 'АДМИН';


            button.className = 'btn btn-warning btn-sm me-2';
            button.innerHTML = '<i class="fas fa-user-times me-1"></i>Снять админа';
            button.onclick = () => removeAdmin(userId);

            showNotification(data.message, 'success');

        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка сети', 'error');
    });
}

// Снять права администратора
function removeAdmin(userId) {
    if (!confirm('Снять права администратора с этого пользователя?')) {
        return;
    }

    fetch(`/admin/users/remove_admin/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Обновляем интерфейс
            const badge = document.getElementById(`admin-badge-${userId}`);
            const button = document.getElementById(`admin-btn-${userId}`);
            updateStats();
            badge.className = 'badge badge-user ms-2';
            badge.textContent = 'ПОЛЬЗОВАТЕЛЬ';

            button.className = 'btn btn-success btn-sm me-2';
            button.innerHTML = '<i class="fas fa-user-shield me-1"></i>Сделать админом';
            button.onclick = () => makeAdmin(userId);

            showNotification(data.message, 'success');
            updateStats();
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка сети', 'error');
    });
}
// Обновление статистики
function updateStats() {
    // Перезагружаем страницу для обновления статистики
    setTimeout(() => {
        window.location.reload();
    }, 500);
}
        // Фильтрация и поиск
        document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('searchInput');
            const filterButtons = document.querySelectorAll('[data-filter]');
            const userItems = document.querySelectorAll('.user-item');

            // Поиск
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();

                userItems.forEach(item => {
                    const searchData = item.getAttribute('data-search');
                    if (searchData.includes(searchTerm)) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });

            // Фильтры
            filterButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const filter = this.getAttribute('data-filter');

                    // Активная кнопка
                    filterButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');

                    // Применяем фильтр
                    userItems.forEach(item => {
                        const userType = item.getAttribute('data-user-type');
                        const hasCart = item.getAttribute('data-has-cart');

                        let show = false;

                        switch(filter) {
                            case 'all':
                                show = true;
                                break;
                            case 'admin':
                                show = userType === 'admin';
                                break;
                            case 'user':
                                show = userType === 'user';
                                break;
                            case 'with-cart':
                                show = hasCart === 'true';
                                break;
                        }

                        item.style.display = show ? 'block' : 'none';
                    });
                });
            });

            // Модальное окно удаления
            const deleteModal = document.getElementById('deleteModal');
            deleteModal.addEventListener('show.bs.modal', function(event) {
                const button = event.relatedTarget;
                const userId = button.getAttribute('data-user-id');
                const userName = button.getAttribute('data-user-name');

                document.getElementById('userNameToDelete').textContent = userName;
                document.getElementById('userIdToDelete').value = userId;

                // Обновляем action формы
                const form = document.getElementById('deleteUserForm');
                form.action = `/admin/delete_user/${userId}`;
            });

            // Подтверждение удаления
            document.getElementById('deleteUserForm').addEventListener('submit', function(e) {
                if (!confirm('Вы уверены, что хотите удалить этого пользователя? Это действие нельзя отменить.')) {
                    e.preventDefault();
                }
            });
        });