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


// Кнопка наверх
  const btn = document.getElementById('backToTop');

  window.addEventListener('scroll', () => {
    btn.classList.toggle('d-none', window.scrollY < 200);
  });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });



// фильтр товаров
function toggleBrands(event) {
    event.preventDefault();
    const brandList = document.querySelector(".brand-list");
    const moreBrands = document.getElementById("more-brands");
    const toggleButton = document.querySelector(".toggle-brands");

    if (moreBrands.classList.contains("hidden")) {
        // Раскрываем список (показываем все бренды + скролл)
        moreBrands.classList.remove("hidden");
        brandList.classList.add("expanded");
        toggleButton.textContent = "VIEW LESS";
    } else {
        // Сворачиваем список (оставляем только 10 брендов)
        moreBrands.classList.add("hidden");
        brandList.classList.remove("expanded");
        toggleButton.textContent = "VIEW MORE";
    }
}


// Переключатель вида карточек товаров
document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.shop-loop-item');
    const views = document.querySelectorAll('.archive-product');

    buttons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            // Сброс всех кнопок
            buttons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            const targetClass = this.getAttribute('data-view');

            views.forEach(view => {
                if (view.classList.contains(targetClass)) {
                    view.classList.add('active');
                } else {
                    view.classList.remove('active');
                }
            });
        });
    });
});


//обрезает текст по количеству символов в кратком описании товара в архиве
document.addEventListener('DOMContentLoaded', () => {
    const descriptions = document.querySelectorAll('.arhive-short-description');
    const maxLength = 400; // Максимальное количество символов

    descriptions.forEach((desc) => {
        if (desc.textContent.length > maxLength) {
            desc.textContent = desc.textContent.slice(0, maxLength) + '...'; // Обрезаем и добавляем '...'
        }
    });
});



// Показать остальные отзывы
document.addEventListener('DOMContentLoaded', function () {
    const moreBtn = document.querySelector('.view-more-reviews');
    const hideBtn = document.querySelector('.hide-reviews');
    const hiddenReviews = document.querySelectorAll('.review-list .review-card.d-none');

    moreBtn?.addEventListener('click', function () {
      hiddenReviews.forEach(card => card.classList.remove('d-none'));
      moreBtn.classList.add('d-none');
      hideBtn.classList.remove('d-none');
    });

    hideBtn?.addEventListener('click', function () {
      hiddenReviews.forEach(card => card.classList.add('d-none'));
      hideBtn.classList.add('d-none');
      moreBtn.classList.remove('d-none');
    });
  });


// ADMIN Копировать ID в буфер обмена
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".copy-product-id").forEach(function (element) {
    element.addEventListener("click", function () {
      const productId = element.getAttribute("data-id");
      navigator.clipboard.writeText(productId).then(() => {
        // Визуальное подтверждение
        element.classList.add("text-success");
        element.textContent = "Copied!";
        setTimeout(() => {
          element.classList.remove("text-success");
          element.textContent = `ID ${productId}`;
        }, 1500);
      });
    });
  });
});
