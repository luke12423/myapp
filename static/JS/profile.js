document.addEventListener('DOMContentLoaded', function() {
        const navButtons = document.querySelectorAll('.nav-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        const editForm = document.querySelector('.edit-form');

        // Функция для активации вкладки
        function activateTab(tabName) {
            // Убираем активный класс у всех кнопок и вкладок
            navButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(tab => tab.classList.remove('active'));

            // Добавляем активный класс выбранной вкладке
            const targetBtn = document.querySelector(`[data-tab="${tabName}"]`);
            const targetTab = document.getElementById(tabName);

            if (targetBtn && targetTab) {
                targetBtn.classList.add('active');
                targetTab.classList.add('active');
            }
        }

        // Проверяем URL хэш при загрузке страницы
        const hash = window.location.hash.substring(1); // Убираем #
        if (hash === 'edit') {
            activateTab('edit');
        }

    // Переключение вкладок через кнопки
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            activateTab(targetTab);
        });
    });

        // Валидация формы
        if (editForm) {
            editForm.addEventListener('submit', function(e) {
                const currentPassword = document.getElementById('current_password').value;
                const newPassword = document.getElementById('new_password').value;
                const confirmPassword = document.getElementById('confirm_password').value;

                let hasErrors = false;

                // Проверяем, есть ли изменения
                const name = document.getElementById('name').value;
                const email = document.getElementById('email').value;
                const username = document.getElementById('username').value;

                const hasChanges = (
                    name !== editForm.dataset.originalName ||
                    email !== editForm.dataset.originalEmail ||
                    username !== editForm.dataset.originalUsername ||
                    newPassword.length > 0
                );

                if (!hasChanges) {
                    e.preventDefault();
                    showError('Нет изменений для сохранения!'); // Простое предупреждение
                    hasErrors = true;
                    return;
                }

                // Если есть изменения, но не введен текущий пароль
                if (hasChanges && !currentPassword) {
                    e.preventDefault();
                    showError('Для сохранения изменений необходимо ввести текущий пароль');
                    hasErrors = true;
                    return;
                }

                // Проверяем совпадение новых паролей
                if (newPassword && newPassword !== confirmPassword) {
                    e.preventDefault();
                    showError('Новые пароли не совпадают');
                    hasErrors = true;
                    return;
                }


                // Если ошибок нет, форма отправится
                if (!hasErrors) {
                    // Показываем индикатор загрузки
                    const submitBtn = document.querySelector('.save-btn');
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Сохранение...';
                }
            });

            // Функция показа ошибки
            function showError(message) {
                // Удаляем старые сообщения об ошибках
                const oldAlerts = document.querySelectorAll('.alert-dynamic');
                oldAlerts.forEach(alert => alert.remove());

                // Создаем новое сообщение об ошибке
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-error alert-dynamic';
                errorDiv.textContent = message;

                // Вставляем перед формой
                editForm.parentNode.insertBefore(errorDiv, editForm);

                // Прокручиваем к ошибке
                errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }

            // Очистка ошибок при изменении полей
            const formInputs = editForm.querySelectorAll('input');
            formInputs.forEach(input => {
                input.addEventListener('input', function() {
                    const oldAlerts = document.querySelectorAll('.alert-dynamic');
                    oldAlerts.forEach(alert => alert.remove());
                });
            });
        }
    });