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


