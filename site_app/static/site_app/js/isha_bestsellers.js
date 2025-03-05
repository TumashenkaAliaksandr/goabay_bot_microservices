// fetch('/product_ishalife.json/')
//     .then(response => {
//         if (!response.ok) {
//             throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
//         }
//         return response.json();
//     })
//     .then(data => {
//         if (Array.isArray(data)) {
//             const productsCarousel = document.getElementById('products-carousel');
//             if (!productsCarousel) {
//                 console.error('Элемент #products-carousel не найден');
//                 return;
//             }
//
//             data.forEach(product => {
//                 if (!product.name || !product.link || !product.image_src || !product.rating || !product.price) {
//                     console.error('Недостаточно данных для продукта:', product);
//                     return;
//                 }
//
//                 // Создаем контейнер для одного продукта
//                 const productDiv = document.createElement('div');
//                 productDiv.classList.add('single-product');
//
//                 // Создаем блок с изображениями
//                 const proImgDiv = document.createElement('div');
//                 proImgDiv.classList.add('pro-img');
//
//                 const productLink = document.createElement('a');
//                 productLink.href = product.link;
//
//                 const primaryImg = document.createElement('img');
//                 primaryImg.classList.add('primary-img');
//                 primaryImg.src = product.image_src;
//                 primaryImg.alt = 'single-product';
//
//                 const secondaryImg = document.createElement('img');
//                 secondaryImg.classList.add('secondary-img');
//                 secondaryImg.src = product.image_src;
//                 secondaryImg.alt = 'single-product';
//
//                 productLink.appendChild(primaryImg);
//                 productLink.appendChild(secondaryImg);
//                 proImgDiv.appendChild(productLink);
//
//                 // Создаем блок с контентом продукта
//                 const proContentDiv = document.createElement('div');
//                 proContentDiv.classList.add('pro-content');
//
//                 // Блок с рейтингом
//                 const productRatingDiv = document.createElement('div');
//                 productRatingDiv.classList.add('product-rating');
//                 productRatingDiv.innerHTML = getStars(product.rating);
//
//                 // Название и цена продукта
//                 const productTitle = document.createElement('h4');
//                 const productLinkTitle = document.createElement('a');
//                 productLinkTitle.href = product.link;
//                 productLinkTitle.textContent = product.name;
//                 productTitle.appendChild(productLinkTitle);
//
//                 const productPrice = document.createElement('p');
//                 const priceSpan = document.createElement('span');
//                 priceSpan.classList.add('price');
//                 priceSpan.textContent = product.price;
//                 const prevPriceDel = document.createElement('del');
//                 prevPriceDel.classList.add('prev-price');
//                 prevPriceDel.textContent = '$32.00';
//                 productPrice.appendChild(priceSpan);
//                 productPrice.appendChild(prevPriceDel);
//
//                 // Блок с действиями (добавить в корзину, сравнить и т.д.)
//                 const proActionsDiv = document.createElement('div');
//                 proActionsDiv.classList.add('pro-actions');
//
//                 const actionsSecondaryDiv = document.createElement('div');
//                 actionsSecondaryDiv.classList.add('actions-secondary');
//
//                 const wishlistLink = document.createElement('a');
//                 wishlistLink.href = '#';
//                 wishlistLink.dataset.toggle = 'tooltip';
//                 wishlistLink.title = 'Add to Wishlist';
//                 const wishlistIcon = document.createElement('i');
//                 wishlistIcon.classList.add('fa', 'fa-heart');
//                 wishlistLink.appendChild(wishlistIcon);
//
//                 const addCartLink = document.createElement('a');
//                 addCartLink.classList.add('add-cart');
//                 addCartLink.href = '#';
//                 addCartLink.dataset.toggle = 'tooltip';
//                 addCartLink.title = 'Add to Cart';
//                 addCartLink.textContent = 'Add To Cart';
//
//                 const compareLink = document.createElement('a');
//                 compareLink.href = '#';
//                 compareLink.dataset.toggle = 'tooltip';
//                 compareLink.title = 'Add to Compare';
//                 const compareIcon = document.createElement('i');
//                 compareIcon.classList.add('fa', 'fa-signal');
//                 compareLink.appendChild(compareIcon);
//
//                 actionsSecondaryDiv.appendChild(wishlistLink);
//                 actionsSecondaryDiv.appendChild(addCartLink);
//                 actionsSecondaryDiv.appendChild(compareLink);
//
//                 proActionsDiv.appendChild(actionsSecondaryDiv);
//
//                 // Собираем блок контента продукта
//                 proContentDiv.appendChild(productRatingDiv);
//                 proContentDiv.appendChild(productTitle);
//                 proContentDiv.appendChild(productPrice);
//                 proContentDiv.appendChild(proActionsDiv);
//
//                 // Добавляем стикер (если нужен)
//                 const stickerNewSpan = document.createElement('span');
//                 stickerNewSpan.classList.add('sticker-new');
//                 stickerNewSpan.textContent = '-32%';
//
//                 // Собираем весь продукт
//                 productDiv.appendChild(proImgDiv);
//                 productDiv.appendChild(proContentDiv);
//                 productDiv.appendChild(stickerNewSpan);
//
//                 // Добавляем продукт в карусель
//                 productsCarousel.appendChild(productDiv);
//             });
//
//             // Инициализация Owl Carousel после добавления всех продуктов
//             $(document).ready(function(){
//                 $("#products-carousel").owlCarousel({
//                     loop: true,
//                     margin: 10,
//                     nav: true,
//                     responsive: {
//                         0: {
//                             items: 1
//                         },
//                         600: {
//                             items: 3
//                         },
//                         1000: {
//                             items: 5
//                         }
//                     }
//                 });
//             });
//         } else {
//             console.error('Ответ не является массивом:', data);
//         }
//     })
//     .catch(error => console.error('Ошибка при загрузке данных:', error));
//
// // Функция для генерации звезд рейтинга
// function getStars(rating) {
//     if (rating === "Рейтинг отсутствует") {
//         return '';
//     } else {
//         const stars = rating.split(' ')[0];
//         let starHTML = '';
//         for (let i = 0; i < 5; i++) {
//             if (i < parseInt(stars)) {
//                 starHTML += '<i class="fa fa-star"></i>';
//             } else {
//                 starHTML += '<i class="fa fa-star-o"></i>';
//             }
//         }
//         return starHTML;
//     }
// }
