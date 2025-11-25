// Функция для удаления товара через AJAX
async function deleteProduct(productId) {

    try {
        const response = await fetch(`/admin/delete_product/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            updateProductUI(productId, 'deleted');
            showNotification('Товар удален', 'success');
        } else {
            showNotification('Ошибка: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Ошибка удаления товара', 'error');
    }
}

// Функция для восстановления товара через AJAX
async function recoverProduct(productId) {

    try {
        const response = await fetch(`/admin/recover_product/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            updateProductUI(productId, 'recovered');
            showNotification('Товар восстановлен', 'success');
        } else {
            showNotification('Ошибка: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Ошибка восстановления товара', 'error');
    }
}

// Обновление интерфейса товара
function updateProductUI(productId, action) {
    const productCard = document.querySelector(`[data-product-id="${productId}"]`);
    const actionsContainer = productCard.querySelector('.card__actions');

    if (action === 'deleted') {
        // Меняем "Удалить" на "Восстановить"
        const deleteButton = actionsContainer.querySelector('.card__delete');
        if (deleteButton) {
            const recoverButton = document.createElement('button');
            recoverButton.className = 'card__recover';
            recoverButton.setAttribute('data-product-id', productId);
            recoverButton.textContent = 'Восстановить';
            recoverButton.addEventListener('click', function(e) {
                e.preventDefault();
                recoverProduct(productId);
            });

            deleteButton.replaceWith(recoverButton);
        }

    } else if (action === 'recovered') {
        // Меняем "Восстановить" на "Удалить"
        const recoverButton = actionsContainer.querySelector('.card__recover');
        if (recoverButton) {
            const deleteButton = document.createElement('button');
            deleteButton.className = 'card__delete';
            deleteButton.setAttribute('data-product-id', productId);
            deleteButton.textContent = 'Удалить';
            deleteButton.addEventListener('click', function(e) {
                e.preventDefault();
                deleteProduct(productId);
            });

            recoverButton.replaceWith(deleteButton);
        }
    }
}

// Показ уведомления
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        border-radius: 5px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Инициализация обработчиков
document.addEventListener('DOMContentLoaded', function() {
    // Обработчики для кнопок УДАЛЕНИЯ
    const deleteButtons = document.querySelectorAll('.card__delete');
    deleteButtons.forEach(button => {
        const productId = button.getAttribute('data-product-id');
        button.addEventListener('click', function(e) {
            e.preventDefault();
            deleteProduct(productId);
        });
    });

    // Обработчики для кнопок ВОССТАНОВЛЕНИЯ
    const recoverButtons = document.querySelectorAll('.card__recover');
    recoverButtons.forEach(button => {
        const productId = button.getAttribute('data-product-id');
        button.addEventListener('click', function(e) {
            e.preventDefault();
            recoverProduct(productId);
        });
    });
});