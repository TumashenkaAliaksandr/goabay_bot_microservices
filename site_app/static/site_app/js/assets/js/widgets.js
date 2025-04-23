// Обновляем текущее время в Гоа в формате AM/PM
function updateGoaTime() {
  const now = new Date();
  const goaTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
  
  // Получаем часы и минуты
  let hours = goaTime.getHours();
  const minutes = goaTime.getMinutes().toString().padStart(2, '0');
  
  // Определяем AM или PM
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // Час в 12-часовом формате
  const formattedTime = `${hours}:${minutes} ${ampm}`;

  document.getElementById('goa-time').textContent = formattedTime;

  const dayIcon = document.getElementById('day-icon');
  dayIcon.textContent = (goaTime.getHours() >= 6 && goaTime.getHours() < 18) ? '🌞' : '🌜';
}

// Обновляем время восхода и заката в формате AM/PM
function updateSunTimes() {
  fetch('https://api.sunrisesunset.io/json?lat=15.325556&lng=74.054111')
    .then(response => response.json())
    .then(data => {
      const sunriseUTC = data.results.sunrise;
      const sunsetUTC = data.results.sunset;

      const sunriseTime = convertUTCToLocal(sunriseUTC);
      const sunsetTime = convertUTCToLocal(sunsetUTC);

      document.getElementById('sunrise-time').textContent = sunsetTime; // Время восхода
      document.getElementById('sunset-time').textContent = sunriseTime; // Время заката
    })
    .catch(error => {
      console.error('Ошибка при получении данных:', error);
    });
}

// Преобразуем время UTC из API в местное индийское время (UTC+5:30) и формат AM/PM
function convertUTCToLocal(utcTimeStr) {
  const [time, modifier] = utcTimeStr.split(' ');
  let [hours, minutes, seconds] = time.split(':').map(Number);

  if (modifier === 'PM' && hours !== 12) hours += 12;
  if (modifier === 'AM' && hours === 12) hours = 0;

  const dateUTC = new Date(Date.UTC(1970, 0, 1, hours, minutes, seconds));
  dateUTC.setMinutes(dateUTC.getMinutes() + 330); // +5:30 для индийского времени

  let localHours = dateUTC.getHours();
  const localMinutes = dateUTC.getMinutes().toString().padStart(2, '0');
  
  const ampm = localHours >= 12 ? 'PM' : 'AM';
  localHours = localHours % 12;
  localHours = localHours ? localHours : 12; // Час в 12-часовом формате

  return `${localHours}:${localMinutes} ${ampm}`;
}

// Основная функция обновления виджета
function updateWidget() {
  updateGoaTime();
  updateSunTimes();
}

// Старт при загрузке
updateWidget();
setInterval(updateWidget, 60000);

// ТВОЙ API-ключ от OpenWeatherMap
const WEATHER_API_KEY = 'c9aeb88dc3a32f57f5415395da797c10'; 

// Функция для получения и отображения погоды
function updateWeather() {
  const url = `https://api.openweathermap.org/data/2.5/weather?lat=15.325556&lon=74.054111&appid=${WEATHER_API_KEY}&units=metric&lang=en`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      const temp = Math.round(data.main.temp); // температура
      const iconCode = data.weather[0].icon; // код иконки
      const description = data.weather[0].description; // описание

      document.getElementById('weather-temp').textContent = `${temp}°C`;
      document.getElementById('weather-icon').src = `https://openweathermap.org/img/wn/${iconCode}@2x.png`; // Иконка
      document.getElementById('weather-icon').alt = description;
      document.getElementById('weather-desc').textContent = description.charAt(0).toUpperCase() + description.slice(1);
    })
    .catch(error => {
      console.error('Ошибка при получении погоды:', error);
    });
}

// Вызов при загрузке и периодическое обновление
updateWeather();
setInterval(updateWeather, 60 * 60 * 1000); // обновлять каждый час
