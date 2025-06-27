document.querySelectorAll('.variant-color-item').forEach(item => {
    item.addEventListener('click', e => {
        e.preventDefault();
        const imageUrl = item.getAttribute('data-image');
        if (imageUrl) {
            const mainImage = document.querySelector('.single-product-slider .swiper-slide img');
            if (mainImage) {
                mainImage.src = imageUrl;
                mainImage.parentElement.href = imageUrl;
            }
        }
        // Здесь можно добавить логику обновления выбранной вариации в форме и других местах
    });
});
