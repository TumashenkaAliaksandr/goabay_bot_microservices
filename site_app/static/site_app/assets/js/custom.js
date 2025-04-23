document.addEventListener('DOMContentLoaded', () => {
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

    // Общий код для слайдеров (проверяем наличие элементов перед инициализацией)

    // Слайдер продуктов
    const sliderBox = document.querySelector('.slider-box');

    if (sliderBox) {
        const wrapper = sliderBox.querySelector('.slider-wrapper');
        const items = sliderBox.querySelectorAll('.slider-item');
        const prevBtn = sliderBox.querySelector('.slider-control-prev');
        const nextBtn = sliderBox.querySelector('.slider-control-next');

        let currentIndex = 0;
        let isAnimating = false;
        let startX = 0;
        let isDragging = false;
        let autoSlideInterval;

        function startAutoSlide() {
            autoSlideInterval = setInterval(() => {
                goToNext();
            }, 5000);
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
            if (currentIndex > 0) {
                currentIndex--;
            } else {
                currentIndex = items.length - 1;
            }
            updateSlider();
            startAutoSlide();
        }

        function goToNext() {
            stopAutoSlide();
            if (currentIndex < items.length - 1) {
                currentIndex++;
            } else {
                currentIndex = 0;
            }
            updateSlider();
            startAutoSlide();
        }

        prevBtn.addEventListener('click', goToPrev);
        nextBtn.addEventListener('click', goToNext);

        sliderBox.addEventListener('mouseenter', stopAutoSlide);
        sliderBox.addEventListener('mouseleave', startAutoSlide);

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

    // Переключение темы и синхронизация всех переключателей
    function toggleTheme(event) {
        const isChecked = event.target.checked;
        const theme = isChecked ? 'dark' : 'light';

        // Применяем тему
        document.body.classList.toggle('dark-theme', isChecked);
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);

        // Обновляем состояние всех переключателей
        document.querySelectorAll('.theme-toggle').forEach(input => {
            if (input !== event.target) {
                input.checked = isChecked;
            }
        });
    }

    // Применение темы при загрузке страницы
    window.addEventListener('DOMContentLoaded', () => {
        const savedTheme = localStorage.getItem('theme') || 'light';
        const isDark = savedTheme === 'dark';

        // Применяем тему
        document.body.classList.toggle('dark-theme', isDark);
        document.documentElement.setAttribute('data-theme', savedTheme);

        // Устанавливаем состояние всех переключателей
        document.querySelectorAll('.theme-toggle').forEach(input => {
            input.checked = isDark;
            input.addEventListener('change', toggleTheme);
        });
    });

    // Блог слайдер
    const blogSlider = document.querySelector('.blog-slider');

    if (blogSlider) {
        const blogWrapper = blogSlider.querySelector('.blog-slider-wrapper');
        const blogItems = blogSlider.querySelectorAll('.blog-slider-item');
        const blogPrevBtn = blogSlider.querySelector('.blog-slider-control-prev');
        const blogNextBtn = blogSlider.querySelector('.blog-slider-control-next');

        let currentIndex = 0;
        let isAnimating = false;
        let startX = 0;
        let isDragging = false;
        let blogAutoSlideInterval;

        function startBlogAutoSlide() {
            blogAutoSlideInterval = setInterval(() => {
                goToNext();
            }, 5000);
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
            stopBlogAutoSlide();
            if (currentIndex > 0) {
                currentIndex--;
            } else {
                currentIndex = blogItems.length - 1;
            }
            updateBlogSlider();
            startBlogAutoSlide();
        }

        function goToNext() {
            stopBlogAutoSlide();
            if (currentIndex < blogItems.length - 1) {
                currentIndex++;
            } else {
                currentIndex = 0;
            }
            updateBlogSlider();
            startBlogAutoSlide();
        }

        blogPrevBtn.addEventListener('click', goToPrev);
        blogNextBtn.addEventListener('click', goToNext);

        blogSlider.addEventListener('mouseenter', stopBlogAutoSlide);
        blogSlider.addEventListener('mouseleave', startBlogAutoSlide);

        blogWrapper.addEventListener('mousedown', (e) => {
            stopBlogAutoSlide();
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
            startBlogAutoSlide();
        });

        blogWrapper.addEventListener('mouseleave', () => {
            if (!isDragging) return;
            isDragging = false;
            blogWrapper.style.transition = 'transform 0.4s ease-in-out';
            updateBlogSlider();
            startBlogAutoSlide();
        });

        blogWrapper.addEventListener('touchstart', (e) => {
            stopBlogAutoSlide();
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
            startBlogAutoSlide();
        });

        updateBlogSlider();
        startBlogAutoSlide();
    }
});

