console.log('✅ Custom JS загружен и работает');

/**
 * Закрытие топ-бара и добавление липкого заголовка
 */
const topBar = document.querySelector('.top-bar');
const topBarCloseBtn = topBar?.querySelector('.btn-close');
const header = document.querySelector('header');
const headerOffset = document.querySelector('.header-offset'); // div с отступом под шапку

if (topBarCloseBtn) {
    topBarCloseBtn.addEventListener('click', function () {
        // Анимация скрытия топ-бара
        topBar.style.transition = "height 0.5s, opacity 0.5s";
        topBar.style.height = "0";
        topBar.style.opacity = "0";
        topBar.style.overflow = "hidden";

        setTimeout(() => {
            topBar.style.display = "none";
            header.classList.add('sticky-header');

            // Уменьшаем отступ под шапку на 40px
            if (headerOffset) {
                const currentHeight = parseInt(getComputedStyle(headerOffset).height);
                headerOffset.style.height = (currentHeight - 40) + 'px';
            }
        }, 500);
    });
}

// Элементы для меню
const sideMenu = document.getElementById('sideMenu');
const overlay = document.getElementById('overlay');
const sideMenuCloseBtn = sideMenu?.querySelector('.close-btn');

// Все кнопки открытия меню (для моб, планшет, десктоп)
const menuBtns = document.querySelectorAll('.menu-button');

// Открытие меню
menuBtns.forEach(btn => {
    btn.addEventListener('click', function () {
        if (sideMenu && overlay) {
            sideMenu.classList.add('active');
            overlay.classList.add('active');
        }
    });
});

// Закрытие меню
sideMenuCloseBtn?.addEventListener('click', closeMenu);
overlay?.addEventListener('click', closeMenu);

function closeMenu() {
    sideMenu.classList.remove('active');
    overlay.classList.remove('active');
}

/**
 * Подменю (раскрытие)
 */
document.querySelectorAll('.has-submenu > a').forEach(link => {
    link.addEventListener('click', function (e) {
        e.preventDefault();
        this.parentElement.classList.toggle('active');
    });
});

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

    function updateSlider() {
        if (isAnimating) return;
        isAnimating = true;
        wrapper.style.transform = `translateX(-${currentIndex * 100}%)`;
        setTimeout(() => {
            isAnimating = false;
        }, 400); // Длительность анимации в миллисекундах
    }

    function goToPrev() {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = items.length - 1; // Зацикливание
        }
        updateSlider();
    }

    function goToNext() {
        if (currentIndex < items.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0; // Зацикливание
        }
        updateSlider();
    }

    // Кнопки
    prevBtn.addEventListener('click', goToPrev);
    nextBtn.addEventListener('click', goToNext);

    // Свайпы мышью
    wrapper.addEventListener('mousedown', (e) => {
        startX = e.clientX;
        isDragging = true;
        wrapper.style.transition = 'none'; // Убираем анимацию во время драга
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
    });

    wrapper.addEventListener('mouseleave', () => {
        if (!isDragging) return;
        isDragging = false;
        wrapper.style.transition = 'transform 0.4s ease-in-out';
        updateSlider();
    });

    // Свайпы тачем
    wrapper.addEventListener('touchstart', (e) => {
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
    });

    // Инициализация
    updateSlider();
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

    function updateBlogSlider() {
        if (isAnimating) return;
        isAnimating = true;
        blogWrapper.style.transform = `translateX(-${currentIndex * 100}%)`;
        setTimeout(() => {
            isAnimating = false;
        }, 400);
    }

    function goToPrev() {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = blogItems.length - 1; // Зацикливание
        }
        updateBlogSlider();
    }

    function goToNext() {
        if (currentIndex < blogItems.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0; // Зацикливание
        }
        updateBlogSlider();
    }

    // Кнопки
    blogPrevBtn.addEventListener('click', goToPrev);
    blogNextBtn.addEventListener('click', goToNext);

    // Свайпы мышью
    blogWrapper.addEventListener('mousedown', (e) => {
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
    });

    blogWrapper.addEventListener('mouseleave', () => {
        if (!isDragging) return;
        isDragging = false;
        blogWrapper.style.transition = 'transform 0.4s ease-in-out';
        updateBlogSlider();
    });

    // Свайпы тачем
    blogWrapper.addEventListener('touchstart', (e) => {
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
    });

    // Инициализация
    updateBlogSlider();
});


