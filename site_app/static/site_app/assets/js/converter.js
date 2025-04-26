document.addEventListener('DOMContentLoaded', () => {
  const baseCurrency = 'INR';
  const apiURL = `https://open.er-api.com/v6/latest/${baseCurrency}`;

  const inrInput = document.getElementById('inr-amount');
  const usdResult = document.getElementById('usd-result');
  const eurResult = document.getElementById('eur-result');
  const rubResult = document.getElementById('rub-result');

  let conversionRates = {};

  function fetchRates() {
    fetch(apiURL)
      .then(response => response.json())
      .then(data => {
        if (data.result === 'success') {
          conversionRates = data.rates;
          updateConvertedResults();
        } else {
          console.error('API error:', data['error-type']);
          setErrorResults();
        }
      })
      .catch(err => {
        console.error('Fetch error:', err);
        setErrorResults();
      });
  }

  function updateConvertedResults() {
    const inrAmount = parseFloat(inrInput.value);
    if (isNaN(inrAmount) || inrAmount < 0) {
      setErrorResults();
      return;
    }

    usdResult.textContent = conversionRates.USD
      ? `$ ${(inrAmount * conversionRates.USD).toFixed(2)}`
      : '$ --';

    eurResult.textContent = conversionRates.EUR
      ? `€ ${(inrAmount * conversionRates.EUR).toFixed(2)}`
      : '€ --';

    rubResult.textContent = conversionRates.RUB
      ? `₽ ${(inrAmount * conversionRates.RUB).toFixed(2)}`
      : '₽ --';
  }

  function setErrorResults() {
    usdResult.textContent = '$ --';
    eurResult.textContent = '€ --';
    rubResult.textContent = '₽ --';
  }

  // Обновляем результаты при изменении суммы
  inrInput.addEventListener('input', updateConvertedResults);

  // Загружаем курсы при старте
  fetchRates();

  // Обновляем курсы каждый час
  setInterval(fetchRates, 60 * 60 * 1000);
});
