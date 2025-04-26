document.addEventListener('DOMContentLoaded', function () {
  // Объект валют
  let rates = {
    INR: { symbol: '₹', rate: 1, active: true, lastModified: '' },
    USD: { symbol: '$', rate: 0.012, active: true, lastModified: '' },
    EUR: { symbol: '€', rate: 0.011, active: true, lastModified: '' },
    RUB: { symbol: '₽', rate: 1.3, active: true, lastModified: '' }
  };

  // Загрузка сохранённых данных
  const savedRates = localStorage.getItem('currencyRates');
  if (savedRates) {
    console.log('Загруженные данные из localStorage:', savedRates);
    Object.assign(rates, JSON.parse(savedRates));
  } else {
    console.log('Нет сохранённых данных в localStorage, используются начальные значения:', rates);
  }

  // Обновление селектов
  function updateCurrencySelects() {
    const currencySelects = document.querySelectorAll('.currency-select');
    currencySelects.forEach(select => {
      const currentValue = select.value;
      select.innerHTML = '';
      Object.keys(rates).forEach(currency => {
        if (rates[currency].active) {
          const option = document.createElement('option');
          option.value = currency;
          option.textContent = `${rates[currency].symbol} ${currency}`;
          select.appendChild(option);
        }
      });
      select.value = currentValue in rates && rates[currentValue].active ? currentValue : 'INR';
    });
  }

  // Слушаем селекты
  const currencySelects = document.querySelectorAll('.currency-select');
  currencySelects.forEach(select => {
    select.addEventListener('change', () => {
      const selectedValue = select.value;
      updatePrices(selectedValue);
      currencySelects.forEach(other => {
        if (other !== select) other.value = selectedValue;
      });
    });
  });

  // Обновление цен
  function updatePrices(currency = 'INR') {
    if (!rates[currency] || !rates[currency].active) currency = 'INR';
    const { symbol, rate } = rates[currency];

    document.querySelectorAll('.price-value').forEach(el => {
      const base = parseFloat(el.dataset.inr);
      if (!isNaN(base)) {
        const converted = (base * rate).toFixed(2);
        el.textContent = converted;
      }
    });

    document.querySelectorAll('.currency-symbol').forEach(cs => {
      cs.textContent = symbol;
    });
  }

  // Конвертер суммы
  const inrInput = document.getElementById('inr-amount');
  if (inrInput) {
    inrInput.addEventListener('input', convertInputAmount);
    convertInputAmount();
  }

  function convertInputAmount() {
    const inr = parseFloat(inrInput.value) || 0;
    ['usd-result', 'eur-result', 'rub-result'].forEach(id => {
      const el = document.getElementById(id);
      const currency = id.split('-')[0].toUpperCase();
      if (el && rates[currency] && rates[currency].active) {
        el.textContent = `${rates[currency].symbol} ${(inr * rates[currency].rate).toFixed(2)}`;
      } else if (el) {
        el.textContent = `${rates[currency]?.symbol || ''} --`;
      }
    });
  }

  // Обновление даты
  function updateLastModified(currency, container) {
    const now = new Date();
    const formattedDate = now.toLocaleString('en-US', {
      month: 'numeric',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      second: 'numeric',
      hour12: true
    });
    rates[currency].lastModified = formattedDate;
    const dateEl = container.querySelector('.last-modified');
    if (dateEl) {
      dateEl.textContent = formattedDate;
    }
  }

  // Инициализация дат и actual-rate-input
  function initializeFields() {
    document.querySelectorAll('tr, .box').forEach(container => {
      const currency = container.querySelector('a.fw-bold')?.textContent;
      if (rates[currency]) {
        // Инициализация даты
        const dateEl = container.querySelector('.last-modified');
        if (dateEl && rates[currency].lastModified) {
          dateEl.textContent = rates[currency].lastModified;
        }
        // Инициализация actual-rate-input
        const rateInput = container.querySelector('.actual-rate-input');
        if (rateInput) {
          rateInput.value = rates[currency].rate;
          console.log(`Инициализация actual-rate-input для ${currency}: ${rateInput.value}`);
        }
      }
    });
  }

  // Получение курса через API (ExchangeRate-API)
  function updateExchangeRate(currency) {
    console.log(`Запрос курса для ${currency}...`);

    // Проверяем, что валюта поддерживается
    const supportedCurrencies = ['INR', 'USD', 'EUR', 'RUB'];
    if (!supportedCurrencies.includes(currency)) {
      console.error(`Валюта ${currency} не поддерживается API`);
      const mockRates = {
        INR: 1,
        USD: 0.012,
        EUR: 0.011,
        RUB: 1.3
      };
      updateRate(currency, mockRates[currency] || 0);
      return;
    }

    const apiKey = '5f803b57a97a864074823781'; // Замените на ваш ключ от ExchangeRate-API
    fetch(`https://v6.exchangerate-api.com/v6/${apiKey}/latest/INR`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ошибка: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Ответ API:', data);
        if (data.result !== 'success') {
          throw new Error('Ошибка API: ' + data['error-type']);
        }

        const apiRate = data.conversion_rates[currency];
        if (!apiRate) {
          console.error(`Курс для ${currency} не найден в ответе API`);
          const mockRates = {
            INR: 1,
            USD: 0.012,
            EUR: 0.011,
            RUB: 1.3
          };
          updateRate(currency, mockRates[currency] || 0);
          return;
        }

        console.log(`Рассчитанный курс INR/${currency}: ${apiRate}`);
        updateRate(currency, apiRate);
      })
      .catch(error => {
        console.error('Ошибка запроса:', error);
        const mockRates = {
          INR: 1,
          USD: 0.012,
          EUR: 0.011,
          RUB: 1.3
        };
        updateRate(currency, mockRates[currency] || 0);
      });
  }

  // Вспомогательная функция для обновления UI
  function updateRate(currency, apiRate) {
    console.log(`Обновление ex-rate для ${currency} с значением ${apiRate.toFixed(3)}...`);
    
    // Десктоп-версия (внутри <tr>)
    const trSelectors = document.querySelectorAll(`tr a.fw-bold[href="#"]`);
    console.log(`Найдено tr элементов для ${currency}: ${trSelectors.length}`);
    
    trSelectors.forEach(el => {
      if (el.textContent.trim() === currency) {
        const exRateEl = el.closest('tr')?.querySelector('.ex-rate');
        if (exRateEl) {
          console.log(`Обновление ex-rate (tr) для ${currency}: ${apiRate.toFixed(3)}`);
          exRateEl.textContent = apiRate.toFixed(3);
          const actualRate = parseFloat(el.closest('tr')?.querySelector('.actual-rate-input')?.value);
          exRateEl.classList.add(Math.abs(apiRate - actualRate) > 0.001 ? 'red' : 'green');
        } else {
          console.log(`Элемент ex-rate (tr) не найден для ${currency}`);
        }
      }
    });

    // Мобильная версия (внутри <div class="box">)
    const boxSelectors = document.querySelectorAll(`.box a.fw-bold[href="#"]`);
    console.log(`Найдено box элементов для ${currency}: ${boxSelectors.length}`);
    
    boxSelectors.forEach(el => {
      if (el.textContent.trim() === currency) {
        const exRateEl = el.closest('.box')?.querySelector('.ex-rate');
        if (exRateEl) {
          console.log(`Обновление ex-rate (box) для ${currency}: ${apiRate.toFixed(3)}`);
          exRateEl.textContent = apiRate.toFixed(3);
          const actualRate = parseFloat(el.closest('.box')?.querySelector('.actual-rate-input')?.value);
          exRateEl.classList.add(Math.abs(apiRate - actualRate) > 0.001 ? 'red' : 'green');
        } else {
          console.log(`Элемент ex-rate (box) не найден для ${currency}`);
        }
      }
    });
  }

  // Обработка currency-on
  document.querySelectorAll('.currency-on').forEach(checkbox => {
    const container = checkbox.closest('tr') || checkbox.closest('.box');
    const currency = container?.querySelector('a.fw-bold')?.textContent;
    if (rates[currency]) {
      checkbox.checked = rates[currency].active;
    }

    checkbox.addEventListener('change', function () {
      if (rates[currency]) {
        rates[currency].active = this.checked;
        localStorage.setItem('currencyRates', JSON.stringify(rates));
        updateLastModified(currency, container);
        updateCurrencySelects();
        updatePrices(document.querySelector('.currency-select')?.value || 'INR');
        convertInputAmount();
      }
    });
  });

  // Обработка actual-rate-input
  document.querySelectorAll('.actual-rate-input').forEach(input => {
    input.addEventListener('change', function () {
      const container = this.closest('tr') || this.closest('.box');
      const currency = container?.querySelector('a.fw-bold')?.textContent;
      const newRate = parseFloat(this.value);

      if (!currency || isNaN(newRate) || newRate <= 0) {
        alert('Введите корректное положительное число (например, 0.012).');
        this.value = rates[currency]?.rate || '';
        return;
      }

      if (rates[currency]) {
        rates[currency].rate = newRate;
        localStorage.setItem('currencyRates', JSON.stringify(rates));
        updateLastModified(currency, container);
        updatePrices(document.querySelector('.currency-select')?.value || 'INR');
        convertInputAmount();

        // Обновляем ex-rate через API для сравнения
        updateExchangeRate(currency);
      }
    });
  });

  // Кнопка Edit
  document.querySelectorAll('a[title="Edit"]').forEach(editBtn => {
    editBtn.addEventListener('click', function (e) {
      e.preventDefault();
      const container = this.closest('tr') || this.closest('.box');
      const currency = container?.querySelector('a.fw-bold')?.textContent;
      const newRate = prompt(`Введите новый курс для ${currency} (например, 0.012):`, rates[currency]?.rate);
      if (newRate !== null) {
        const parsedRate = parseFloat(newRate);
        if (isNaN(parsedRate) || parsedRate <= 0) {
          alert('Введите корректное положительное число (например, 0.012).');
          return;
        }
        rates[currency].rate = parsedRate;
        const rateInput = container.querySelector('.actual-rate-input');
        if (rateInput) rateInput.value = parsedRate;
        localStorage.setItem('currencyRates', JSON.stringify(rates));
        updateLastModified(currency, container);
        updatePrices(document.querySelector('.currency-select')?.value || 'INR');
        convertInputAmount();

        // Обновляем ex-rate через API для сравнения
        updateExchangeRate(currency);
      }
    });
  });

  // Кнопка Delete
  document.querySelectorAll('a[title="Delete"]').forEach(deleteBtn => {
    deleteBtn.addEventListener('click', function (e) {
      e.preventDefault();
      const container = this.closest('tr') || this.closest('.box');
      const currency = container?.querySelector('a.fw-bold')?.textContent;
      if (currency === 'INR') {
        alert('Нельзя удалить базовую валюту INR.');
        return;
      }
      if (confirm(`Вы уверены, что хотите удалить валюту ${currency}?`)) {
        delete rates[currency];
        localStorage.setItem('currencyRates', JSON.stringify(rates));
        container.remove();
        updateCurrencySelects();
        updatePrices(document.querySelector('.currency-select')?.value || 'INR');
        convertInputAmount();
      }
    });
  });

  // Кнопка Save
  document.querySelector('.h-list-item[href="#"][title="Save"]')?.addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.setItem('currencyRates', JSON.stringify(rates));
    alert('Изменения сохранены!');
  });

  // Инициализация
  updateCurrencySelects();
  updatePrices(currencySelects[0]?.value || 'INR');
  initializeFields();
  Object.keys(rates).forEach(currency => updateExchangeRate(currency));
});