document.addEventListener("DOMContentLoaded", function () {
  const countryList = [
    "United States", "United Kingdom", "Australia", "Canada", "Germany", "France", "Japan", "Singapore", "Malaysia",
    "United Arab Emirates", "Saudi Arabia", "South Korea", "Thailand", "Indonesia", "Brazil", "Russia", "China",
    "Sri Lanka", "Bangladesh", "Kuwait", "Philippines", "Italy", "Spain", "Netherlands", "South Africa", "Nigeria",
    "Kenya", "New Zealand", "Argentina", "Chile", "Pakistan", "Nepal", "Vietnam", "Hong Kong", "Qatar", "Oman",
    "Bahrain", "Belgium", "Denmark", "Finland", "Ireland", "Norway", "Sweden", "Switzerland", "Turkey", "Egypt",
    "Morocco", "Algeria", "Colombia", "Peru", "Mexico", "Afghanistan", "Bhutan", "Brunei", "Hungary", "Poland",
    "Portugal", "Austria", "Czech Republic", "Greece", "Iceland", "Kuwait", "Bulgaria", "Romania", "Slovakia",
    "Slovenia", "Croatia", "Estonia", "Latvia", "Lithuania", "Malta", "Cyprus", "Luxembourg", "Barbados", "Bermuda",
    "Cayman Islands", "Cuba", "El Salvador", "Panama", "Ecuador", "Venezuela", "Uruguay", "Paraguay", "Bolivia",
    "Ghana", "Ethiopia", "Eritrea", "Democratic Republic of Congo", "Cape Verde", "Mauritius", "Namibia", "Niger",
    "Fiji", "Maldives", "Jordan", "Lebanon", "Israel", "Iran", "Iraq", "Yemen", "Brunei", "Myanmar", "Cambodia",
    "Laos", "Mongolia", "Macau", "Taiwan", "Albania", "Andorra", "Armenia", "Azerbaijan", "Belarus",
    "Bosnia and Herzegovina", "Georgia", "Kazakhstan", "Kyrgyzstan", "Moldova", "Monaco", "Montenegro",
    "North Macedonia", "San Marino", "Serbia", "Ukraine", "Uzbekistan", "Vatican City"
  ];

  const countrySelect = document.getElementById("shipping-country");
  if (!countrySelect) {
    console.warn("Элемент #shipping-country не найден в DOM.");
    return;
  }

  // Очищаем список, если вдруг там уже есть опции
  countrySelect.innerHTML = "";

  // Добавляем опцию по умолчанию
  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "Select a country";
  defaultOption.disabled = true;
  defaultOption.selected = true;
  countrySelect.appendChild(defaultOption);

  // Заполнение списка стран
  countryList.forEach(country => {
    const option = document.createElement("option");
    option.value = country;
    option.textContent = country;
    countrySelect.appendChild(option);
  });

  // Установка страны по умолчанию (если она есть в списке)
  const defaultCountry = "Vietnam";
  if (countryList.includes(defaultCountry)) {
    countrySelect.value = defaultCountry;
    defaultOption.selected = false;
  }

  // Обработка изменения страны
  countrySelect.addEventListener("change", function () {
    const selectedCountry = this.value;
    console.log("Selected country:", selectedCountry);
    // updateShippingCost(selectedCountry); // Здесь ваш код для обновления стоимости доставки
  });
});
