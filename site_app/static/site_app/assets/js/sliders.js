document.addEventListener('DOMContentLoaded', () => {
  // Слайдер продуктов (Ручной)
  const sliderBox = document.querySelector('.slider-box');

  if (sliderBox) {
    const wrapper = sliderBox.querySelector('.slider-wrapper');
    const items = sliderBox.querySelectorAll('.slider-item');
    const prevBtn = sliderBox.querySelector('.slider-control-prev');
    const nextBtn = sliderBox.querySelector('.slider-control-next');

    if (!wrapper || !items || !prevBtn || !nextBtn) {
      console.warn('Не все элементы найдены для slider-box');
      return;
    }

    let currentIndex = 0;
    let isAnimating = false;
    let startX = 0;
    let isDragging = false;
    let autoSlideInterval; // Добавляем переменную для интервала

    function updateSlider() {
      if (isAnimating) return;
      isAnimating = true;
      wrapper.style.transform = `translateX(-${currentIndex * 100}%)`;
      setTimeout(() => {
        isAnimating = false;
      }, 400);
    }

    function goToPrev() {
      if (currentIndex > 0) {
        currentIndex--;
      } else {
        currentIndex = items.length - 1;
      }
      updateSlider();
    }

    function goToNext() {
      if (currentIndex < items.length - 1) {
        currentIndex++;
      } else {
        currentIndex = 0;
      }
      updateSlider();
    }

    // Функция автоматической прокрутки
    function startAutoSlide() {
      autoSlideInterval = setInterval(() => {
        goToNext(); // Переключаемся на следующий слайд
      }, 3000); // Интервал 3 секунды (можно изменить)
    }

    // Останавливаем автоматическую прокрутку
    function stopAutoSlide() {
      clearInterval(autoSlideInterval);
    }

    prevBtn.addEventListener('click', goToPrev);
    nextBtn.addEventListener('click', goToNext);

    // Добавляем обработку событий для остановки/запуска при наведении
    sliderBox.addEventListener('mouseenter', stopAutoSlide);
    sliderBox.addEventListener('mouseleave', startAutoSlide);

    wrapper.addEventListener('mousedown', (e) => {
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
    });

    wrapper.addEventListener('mouseleave', () => {
      if (!isDragging) return;
      isDragging = false;
      wrapper.style.transition = 'transform 0.4s ease-in-out';
      updateSlider();
    });

    wrapper.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      isDragging = true;
      wrapper.style.transition = 'none';
    });

    wrapper.addEventListener('touchmove', (e) => {
      if (!isDragging) return;
      const diff = e.touches[0].clientX - startX;
      const translate = -currentIndex * 100 + (diff / wrapper.offsetWidth) * 100;
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

    updateSlider();
    startAutoSlide(); // Запускаем автоматическую прокрутку
  }

  // Блог слайдер (Ручной)
  const blogSlider = document.querySelector('.blog-slider');

  if (blogSlider) {
    const blogWrapper = blogSlider.querySelector('.blog-slider-wrapper');
    const blogItems = blogSlider.querySelectorAll('.blog-slider-item');
    const blogPrevBtn = blogSlider.querySelector('.blog-slider-control-prev');
    const blogNextBtn = blogSlider.querySelector('.blog-slider-control-next');

    //Проверка на null
    if (!blogWrapper || !blogItems || !blogPrevBtn || !blogNextBtn) {
      console.warn('Не все элементы найдены для blog-slider');
      return; // Выходим из функции, если что-то не найдено
    }

    let currentIndex = 0;
    let isAnimating = false;
    let startX = 0;
    let isDragging = false;
    let blogAutoSlideInterval;

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

    function startBlogAutoSlide() {
      blogAutoSlideInterval = setInterval(() => {
        goToNext(); // Переключаемся на следующий слайд
      }, 3000); // Интервал 3 секунды (можно изменить)
    }

    function stopBlogAutoSlide() {
      clearInterval(blogAutoSlideInterval);
    }


    // Кнопки
    blogPrevBtn.addEventListener('click', goToPrev);
    blogNextBtn.addEventListener('click', goToNext);

    // События для остановки и запуска автопрокрутки при наведении
    blogSlider.addEventListener('mouseenter', stopBlogAutoSlide);
    blogSlider.addEventListener('mouseleave', startBlogAutoSlide);

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
    startBlogAutoSlide(); // Запускаем автоматическую прокрутку
  }


  // Сервис слайдер (Swiper)
  const swiper = new Swiper('.service-slider', {
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false,
    },
    slidesPerView: 3,
    spaceBetween: 15,
    grabCursor: true,
    allowTouchMove: true,
    breakpoints: {
      0: { slidesPerView: 1 },
      768: { slidesPerView: 2 },
      992: { slidesPerView: 3 },
    },
  });

  // Бренд слайдер (Swiper)
  const brandSlider = new Swiper('.brand-slider', {
    slidesPerView: 8,
    spaceBetween: 15,
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false,
    },
    breakpoints: {
      320: { slidesPerView: 2 },
      576: { slidesPerView: 3 },
      768: { slidesPerView: 5 },
      1200: { slidesPerView: 6 },
      1400: { slidesPerView: 8 }
    }
  });

  // Категории слайдер (Swiper)
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
      480: { slidesPerView: 3 },
      768: { slidesPerView: 5 },
      1200: { slidesPerView: 6 },
      1400: { slidesPerView: 8 }
    }
  });

  // БАННЕР слайдер (Swiper)
  const bannerSwiper = new Swiper('.banner-slider', {
    loop: true,
    slidesPerView: 2,        // Показываем 2 слайда одновременно
    spaceBetween: 15,        // Отступ между слайдами
    autoplay: {
      delay: 5000,
    },
    breakpoints: {
      320: { slidesPerView: 1 },
      480: { slidesPerView: 1 },
      768: { slidesPerView: 1 },
      1024: { slidesPerView: 2 }
    }
  });

  // Первый слайдер (Swiper)
  const productSwiper = new Swiper('.product-slider', {
    loop: true,
    slidesPerView: 8,
    spaceBetween: 15,
    autoplay: {
      delay: 5000,
    },
    breakpoints: {
      320: { slidesPerView: 1 },
      768: { slidesPerView: 2 },
      1200: { slidesPerView: 3 },
    }
  });

  // Второй слайдер (Swiper)
  const secondSwiper = new Swiper('.second-product-slider', {
    loop: true,
    slidesPerView: 5,
    spaceBetween: 20,
    autoplay: {
      delay: 4500,
    },
    breakpoints: {
      320: { slidesPerView: 2 },
      768: { slidesPerView: 3 },
      1200: { slidesPerView: 6 },
    }
  });

  // Третий слайдер (Swiper)
  const thirdSwiper = new Swiper('.third-product-slider', {
    loop: true,
    slidesPerView: 5,
    spaceBetween: 20,
    autoplay: {
      delay: 4000,
    },
    breakpoints: {
      320: { slidesPerView: 2 },
      768: { slidesPerView: 4 },
      1200: { slidesPerView: 8 },
    }
  });


  // Вертикальный слайдер (Swiper)
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

});
