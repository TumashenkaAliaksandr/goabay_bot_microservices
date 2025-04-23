document.addEventListener('DOMContentLoaded', function () {
  const rates = {
    INR: { symbol: '₹', rate: 1 },
    USD: { symbol: '$', rate: 0.012 },
    EUR: { symbol: '€', rate: 0.011 },
    RUB: { symbol: '₽', rate: 1.3 }
  };

  // Слушаем ВСЕ элементы с классом .currency-select
  const currencySelects = document.querySelectorAll('.currency-select');
  currencySelects.forEach(select => {
    select.addEventListener('change', () => {
      const selectedValue = select.value;
      updatePrices(selectedValue);
      // Синхронизировать другие селекты
      currencySelects.forEach(other => {
        if (other !== select) other.value = selectedValue;
      });
    });
  });

  // Обновление цен
  function updatePrices(currency = 'INR') {
    const { symbol, rate } = rates[currency];

    document.querySelectorAll('.price-value').forEach(el => {
      const base = parseFloat(el.dataset.inr);
      const converted = (base * rate).toFixed(2);
      el.textContent = converted;
    });

    document.querySelectorAll('.currency-symbol').forEach(cs => {
      cs.textContent = symbol;
    });
  }

  // Инициализация на старте
  updatePrices(currencySelects[0]?.value || 'INR');

  // Блок конвертера суммы (если есть)
  const inrInput = document.getElementById('inr-amount');
  if (inrInput) {
    inrInput.addEventListener('input', convertInputAmount);
    convertInputAmount();
  }

  function convertInputAmount() {
    const inr = parseFloat(inrInput.value) || 0;
    if (document.getElementById('usd-result'))
      document.getElementById('usd-result').textContent = `${rates.USD.symbol} ${(inr * rates.USD.rate).toFixed(2)}`;
    if (document.getElementById('eur-result'))
      document.getElementById('eur-result').textContent = `${rates.EUR.symbol} ${(inr * rates.EUR.rate).toFixed(2)}`;
    if (document.getElementById('rub-result'))
      document.getElementById('rub-result').textContent = `${rates.RUB.symbol} ${(inr * rates.RUB.rate).toFixed(2)}`;
  }
});

