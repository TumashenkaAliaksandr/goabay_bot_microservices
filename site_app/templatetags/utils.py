from django import template

register = template.Library()

@register.filter
def rating_to_stars(rating):
    if rating is None:
        return ['fa fa-star-o'] * 5  # Возвращаем пустые звезды, если рейтинг отсутствует
    rating = float(rating)
    stars = []
    for i in range(5):
        if rating >= (i + 1) * 20:
            stars.append('fa fa-star')
        elif rating >= i * 20 + 10:
            stars.append('fa fa-star-half-o')
        else:
            stars.append('fa fa-star-o')
    return stars
