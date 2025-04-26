document.addEventListener('DOMContentLoaded', () => {
    // Боковое меню корзины
    const openCartBtns = document.querySelectorAll('.open-cart-btn');
    const cartMenu = document.getElementById('cartMenu');
    const cartOverlay = document.getElementById('cartOverlay');
    const closeCartBtn = cartMenu?.querySelector('.close-cart-btn');

    // Открытие корзины по любой кнопке
    openCartBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            cartMenu?.classList.add('active');
            cartOverlay?.classList.add('active');
        });
    });

    // Закрытие корзины по крестику или оверлею
    closeCartBtn?.addEventListener('click', closeCart);
    cartOverlay?.addEventListener('click', closeCart);

    function closeCart() {
        cartMenu?.classList.remove('active');
        cartOverlay?.classList.remove('active');
    }

    // Универсальная функция инициализации слайдера
    function initSlider(selector, wrapperSelector, itemSelector, prevBtnSelector, nextBtnSelector) {
        const sliderBox = document.querySelector(selector);
        if (!sliderBox) return;

        const wrapper = sliderBox.querySelector(wrapperSelector);
        const items = sliderBox.querySelectorAll(itemSelector);
        const prevBtn = sliderBox.querySelector(prevBtnSelector);
        const nextBtn = sliderBox.querySelector(nextBtnSelector);

        let currentIndex = 0;
        let isAnimating = false;
        let startX = 0;
        let isDragging = false;
        let autoSlideInterval;

        function startAutoSlide() {
            autoSlideInterval = setInterval(goToNext, 5000);
        }

        function stopAutoSlide() {
            clearInterval(autoSlideInterval);
        }

        function updateSlider() {
            if (isAnimating) return;
            isAnimating = true;
            wrapper.style.transform = `translateX(-${currentIndex * 100}%)`;
            setTimeout(() => {
                isAnimating = false;
            }, 400);
        }

        function goToPrev() {
            stopAutoSlide();
            currentIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
            updateSlider();
            startAutoSlide();
        }

        function goToNext() {
            stopAutoSlide();
            currentIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
            updateSlider();
            startAutoSlide();
        }

        prevBtn?.addEventListener('click', goToPrev);
        nextBtn?.addEventListener('click', goToNext);

        sliderBox.addEventListener('mouseenter', stopAutoSlide);
        sliderBox.addEventListener('mouseleave', startAutoSlide);

        // Drag & Touch Events
        wrapper.addEventListener('mousedown', (e) => {
            stopAutoSlide();
            startX = e.clientX;
            isDragging = true;
            wrapper.style.transition = 'none';
            e.preventDefault();
        });

        wrapper.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const diff = e.clientX - startX;
            const translate = -currentIndex * 100 + (diff / wrapper.offsetWidth) * 100;
            wrapper.style.transform = `translateX(${translate}%)`;
        });

        wrapper.addEventListener('mouseup', (e) => {
            if (!isDragging) return;
            isDragging = false;
            wrapper.style.transition = 'transform 0.4s ease-in-out';
            const diff = e.clientX - startX;
            if (Math.abs(diff) > 50) {
                diff > 0 ? goToPrev() : goToNext();
            } else {
                updateSlider();
            }
            startAutoSlide();
        });

        wrapper.addEventListener('mouseleave', () => {
            if (!isDragging) return;
            isDragging = false;
            wrapper.style.transition = 'transform 0.4s ease-in-out';
            updateSlider();
            startAutoSlide();
        });

        wrapper.addEventListener('touchstart', (e) => {
            stopAutoSlide();
            startX = e.touches[0].clientX;
            isDragging = true;
            wrapper.style.transition = 'none';
        });

        wrapper.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            const diff = e.touches[0].clientX - startX;
            const translate = -currentIndex * 100 + (diff / wrapper.offsetWidth) * 100;
            wrapper.style.transform = `translateX(${translate}%)`;
            e.preventDefault();
        });

        wrapper.addEventListener('touchend', (e) => {
            if (!isDragging) return;
            isDragging = false;
            wrapper.style.transition = 'transform 0.4s ease-in-out';
            const diff = e.changedTouches[0].clientX - startX;
            if (Math.abs(diff) > 50) {
                diff > 0 ? goToPrev() : goToNext();
            } else {
                updateSlider();
            }
            startAutoSlide();
        });

        updateSlider();
        startAutoSlide();
    }

    // Инициализация слайдера продуктов
    initSlider('.slider-box', '.slider-wrapper', '.slider-item', '.slider-control-prev', '.slider-control-next');

    // Инициализация слайдера блога
    initSlider('.blog-slider', '.blog-slider-wrapper', '.blog-slider-item', '.blog-slider-control-prev', '.blog-slider-control-next');
});
