
/*================================================
[  Table of contents  ]
==================================================
 1. Newsletter Popup
 2. Mobile Menu Activation
 3 Checkout Page Activation
 4. NivoSlider Activation
 5. New Products Activation
 6. New Upsell Product Activation
 7. Side Product Activation
 8. Best Seller Activation
 9. Hand Tool Activation
 10. Brand Banner Activation
 11. Blog Activation
 12. Blog two Activation
 13. WOW Js Activation
 14. ScrollUp Activation
 15. Sticky-Menu Activation
 16. Price Slider Activation
 17. Testimonial Slick Carousel
 18. Best Seller Activation
 19. Best Product Activation
 20. Blog Realted Post activation
 21.Best Seller  Unique Activation



================================================*/

(function ($) {
    "use Strict";
    /*--------------------------
    1. Newsletter Popup
    ---------------------------*/
    // setTimeout(function () {
    //     $('.popup_wrapper').css({
    //         "opacity": "1",
    //         "visibility": "visible"
    //     });
    //     $('.popup_off').on('click', function () {
    //         $(".popup_wrapper").fadeOut(500);
    //     })
    // }, 2500);
    /* Newsletter Popup JavaScript */
    setTimeout(function () {
        // Проверяем, если пользователь уже выбрал "Don't show this popup again"
        if (localStorage.getItem('newsletter_subscription') !== 'subscribed') {
            // Показываем окно, если пользователь не выбрал "Don't show this popup again"
            $('.popup_wrapper').css({
                "opacity": "1",
                "visibility": "visible"
            });

            $('.popup_off').on('click', function () {
                $(".popup_wrapper").fadeOut(500);
            });

            $("form").on('submit', function (e) {
                e.preventDefault();
                var email = $("#message").val();
                var checkbox = $('#newsletter-permission').prop('checked');

                // Получаем CSRF токен из мета-тега
                var csrfToken = document.querySelector('[name="csrf-token"]').content;

                // Отправляем AJAX запрос на сервер
                $.ajax({
                    type: 'POST',
                    url: '/newsletter-signup/',
                    data: {
                        email: email,
                        csrfmiddlewaretoken: csrfToken,
                        permission: checkbox
                    },
                    success: function (response) {
                        if (response.status === 'success') {
                            $(".popup_wrapper").fadeOut(500);
                            alert('You have successfully subscribed!');
                        } else {
                            alert('There was an error with your subscription.');
                        }
                    },
                    error: function () {
                        alert('There was an error with your subscription.');
                    }
                });
            });
        }
    }, 2500);

    /* Checking checkbox and setting cookie */
    $('#newsletter-permission').on('change', function () {
        if ($(this).is(':checked')) {
            // Сохраняем выбор пользователя в localStorage
            localStorage.setItem('newsletter_subscription', 'subscribed');
        } else {
            localStorage.removeItem('newsletter_subscription');
        }
    });



// Показывать всплывающее окно, только если в localStorage нет данных о подписке
    if (!localStorage.getItem('newsletter_subscription')) {
        setTimeout(function () {
            $('.popup_wrapper').css({
                "opacity": "1",
                "visibility": "visible"
            });
        }, 2500);
    }



    /*----------------------------
    2. Mobile Menu Activation
    -----------------------------*/
    jQuery('.mobile-menu nav').meanmenu({
        meanScreenWidth: "991",
    });

    /*----------------------------
    3 Checkout Page Activation
    -----------------------------*/
     $('.categorie-title').on('click', function () {
    $('.vertical-menu-list').slideToggle();
    });

    $('#showlogin').on('click', function () {
        $('#checkout-login').slideToggle();
    });
    $('#showcoupon').on('click', function () {
        $('#checkout_coupon').slideToggle();
    });
    $('#cbox').on('click', function () {
        $('#cbox_info').slideToggle();
    });
    $('#ship-box').on('click', function () {
        $('#ship-box-info').slideToggle();
    });

    /*----------------------------
    4. NivoSlider Activation
    -----------------------------*/
    $('#slider').nivoSlider({
    effect: 'random', // Эффект смены слайдов
    animSpeed: 300, // Скорость анимации (мс)
    pauseTime: 7000, // Время показа одного слайда (мс)
    directionNav: false, // Убираем кнопки "вперед/назад"
    controlNavThumbs: false, // Убираем миниатюры
    pauseOnHover: true, // Остановка при наведении
    controlNav: true, // Показывать точки навигации
    prevText: "<i class='zmdi zmdi-chevron-left'></i>",
    nextText: "<i class='zmdi zmdi-chevron-right'></i>",
    manualAdvance: false // Включаем автоматическое перелистывание
});


    /*----------------------------------------------------
    5. New Products Activation
    -----------------------------------------------------*/
    $('.new-pro-active').owlCarousel({
            loop: true,
            nav: true,
            dots: false,
            smartSpeed: 1000,

            navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
            margin: 30,
            responsive: {
                0: {
                    items: 1,
                    autoplay:true
                },
                480: {
                    items: 2
                },
                768: {
                    items: 2
                },
                1000: {
                    items: 2
                },
                1200: {
                    items: 3
                }
            }

        })
    $('.new-pro-active-two').owlCarousel({
            loop: true,
            nav: true,
            dots: false,
            smartSpeed: 1000,

            navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
            margin: 30,
            responsive: {
                0: {
                    items: 1,
                    autoplay:true
                },
                480: {
                    items: 2
                },
                768: {
                    items: 2
                },
                1000: {
                    items: 3
                },
                1200: {
                    items: 5
                }
            }

        })
    /*----------------------------------------------------
    6. New Upsell Product Activation
    -----------------------------------------------------*/
    $('.new-upsell-pro').owlCarousel({
            loop: false,
            nav: true,
            dots: false,
            smartSpeed: 1000,

            navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
            margin: 30,
            responsive: {
                0: {
                    items: 1,
                    autoplay:true
                },
                480: {
                    items: 2
                },
                768: {
                    items: 2
                },
                1000: {
                    items: 3
                },
                1200: {
                    items: 4
                }
            }

        })

    /*----------------------------------------------------
    7. Side Product Activation
    -----------------------------------------------------*/
    $('.side-product-list-active')
        .on('changed.owl.carousel initialized.owl.carousel', function (event) {
            $(event.target)
                .find('.owl-item').removeClass('last')
                .eq(event.item.index + event.page.size - 1).addClass('last');
        }).owlCarousel({
            loop: true,
            nav: true,
            dots: false,
            smartSpeed: 1500,
            autoplay: true, // Автоматическое воспроизведение
            autoplayTimeout: 6000, // Время между слайдами (2 секунды)
            autoplayHoverPause: true, // Остановка при наведении
            rtl: true,
            navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
            margin: 1,
            responsive: {
                0: {
                    items: 1,
                    autoplay:true
                },
               480: {
                    items: 2
                },
                768: {
                    items: 2
                },
                991: {
                    items: 1
                }
            }
        })

    /*----------------------------------------------------
    8. Best Seller Activation
    -----------------------------------------------------*/
    $('.best-seller-pro-active')
        .on('changed.owl.carousel initialized.owl.carousel', function (event) {
            $(event.target)
                .find('.owl-item').removeClass('last')
                .eq(event.item.index + event.page.size - 1).addClass('last');
        }).owlCarousel({
            loop: true,
            nav: true,
            dots: false,
            smartSpeed: 1200,
            autoplay: true, // Автоматическое воспроизведение
            autoplayTimeout: 4000, // Время между слайдами (2 секунды)
            autoplayHoverPause: true, // Остановка при наведении
            navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
            margin: 1,
            responsive: {
                0: {
                    items: 1,
                    autoplay:true
                },
                480: {
                    items: 2
                },
                768: {
                    items: 2
                },
                992: {
                    items: 3
                },
                1200: {
                    items: 4
                }
            }
        })

    $('.best-seller-pro-active-product')
        .on('changed.owl.carousel initialized.owl.carousel', function (event) {
            $(event.target)
                .find('.owl-item').removeClass('last')
                .eq(event.item.index + event.page.size - 1).addClass('last');
        }).owlCarousel({
            loop: true,
            nav: false,
            dots: false,
            smartSpeed: 500,
            autoplay: true, // Автоматическое воспроизведение
            autoplayTimeout: 4600, // Время между слайдами (3 секунды)
            autoplayHoverPause: false, // Остановка при наведении
            navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
            margin: 1,
            responsive: {
                0: {
                    items: 1,
                    autoplay:true
                },
                480: {
                    items: 2
                },
                768: {
                    items: 2
                },
                992: {
                    items: 3
                },
                1200: {
                    items: 4
                },
                1300: {
                    items: 5
                },
                1400: {
                    items: 6
                },
                1500: {
                    items: 7
                },
            }
        })


    /*----------------------------------------------------
    9. Hand Tool Activation
    -----------------------------------------------------*/
    $('.hand-tool-active').owlCarousel({
            loop: false,
            nav: true,
            dots: false,
            smartSpeed: 1200,
            navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
            margin: 30,
            responsive: {
                0: {
                    items: 1,
                    autoplay:true
                },
                480: {
                    items: 2
                },
                768: {
                    items: 3
                },
                992: {
                    items: 3
                },
                1200: {
                    items: 4
                }
            }
    })
    /*----------------------------------------------------
    10. Brand Banner Activation
    -----------------------------------------------------*/
    $('.brand-banner').on('changed.owl.carousel initialized.owl.carousel', function (event) {
        $(event.target)
            .find('.owl-item').removeClass('last')
            .eq(event.item.index + event.page.size - 1).addClass('last');

        $(event.target)
            .find('.owl-item').removeClass('first')
            .eq(event.item.index).addClass('first')
    }).owlCarousel({
        loop: true,
        nav: false, // Включить навигацию
        dots: false,
        smartSpeed: 1200,
        navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"], // Круглые стрелочки
        margin: 1,
        autoplay: true, // Автоматическое воспроизведение
        autoplayTimeout: 3000, // Время между слайдами
        responsive: {
            0: {
                items: 1,
                autoplay: true
            },
            480: {
                items: 3
            },
            768: {
                items: 4
            },
            1000: {
                items: 5
            }
        }
    })


    /*----------------------------------------------------
    11. Blog Activation
    -----------------------------------------------------*/
    $('.blog-active').owlCarousel({
        loop: false,
        nav: true,
        dots: false,
        smartSpeed: 1000,
        navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
        margin: 30,
        responsive: {
            0: {
                items: 1,
                autoplay:true
            },
            768: {
                items: 2
            },
            1000: {
                items: 3
            }
        }
    })
    /*----------------------------------------------------
    12. Blog two Activation
    -----------------------------------------------------*/
    $('.blog-active2').owlCarousel({
        loop: false,
        nav: true,
        dots: false,
        smartSpeed: 1000,
        navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
        margin: 30,
        responsive: {
            0: {
                items: 1,
                autoplay:true
            },
            768: {
                items: 2
            },
            1000: {
                items: 2
            }
        }
    })
    /*----------------------------
    13. WOW Js Activation
    -----------------------------*/
    new WOW().init();

    /*----------------------------
    14. ScrollUp Activation
    -----------------------------*/
    $.scrollUp({
        scrollName: 'scrollUp', // Element ID
        topDistance: '550', // Distance from top before showing element (px)
        topSpeed: 1000, // Speed back to top (ms)
        animation: 'fade', // Fade, slide, none
        scrollSpeed: 900,
        animationInSpeed: 1000, // Animation in speed (ms)
        animationOutSpeed: 1000, // Animation out speed (ms)
        scrollText: '<i class="fa fa-angle-up"></i>', // Text for element
        activeOverlay: false // Set CSS color to display scrollUp active point, e.g '#00FFFF'
    });

    /*----------------------------
    15. Sticky-Menu Activation
    ------------------------------ */
    $(window).on('scroll', function () {
        if ($(this).scrollTop() > 150) {
            $('.header-sticky').addClass("sticky");
        } else {
            $('.header-sticky').removeClass("sticky");
        }
    });

    /*----------------------------
    16. Price Slider Activation
    -----------------------------*/
    $("#slider-range").slider({
        range: true,
        min: 0,
        max: 80,
        values: [0, 74],
        slide: function (event, ui) {
            $("#amount").val("$" + ui.values[0] + "  $" + ui.values[1]);
        }
    });
    $("#amount").val("$" + $("#slider-range").slider("values", 0) +
        "  $" + $("#slider-range").slider("values", 1));

    /*--------------------------------
    17. Testimonial Slick Carousel
    -----------------------------------*/
    $('.testext_active').owlCarousel({
        loop: false,
        navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
        margin: 15,
        smartSpeed: 1000,
        nav: true,
        dots: true,
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 1
            },
            1000: {
                items: 1
            }
        }
    })

    /*----------------------------------------------------
    18. Best Seller Activation
    -----------------------------------------------------*/
    $('.best-seller-pro').on('changed.owl.carousel initialized.owl.carousel', function (event) {
        $(event.target)
                .find('.owl-item').removeClass('last')
                .eq(event.item.index + event.page.size - 1).addClass('last');
        }).owlCarousel({
        loop: false,
        nav: true,
        dots: false,
        smartSpeed: 1000,
        navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
        margin: 0,
        responsive: {
            0: {
                items: 1,
                autoplay:true
            },
            480: {
                items: 2
            },
            768: {
                items: 2
            },
            1000: {
                items: 1
            }
        }
    })
    /*----------------------------------------------------
    19. Best Product Activation
    -----------------------------------------------------*/
    $('.best-seller-pro-two')
        .owlCarousel({
            loop: true,
            nav: false,
            dots: false,
            smartSpeed: 1200,
            margin: 0,
            responsive: {
                0: {
                    items: 1,
                    autoplay:true
                },
                768: {
                    items: 3
                },
                1000: {
                    items: 1
                }
            }
        })
    
    /*-------------------------------------
    20. Blog Realted Post activation
    --------------------------------------*/
    $('.blog-related-post-active').owlCarousel({
        loop: false,
        margin: 30,
        smartSpeed: 1000,
        nav: false,
        dots: false,
        items: 2,
        responsive: {
            0: {
                items: 1,
                autoplay:true
            },
            480: {
                items: 1
            },
            768: {
                items: 2
            },
            992:{
                margin: 29,
                items: 2
            },
            1200: {
                items: 2
            }
        }
    })
    
    /*----------------------------------------------------
    21.Best Seller  Unique Activation
    -----------------------------------------------------*/
    $('.best-seller-unique').on('changed.owl.carousel initialized.owl.carousel', function (event) {
        $(event.target)
                .find('.owl-item').removeClass('last')
                .eq(event.item.index + event.page.size - 1).addClass('last');
        }).owlCarousel({
        loop: true,
        nav: true,
        dots: false,
        smartSpeed: 1000,
        navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
        margin: 0,
        responsive: {
            0: {
                items: 1,
                autoplay:true
            },
            768: {
                items: 2
            },
            1000: {
                items: 1
            }
        }
    })

    /*----------------------------------------------------
    22.Slider Control  Unique Activation
    -----------------------------------------------------*/

    document.addEventListener('DOMContentLoaded', function () {
        const sliders = document.querySelectorAll('.slider');

        sliders.forEach(slider => {
            const slides = slider.querySelectorAll('.slide');
            const controls = slider.closest('.single-banner-index-two').querySelectorAll('.slider-control');
            let currentSlide = 0;

            function showSlide(index) {
                slides[currentSlide].classList.remove('active');
                controls[currentSlide].classList.remove('active');
                currentSlide = index;
                slides[currentSlide].classList.add('active');
                controls[currentSlide].classList.add('active');
            }

            controls.forEach((control, index) => {
                control.addEventListener('click', () => showSlide(index));
            });

            // Автоматическое переключение слайдов
            setInterval(() => {
                showSlide((currentSlide + 1) % slides.length);
            }, 4000);
        });
    });





     
    
})(jQuery);