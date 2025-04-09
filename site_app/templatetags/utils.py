import random

from django import template

register = template.Library()

@register.filter
def rating_to_stars(rating):
    if rating is None or isinstance(rating, str) and rating.lower() == 'рейтинг отсутствует':
        return ['fa fa-star-o'] * 5  # Возвращаем пустые звезды, если рейтинг отсутствует
    try:
        rating = float(rating)
    except ValueError:
        return ['fa fa-star-o'] * 5  # Возвращаем пустые звезды, если рейтинг не является числом
    stars = []
    for i in range(5):
        if rating >= (i + 1) * 20:
            stars.append('fa fa-star')
        elif rating >= i * 20 + 10:
            stars.append('fa fa-star-half-o')
        else:
            stars.append('fa fa-star-o')
    return stars

@register.filter
def normalize_rating(rating):
    try:
        rating = float(rating)
        return round(rating / 20, 1)
    except (ValueError, TypeError):
        return 0.0


@register.filter
def random_increase(value):
    try:
        value = float(value)
        increase = random.uniform(0, 13)
        increased_value = value + increase
        return "{:.2f}".format(increased_value)  # Форматировать до 2 десятичных знаков
    except (ValueError, TypeError):
        return value