// Сервис слайдер
// const swiper = new Swiper('.service-slider', {
//     loop: true,
//     autoplay: {
//       delay: 5000,
//       disableOnInteraction: false,
//     },
//     slidesPerView: 3,
//     spaceBetween: 15,
//     grabCursor: true,
//     allowTouchMove: true,
//     breakpoints: {
//       // Для мобильных — по одному
//       0: { slidesPerView: 1 },
//       // Планшеты — два
//       768: { slidesPerView: 2 },
//       // Десктоп — три
//       992: { slidesPerView: 3 },
//     },
//   });
//
//
// // Бренд слайдер
// const brandSlider = new Swiper('.brand-slider', {
//   slidesPerView: 8,
//   spaceBetween: 15,
//   loop: true,
//   autoplay: {
//     delay: 5000,
//     disableOnInteraction: false,
//   },
//   breakpoints: {
//     320: { slidesPerView: 2 },
//     576: { slidesPerView: 3 },
//     768: { slidesPerView: 5 },
//     1200: { slidesPerView: 8 }
//   }
// });

// Категории слайдер
const categorySlider = new Swiper('.category-slider', {
    slidesPerView: 8,
    spaceBetween: 15,
    loop: true,
    autoplay: {
        delay: 5000,
        disableOnInteraction: false,
    },
    breakpoints: {
      320: { slidesPerView: 2 },
      480: { slidesPerView: 3  },
      768: { slidesPerView: 5 },
      1024: { slidesPerView: 8 }
    }
  });

// БАННЕР слайдер
const bannerSwiper = new Swiper('.banner-slider', {
    loop: true,
    slidesPerView: 2,        // Показываем 2 слайда одновременно
    spaceBetween: 15,        // Отступ между слайдами
    autoplay: {
        delay: 5000,
    },
    breakpoints: {
      320: { slidesPerView: 1 },
      480: { slidesPerView: 1  },
      768: { slidesPerView: 1 },
      1024: { slidesPerView: 2 }
    }
});












// Первый слайдер
const productSwiper = new Swiper('.product-slider', {
  loop: true,
  slidesPerView: 3,
  spaceBetween: 15,
  breakpoints: {
    320: { slidesPerView: 1 },
    768: { slidesPerView: 2 },
    1200: { slidesPerView: 3 },
  }
});

// Второй слайдер
const secondSwiper = new Swiper('.second-product-slider', {
  loop: true,
  slidesPerView: 5,
  spaceBetween: 20,
  breakpoints: {
    320: { slidesPerView: 2 },
    768: { slidesPerView: 3 },
    1200: { slidesPerView: 6 },
  }
});

// Третий слайдер
const thirdSwiper = new Swiper('.third-product-slider', {
  loop: true,
  slidesPerView: 5,
  spaceBetween: 20,
  breakpoints: {
    320: { slidesPerView: 2 },
    768: { slidesPerView: 4 },
    1200: { slidesPerView: 8 },
  }
});




// Вертикальный слайдер в с товарами в ряд
const sliders = document.querySelectorAll('.vertical-swiper');
  sliders.forEach((slider) => {
    new Swiper(slider, {
      direction: 'vertical',
      slidesPerView: 3,
      spaceBetween: 10,
      loop: true,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false,
      },
      allowTouchMove: true, // Можно убрать если нужен только авто-скролл
    });
  });







