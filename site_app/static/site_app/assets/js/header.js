// TOP BAR
const topBar = document.querySelector('.top-bar');
const topBarCloseBtn = topBar?.querySelector('.btn-close');
const header = document.querySelector('header');
const headerOffset = document.querySelector('.header-offset');

if (topBarCloseBtn) {
    topBarCloseBtn.addEventListener('click', function () {
        topBar.style.transition = "height 0.5s, opacity 0.5s";
        topBar.style.height = "0";
        topBar.style.opacity = "0";
        topBar.style.overflow = "hidden";

        setTimeout(() => {
            topBar.style.display = "none";
            header?.classList.add('sticky-header');
            if (headerOffset) {
                const currentHeight = parseInt(getComputedStyle(headerOffset).height);
                headerOffset.style.height = (currentHeight - 40) + 'px';
            }
        }, 500);
    });
}

// OVERLAY
const overlay = document.getElementById('overlay');

// SIDE MENUS Универсальная функция для боковых меню
function setupMenu(triggerSelector, menuId) {
    const buttons = document.querySelectorAll(triggerSelector);
    const menu = document.getElementById(menuId);
    const closeBtn = menu?.querySelector('.close-side-btn');

    if (!menu) return;

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Закрыть все открытые меню
            document.querySelectorAll('.side-menu.active, .cart-menu.active').forEach(m => m.classList.remove('active'));
            menu.classList.add('active');
            overlay?.classList.add('active');
        });
    });

    closeBtn?.addEventListener('click', () => {
        menu.classList.remove('active');
        overlay?.classList.remove('active');
    });
}

// Закрытие активного меню по overlay
overlay?.addEventListener('click', () => {
    const openMenu = document.querySelector('.side-menu.active, .cart-menu.active');
    if (openMenu) openMenu.classList.remove('active');
    overlay.classList.remove('active');
});

// Подключение всех меню
setupMenu('.btn-box--menu', 'sideMenu');
setupMenu('.btn-box--wishlist', 'wishlistMenu');
setupMenu('.btn-box--messages', 'messagesMenu');
setupMenu('.btn-box--wallet', 'walletMenu');
setupMenu('.btn-box--cart', 'cartMenu');

// Подменю (раскрытие)
document.querySelectorAll('.has-submenu > a').forEach(link => {
    link.addEventListener('click', function (e) {
        e.preventDefault();
        this.parentElement.classList.toggle('active');
    });
});






// ACCOUNT DROPDOWN MENU
document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('overlay-dropdown');
    const menu = document.getElementById('mobileAccountDropdown');

    if (!overlay || !menu) return;

    // Показываем overlay при открытии меню
    menu.addEventListener('show.bs.collapse', () => {
      overlay.classList.add('active');
    });

    // Скрываем overlay при закрытии меню
    menu.addEventListener('hide.bs.collapse', () => {
      overlay.classList.remove('active');
    });

    // Клик по overlay закрывает меню
    overlay.addEventListener('click', () => {
      const bsCollapse = bootstrap.Collapse.getInstance(menu);
      if (bsCollapse) bsCollapse.hide();
    });
  });














// GEOLOCATION
async function detectCityByIP() {
    try {
        const response = await fetch('http://ip-api.com/json/');
        const data = await response.json();
        const cityName = data.city || 'Ваш город';

        localStorage.setItem('userCity', cityName);
        const citySpan = document.querySelector('.your-city');
        if (citySpan) citySpan.textContent = cityName;
    } catch (error) {
        console.error('Ошибка IP-определения:', error);
        const citySpan = document.querySelector('.your-city');
        if (citySpan) citySpan.textContent = 'Ваш город';
    }
}

async function detectCityByGeolocation() {
    try {
        const position = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject);
        });
        const { latitude, longitude } = position.coords;
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`);
        const data = await response.json();
        const cityName = data.address.city || data.address.town || 'Ваш город';

        localStorage.setItem('userCity', cityName);
        const citySpan = document.querySelector('.your-city');
        if (citySpan) citySpan.textContent = cityName;
    } catch (error) {
        console.error('Ошибка геолокации:', error);
        detectCityByIP();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const citySpan = document.querySelector('.your-city');
    const savedCity = localStorage.getItem('userCity');

    if (savedCity && citySpan) {
        citySpan.textContent = savedCity;
    } else {
        detectCityByIP();
    }

    document.querySelector('.location')?.addEventListener('click', () => {
        if (navigator.geolocation) {
            detectCityByGeolocation();
        } else {
            detectCityByIP();
        }
    });
});
