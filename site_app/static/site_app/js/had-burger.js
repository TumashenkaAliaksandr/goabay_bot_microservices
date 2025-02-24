document.addEventListener('DOMContentLoaded', function() {
    const burgerIcon = document.querySelector('.burger-icon');
    const burgerList = document.querySelector('.burger-list');

    burgerIcon.addEventListener('click', function() {
        burgerIcon.classList.toggle('active');
        burgerList.classList.toggle('show');
    });
});
