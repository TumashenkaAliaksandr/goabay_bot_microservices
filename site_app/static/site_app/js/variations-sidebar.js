// Глобальные переменные для Swiper-инстансов
let singleProductSwiper = null;
let thumbsSwiper = null;

// Инициализация слайдеров Swiper
function initSwipers() {
    if (singleProductSwiper) {
        singleProductSwiper.destroy(true, true);
        singleProductSwiper = null;
    }
    if (thumbsSwiper) {
        thumbsSwiper.destroy(true, true);
        thumbsSwiper = null;
    }

    thumbsSwiper = new Swiper('.thumbs-slider', {
        spaceBetween: 10,
        slidesPerView: 4,
        freeMode: true,
        watchSlidesProgress: true,
        slideToClickedSlide: false,
        loop: false,
    });

    singleProductSwiper = new Swiper('.single-product-slider', {
        spaceBetween: 10,
        loop: false,
    });

    thumbsSwiper.on('click', (swiper) => {
        const clickedIndex = swiper.clickedIndex;
        if (typeof clickedIndex === 'undefined' || clickedIndex === null) return;
        singleProductSwiper.slideTo(clickedIndex + 1);
    });
}

// Обновление изображений вариации
function updateVariantImages(mainImage, additionalImages) {
    const swiperWrapper = document.querySelector('.single-product-slider .swiper-wrapper');
    const thumbsWrapper = document.querySelector('.thumbs-slider .swiper-wrapper');
    if (!swiperWrapper || !thumbsWrapper) return;

    swiperWrapper.innerHTML = '';
    thumbsWrapper.innerHTML = '';

    if (mainImage) {
        const mainSlide = document.createElement('div');
        mainSlide.className = 'swiper-slide';
        mainSlide.innerHTML = `
            <a href="${mainImage}" class="glightbox" data-gallery="product-gallery">
                <img src="${mainImage}" class="img-fluid" alt="Main product image" />
            </a>
        `;
        swiperWrapper.appendChild(mainSlide);
    }

    additionalImages.forEach(imgUrl => {
        if (!imgUrl) return;

        const slide = document.createElement('div');
        slide.className = 'swiper-slide';
        slide.innerHTML = `
            <a href="${imgUrl}" class="glightbox" data-gallery="product-gallery">
                <img src="${imgUrl}" class="img-fluid" alt="Additional product image" />
            </a>
        `;
        swiperWrapper.appendChild(slide);

        const thumb = document.createElement('div');
        thumb.className = 'swiper-slide';
        thumb.style.width = '50px';
        thumb.innerHTML = `
            <img src="${imgUrl}" class="img-fluid rounded border border-secondary" alt="Thumbnail image" />
        `;
        thumbsWrapper.appendChild(thumb);
    });

    initSwipers();
}

// Обновление размеров вариации
function updateVariantSizes(sizes) {
    const sizesContainer = document.getElementById('variant-sizes-container');
    if (!sizesContainer) return;

    if (!sizes || sizes.length === 0) {
        sizesContainer.innerHTML = '<em>➖</em>';
        return;
    }

    sizesContainer.innerHTML = '';
    sizes.forEach(size => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-outline-secondary btn-sm me-1 mb-1';
        btn.textContent = size;
        btn.setAttribute('data-size', size);
        btn.setAttribute('aria-label', `Выбрать размер ${size}`);
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

        // Обновляем активный класс
        document.querySelectorAll('.variant-color-item.active').forEach(btn => btn.classList.remove('active'));
        item.classList.add('active');

        fetch(`/ajax/variant-images/${productId}/${encodeURIComponent(color)}/`)
            .then(resp => {
                if (!resp.ok) throw new Error(`HTTP error! status: ${resp.status}`);
                return resp.json();
            })
            .then(data => {
                if (!data.images || data.images.length === 0) {
                    console.warn('Нет изображений для выбранной вариации');
                    updateVariantImages(null, []);
                    updateVariantSizes([]);
                    return;
                }

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

// При загрузке страницы показываем размеры активной вариации
document.addEventListener('DOMContentLoaded', () => {
    initSwipers();

    const activeColorBtn = document.querySelector('.variant-color-item.active');
    if (activeColorBtn) {
        const sizesStr = activeColorBtn.getAttribute('data-sizes') || '';
        const sizes = sizesStr ? sizesStr.split(',') : [];
        updateVariantSizes(sizes);
    } else {
        updateVariantSizes([]);
    }
});
