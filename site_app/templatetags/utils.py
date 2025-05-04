import random

from django import template
from django.forms import BoundField

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


def get_rating_breakdown(ratings):
    # ratings - список оценок от 0 до 100
    breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in ratings:
        # Переводим рейтинг в звезды (от 1 до 5)
        if r == 100:
            star = 5
        else:
            star = max(1, (r - 1) // 20 + 1)
        breakdown[star] += 1
    total = len(ratings)
    result = []
    for star in range(5, 0, -1):
        count = breakdown[star]
        percent = (count / total * 100) if total else 0
        result.append({
            'star': star,
            'count': count,
            'percent': round(percent),
        })
    return result


@register.filter(name='add_class')
def add_class(field, css):
    if isinstance(field, BoundField):
        return field.as_widget(attrs={"class": css})
    return field


@register.filter
def average_rating(reviews):
    total = len(reviews)
    if total == 0:
        return 0
    sum_rating = sum(review.rating for review in reviews)
    return sum_rating / total


# templatetags/custom_filters.py
@register.filter
def filter_by_category(products, category):
    return products.filter(category=category)


@register.filter
def random_increase(value):
    try:
        value = float(value)
        increase = random.uniform(0, 13)
        increased_value = value + increase
        return "{:.2f}".format(increased_value)  # Форматировать до 2 десятичных знаков
    except (ValueError, TypeError):
        return value
