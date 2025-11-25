document.querySelectorAll('.quantity-input').forEach(input => {
    input.addEventListener('change', function() {
        const itemId = this.dataset.itemId;
        const quantity = this.value;

        fetch(`/update_cart/${itemId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `quantity=${quantity}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    });
});

// Оформление заказа
document.getElementById('checkoutForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const checkoutBtn = document.getElementById('checkoutBtn');
    const originalText = checkoutBtn.innerHTML;

    // Показываем загрузку
    checkoutBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Оформление...';
    checkoutBtn.disabled = true;

    const formData = new FormData();
    formData.append('shipping_address', document.getElementById('shipping_address').value);
    formData.append('phone', document.getElementById('phone').value);
    formData.append('email', document.getElementById('email').value);

    fetch('/create_order', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Заказ успешно оформлен! Номер заказа: ' + data.order_id, 'success');
            setTimeout(() => {
                window.location.href = '/cart'; // Перенаправляем в профиль
            }, 2000);
        } else {
            showNotification(data.message, 'error');
            checkoutBtn.innerHTML = originalText;
            checkoutBtn.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при оформлении заказа', 'error');
        checkoutBtn.innerHTML = originalText;
        checkoutBtn.disabled = false;
    });
});

function showNotification(message, type) {
    // Создаем уведомление
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);

    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}