// Глобальные переменные для Swiper-инстансов
let singleProductSwiper = null;
let thumbsSwiper = null;

// Инициализация слайдеров Swiper
function initSwipers() {
    // Уничтожаем старые слайдеры, если они существуют
    if (singleProductSwiper) {
        singleProductSwiper.destroy(true, true);
        singleProductSwiper = null;
    }
    if (thumbsSwiper) {
        thumbsSwiper.destroy(true, true);
        thumbsSwiper = null;
    }

    // Инициализация слайдера миниатюр
    thumbsSwiper = new Swiper('.thumbs-slider', {
        spaceBetween: 10,
        slidesPerView: 4,
        freeMode: true,
        watchSlidesProgress: true,
        slideToClickedSlide: false, // Отключаем, чтобы реализовать кастомное переключение
        loop: false,
    });

    // Инициализация главного слайдера без привязки к thumbs (будем переключать вручную)
    singleProductSwiper = new Swiper('.single-product-slider', {
        spaceBetween: 10,
        loop: false,
    });

    // Обработчик клика по миниатюре с учётом смещения индексов
    thumbsSwiper.on('click', (swiper, event) => {
        const clickedIndex = swiper.clickedIndex;
        if (typeof clickedIndex === 'undefined' || clickedIndex === null) return;
        // Смещаем индекс на 1, т.к. в главном слайдере первое фото — главное, а миниатюры без него
        singleProductSwiper.slideTo(clickedIndex + 1);
    });
}

// Обновление слайдов: главное фото отдельно, миниатюры — только дополнительные фото
function updateVariantImages(mainImage, additionalImages) {
    const swiperWrapper = document.querySelector('.single-product-slider .swiper-wrapper');
    const thumbsWrapper = document.querySelector('.thumbs-slider .swiper-wrapper');
    if (!swiperWrapper || !thumbsWrapper) return;

    // Очищаем текущие слайды
    swiperWrapper.innerHTML = '';
    thumbsWrapper.innerHTML = '';

    // Добавляем главное фото в главный слайдер
    if (mainImage) {
        const mainSlide = document.createElement('div');
        mainSlide.className = 'swiper-slide';
        mainSlide.innerHTML = `
            <a href="${mainImage}" class="glightbox" data-gallery="product-gallery">
                <img src="${mainImage}" class="img-fluid" />
            </a>
        `;
        swiperWrapper.appendChild(mainSlide);
    }

    // Добавляем дополнительные фото в главный слайдер и миниатюры
    additionalImages.forEach(imgUrl => {
        // Главный слайд
        const slide = document.createElement('div');
        slide.className = 'swiper-slide';
        slide.innerHTML = `
            <a href="${imgUrl}" class="glightbox" data-gallery="product-gallery">
                <img src="${imgUrl}" class="img-fluid" />
            </a>
        `;
        swiperWrapper.appendChild(slide);

        // Миниатюра
        const thumb = document.createElement('div');
        thumb.className = 'swiper-slide';
        thumb.style.width = '50px';
        thumb.innerHTML = `
            <img src="${imgUrl}" class="img-fluid rounded border border-secondary" />
        `;
        thumbsWrapper.appendChild(thumb);
    });

    // Переинициализируем слайдеры для корректной работы
    initSwipers();
}

// Обновление размеров вариации
function updateVariantSizes(sizes) {
    const sizesContainer = document.querySelector('#variant-sizes-container');
    if (!sizesContainer) return;

    if (!sizes || sizes.length === 0) {
        sizesContainer.innerHTML = '<em>Размеры не доступны</em>';
        return;
    }

    sizesContainer.innerHTML = '';
    sizes.forEach(size => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-outline-secondary btn-sm me-1 mb-1';
        btn.textContent = size;
        sizesContainer.appendChild(btn);
    });
}

// Обработчик клика по цвету вариации
document.querySelectorAll('.variant-color-item').forEach(item => {
    item.addEventListener('click', e => {
        e.preventDefault();

        const color = item.getAttribute('data-color');
        const productId = item.getAttribute('data-product');
        if (!color || !productId) return;

        fetch(`/ajax/variant-images/${productId}/${encodeURIComponent(color)}/`)
            .then(resp => resp.json())
            .then(data => {
                if (!data.images || data.images.length === 0) return;

                // data.images[0] — главное фото, остальные — дополнительные
                const mainImage = data.images[0];
                const additionalImages = data.images.slice(1);

                updateVariantImages(mainImage, additionalImages);
                updateVariantSizes(data.sizes);
            })
            .catch(err => {
                console.error('Ошибка при загрузке данных вариации:', err);
            });
    });
});

// Инициализация слайдеров при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    initSwipers();
});
