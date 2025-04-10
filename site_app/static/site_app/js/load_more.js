document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('products-container');
    const loadMoreContainer = document.getElementById('load-more-container');

    if (!container || !loadMoreContainer) {
        console.error('Контейнеры не найдены!');
        return;
    }

    let isLoading = false;
    let page = 2;
    let hasMore = true;
    let lastScrollTime = 0;

    const loadProducts = () => {
        if (!hasMore || isLoading) return;

        isLoading = true;
        loadMoreContainer.innerHTML = '<div class="loader">Loading...</div>';

        const url = new URL(window.location.href);
        url.searchParams.set('page', page);
        url.searchParams.set('_', Date.now());

        fetch(url, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(response => {
            if (!response.ok) throw new Error(`Ошибка ${response.status}`);
            return response.json();
        })
        .then(data => {
            // Добавляем проверку данных
            if (!data || !data.html || !data.has_next) {
                throw new Error('Некорректный ответ сервера');
            }

            // Улучшенная проверка дубликатов
            const parser = new DOMParser();
            const doc = parser.parseFromString(data.html, 'text/html');
            const newItems = doc.body.children;

            Array.from(newItems).forEach(item => {
                if (!container.querySelector(`[data-id="${item.dataset.id}"]`)) {
                    container.insertAdjacentHTML('beforeend', item.outerHTML);
                }
            });

            page++;
            hasMore = data.has_next;

            // Обновление информации о страницах
            if (!data.has_next) {
                loadMoreContainer.innerHTML = `
                    <p class="text-center py-3">
                        Показано ${container.children.length} из ${data.total_pages * 15} товаров
                    </p>`;
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            loadMoreContainer.innerHTML = `
                <div class="text-center py-3 text-danger">
                    ${error.message}
                    <button class="btn btn-sm btn-secondary mt-2" 
                            onclick="window.location.reload()">
                        Обновить страницу
                    </button>
                </div>`;
        })
        .finally(() => {
            isLoading = false;
        });
    };

    // Оптимизированный обработчик скролла
    const scrollHandler = () => {
        if (isLoading || !hasMore) return;

        if (Date.now() - lastScrollTime < 500) return;
        lastScrollTime = Date.now();

        const { bottom } = loadMoreContainer.getBoundingClientRect();
        const triggerPoint = window.innerHeight + 300;

        if (bottom <= triggerPoint) {
            loadProducts();
        }
    };

    // Инициализация
    window.addEventListener('scroll', scrollHandler);
    window.addEventListener('resize', scrollHandler);
    scrollHandler();
});
