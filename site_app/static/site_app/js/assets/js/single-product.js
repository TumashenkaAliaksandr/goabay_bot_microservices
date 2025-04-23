// SINGLE-PRODUCT Фото слайдер товара
document.addEventListener('DOMContentLoaded', function () {
  const thumbsSwiper = new Swiper(".thumbs-slider", {
    slidesPerView: 3,
    spaceBetween: 10,
    watchSlidesProgress: true,
  });

  const mainSwiper = new Swiper(".single-product-slider", {
    spaceBetween: 10,
    loop: true,
    thumbs: {
      swiper: thumbsSwiper,
    },
  });

  const lightbox = GLightbox({
    selector: '.glightbox',
    touchNavigation: true,
    loop: true,
    zoomable: true,
  });
});

// SINGLE PRODUCT NAVIGATION
document.addEventListener('DOMContentLoaded', () => {
  // Выбираем только блоки с классом .product-navigation
  const boxes = document.querySelectorAll('.box.product-navigation');

  if (!boxes.length) {
    console.warn('Блоки навигации (.box.product-navigation) не найдены');
    return;
  }

  boxes.forEach(box => {
    const quantityInput = box.querySelector('input[type="number"]');
    const minusBtn = box.querySelector('.input-group button:first-child');
    const plusBtn = box.querySelector('.input-group button:last-child');
    const variationGroups = box.querySelectorAll('.product-variations');
    const colorBoxes = box.querySelectorAll('.color-box input[type="checkbox"]');

    // Проверка наличия всех необходимых элементов
    if (!quantityInput || !minusBtn || !plusBtn || !variationGroups.length || !colorBoxes.length) {
      console.warn('Некоторые элементы не найдены в блоке:', box);
      return;
    }

    // Уменьшение количества
    minusBtn.addEventListener('click', () => {
      let val = parseInt(quantityInput.value) || 1;
      if (val > 1) {
        quantityInput.value = val - 1;
        updateSummary();
      }
    });

    // Увеличение количества
    plusBtn.addEventListener('click', () => {
      let val = parseInt(quantityInput.value) || 1;
      quantityInput.value = val + 1;
      updateSummary();
    });

    // Обновление при изменении количества
    quantityInput.addEventListener('input', () => {
      if (quantityInput.value < 1) quantityInput.value = 1;
      updateSummary();
    });

    // Обработчики для размеров и опций
    variationGroups.forEach(group => {
      const buttons = group.querySelectorAll('.btn-variation');
      buttons.forEach(btn => {
        btn.addEventListener('click', () => {
          buttons.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          updateSummary();
        });
      });
    });

    // Обработчики для цвета
    colorBoxes.forEach(input => {
      input.addEventListener('change', () => {
        colorBoxes.forEach(box => {
          if (box !== input) box.checked = false;
        });
        updateSummary();
      });
    });

    // Обновление итоговой суммы и опций для всех блоков
    function updateSummary() {
      boxes.forEach(b => {
        const sizeBtn = b.querySelector('.product-variations .btn-variation.active');
        const optionBtn = b.querySelectorAll('.product-variations')[1]?.querySelector('.btn-variation.active');
        const colorInput = [...b.querySelectorAll('.color-box input[type="checkbox"]')].find(i => i.checked);
        const quantity = parseInt(b.querySelector('input[type="number"]').value) || 1;
        const base = parseFloat(b.querySelector('.price-value')?.dataset.inr || 0);
        const sizePrice = parseFloat(sizeBtn?.dataset.price || 0);
        const optPrice = parseFloat(optionBtn?.dataset.price || 0);
        const colPrice = parseFloat(colorInput?.dataset.price || 0);
        const final = (base + sizePrice + optPrice + colPrice) * quantity;

        // Обновление отображаемой цены и значений
        const priceElement = b.querySelector('.price-value');
        const sizeElement = b.querySelector('.size-value');
        const optionElement = b.querySelector('.option-value');
        const colorElement = b.querySelector('.color-value');

        if (priceElement) priceElement.textContent = final.toFixed(2);
        if (sizeElement) sizeElement.textContent = sizeBtn?.textContent || '-';
        if (optionElement) optionElement.textContent = optionBtn?.textContent || '-';
        if (colorElement) colorElement.textContent = colorInput ? capitalize(colorInput.value) : '-';
      });
    }

    // Функция для капитализации первого символа
    function capitalize(str) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }

    // Инициализация
    updateSummary();
  });
});