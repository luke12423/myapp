    // Функция для добавления в корзину через AJAX
async function addToCart(productId) {

    try {
        const response = await fetch(`/add_to_cart/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            // Находим кнопку по data-атрибуту
            const button = document.querySelector(`[data-product-id="${productId}"]`);

            if (button) {
                // Заменяем кнопку на "В корзине"
                const newButton = document.createElement('button');
                newButton.className = 'added-to-cart-btn';
                newButton.disabled = true;
                newButton.textContent = 'В корзине';
                button.parentNode.replaceChild(newButton, button);
            }

            // Обновляем счетчик корзины
            updateCartCount(data.cart_count);

            // Показываем уведомление
            showNotification('Товар добавлен в корзину', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Ошибка добавления в корзину', 'error');
    }
}

// Обновление счетчика корзины
function updateCartCount(count) {
    const cartCounter = document.querySelector('.cart-counter');
    if (cartCounter) {
        cartCounter.textContent = count;
    } else if (count > 0) {
        // Создаем счетчик если его нет
        const cartLink = document.querySelector('.nav-cart-simple');
        if (cartLink) {
            cartLink.innerHTML = `🛒 Корзина <span class="cart-counter">${count}</span>`;
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

    const cartButtons = document.querySelectorAll('.add-to-cart-btn');

    cartButtons.forEach(button => {
        const productId = button.getAttribute('data-product-id');

        button.addEventListener('click', function(e) {
            e.preventDefault();
            addToCart(productId);
        });
    });
});