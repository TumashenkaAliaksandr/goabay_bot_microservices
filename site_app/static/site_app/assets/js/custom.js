// Боковое меню корзины
const openCartBtns = document.querySelectorAll('.open-cart-btn');
const cartMenu = document.getElementById('cartMenu');
const cartOverlay = document.getElementById('cartOverlay');
const closeCartBtn = cartMenu?.querySelector('.close-cart-btn');

// Открытие корзины по любой кнопке
openCartBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        cartMenu.classList.add('active');
        cartOverlay.classList.add('active');
    });
});

// Закрытие корзины по крестику или оверлею
closeCartBtn?.addEventListener('click', closeCart);
cartOverlay?.addEventListener('click', closeCart);

function closeCart() {
    cartMenu.classList.remove('active');
    cartOverlay.classList.remove('active');
}

// Слайдер
document.addEventListener('DOMContentLoaded', () => {
    const sliderBox = document.querySelector('.slider-box');
    const wrapper = sliderBox.querySelector('.slider-wrapper');
    const items = sliderBox.querySelectorAll('.slider-item');
    const prevBtn = sliderBox.querySelector('.slider-control-prev');
    const nextBtn = sliderBox.querySelector('.slider-control-next');

    let currentIndex = 0;
    let isAnimating = false;
    let startX = 0;
    let isDragging = false;
    let autoSlideInterval; // Добавили переменную для интервала

    // Автоматическая прокрутка
    function startAutoSlide() {
        autoSlideInterval = setInterval(() => {
            goToNext();
        }, 5000); // Интервал 5 секунд
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
        stopAutoSlide(); // Останавливаем авто-прокрутку при ручном управлении
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = items.length - 1;
        }
        updateSlider();
        startAutoSlide(); // Возобновляем авто-прокрутку
    }

    function goToNext() {
        stopAutoSlide(); // Останавливаем авто-прокрутку при ручном управлении
        if (currentIndex < items.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0;
        }
        updateSlider();
        startAutoSlide(); // Возобновляем авто-прокрутку
    }

    // Обработчики событий
    prevBtn.addEventListener('click', goToPrev);
    nextBtn.addEventListener('click', goToNext);

    // Пауза при наведении
    sliderBox.addEventListener('mouseenter', stopAutoSlide);
    sliderBox.addEventListener('mouseleave', startAutoSlide);

    // Свайпы мышью
    wrapper.addEventListener('mousedown', (e) => {
        stopAutoSlide(); // Пауза при взаимодействии
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
        startAutoSlide(); // Возобновление после взаимодействия
    });

    wrapper.addEventListener('mouseleave', () => {
        if (!isDragging) return;
        isDragging = false;
        wrapper.style.transition = 'transform 0.4s ease-in-out';
        updateSlider();
        startAutoSlide(); // Возобновление при уходе курсора
    });

    // Свайпы тачем
    wrapper.addEventListener('touchstart', (e) => {
        stopAutoSlide(); // Пауза при взаимодействии
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
        startAutoSlide(); // Возобновление после взаимодействия
    });

    // Инициализация
    updateSlider();
    startAutoSlide(); // Запускаем авто-прокрутку при загрузке
});

// Блог слайдер
document.addEventListener('DOMContentLoaded', () => {
    // Слайдер для блога
    const blogSlider = document.querySelector('.blog-slider');
    const blogWrapper = blogSlider.querySelector('.blog-slider-wrapper');
    const blogItems = blogSlider.querySelectorAll('.blog-slider-item');
    const blogPrevBtn = blogSlider.querySelector('.blog-slider-control-prev');
    const blogNextBtn = blogSlider.querySelector('.blog-slider-control-next');

    let currentIndex = 0;
    let isAnimating = false;
    let startX = 0;
    let isDragging = false;
    let blogAutoSlideInterval; // Добавляем переменную для интервала

    // Функции для автопрокрутки
    function startBlogAutoSlide() {
        blogAutoSlideInterval = setInterval(() => {
            goToNext();
        }, 5000); // Интервал 5 секунд
    }

    function stopBlogAutoSlide() {
        clearInterval(blogAutoSlideInterval);
    }

    function updateBlogSlider() {
        if (isAnimating) return;
        isAnimating = true;
        blogWrapper.style.transform = `translateX(-${currentIndex * 100}%)`;
        setTimeout(() => {
            isAnimating = false;
        }, 400);
    }

    function goToPrev() {
        stopBlogAutoSlide(); // Останавливаем авто-прокрутку
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = blogItems.length - 1;
        }
        updateBlogSlider();
        startBlogAutoSlide(); // Возобновляем авто-прокрутку
    }

    function goToNext() {
        stopBlogAutoSlide(); // Останавливаем авто-прокрутку
        if (currentIndex < blogItems.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0;
        }
        updateBlogSlider();
        startBlogAutoSlide(); // Возобновляем авто-прокрутку
    }

    // Кнопки
    blogPrevBtn.addEventListener('click', goToPrev);
    blogNextBtn.addEventListener('click', goToNext);

    // Управление автопрокруткой при наведении
    blogSlider.addEventListener('mouseenter', stopBlogAutoSlide);
    blogSlider.addEventListener('mouseleave', startBlogAutoSlide);

    // Свайпы мышью
    blogWrapper.addEventListener('mousedown', (e) => {
        stopBlogAutoSlide(); // Пауза при взаимодействии
        startX = e.clientX;
        isDragging = true;
        blogWrapper.style.transition = 'none';
        e.preventDefault();
    });

    blogWrapper.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const diff = e.clientX - startX;
        const translate = -currentIndex * 100 + (diff / blogWrapper.offsetWidth) * 100;
        blogWrapper.style.transform = `translateX(${translate}%)`;
    });

    blogWrapper.addEventListener('mouseup', (e) => {
        if (!isDragging) return;
        isDragging = false;
        blogWrapper.style.transition = 'transform 0.4s ease-in-out';
        const diff = e.clientX - startX;
        if (Math.abs(diff) > 50) {
            diff > 0 ? goToPrev() : goToNext();
        } else {
            updateBlogSlider();
        }
        startBlogAutoSlide(); // Возобновление после взаимодействия
    });

    blogWrapper.addEventListener('mouseleave', () => {
        if (!isDragging) return;
        isDragging = false;
        blogWrapper.style.transition = 'transform 0.4s ease-in-out';
        updateBlogSlider();
        startBlogAutoSlide(); // Возобновление при уходе курсора
    });

    // Свайпы тачем
    blogWrapper.addEventListener('touchstart', (e) => {
        stopBlogAutoSlide(); // Пауза при взаимодействии
        startX = e.touches[0].clientX;
        isDragging = true;
        blogWrapper.style.transition = 'none';
    });

    blogWrapper.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        const diff = e.touches[0].clientX - startX;
        const translate = -currentIndex * 100 + (diff / blogWrapper.offsetWidth) * 100;
        blogWrapper.style.transform = `translateX(${translate}%)`;
        e.preventDefault();
    });

    blogWrapper.addEventListener('touchend', (e) => {
        if (!isDragging) return;
        isDragging = false;
        blogWrapper.style.transition = 'transform 0.4s ease-in-out';
        const diff = e.changedTouches[0].clientX - startX;
        if (Math.abs(diff) > 50) {
            diff > 0 ? goToPrev() : goToNext();
        } else {
            updateBlogSlider();
        }
        startBlogAutoSlide(); // Возобновление после взаимодействия
    });

    // Инициализация
    updateBlogSlider();
    startBlogAutoSlide(); // Запускаем авто-прокрутку
});
