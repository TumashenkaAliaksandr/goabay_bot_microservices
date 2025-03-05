function addToBasket(productId) {
    const quantityInput = document.getElementById('quantity-input');
    const quantity = quantityInput ? quantityInput.value : 1; // Получаем количество

    fetch('/add_to_cart/', {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `product_id=${productId}&quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById("cart-count").innerText = data.total_quantity; // Обновляем кружок
            updateBasketTotal();
        } else {
            alert("Error: " + data.error);
        }
    })
    .catch(error => console.error("Error:", error));
}
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('add-to-cart-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Предотвращаем отправку формы по умолчанию

        const formData = new FormData(form);
        const csrfToken = formData.get('csrfmiddlewaretoken');
        const quantity = formData.get('quantity');
        const productId = formData.get('product_id');

        fetch('/add_to_cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `csrfmiddlewaretoken=${csrfToken}&quantity=${quantity}&product_id=${productId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Обновляем отображение корзины (пример)
                alert('Товар добавлен в корзину!');
                // Обновите счетчик товаров в корзине здесь
            } else {
                alert('Ошибка добавления в корзину.');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при добавлении в корзину.');
        });
    });
});
