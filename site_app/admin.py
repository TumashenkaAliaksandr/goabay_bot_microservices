from django.contrib import admin

from bot_app.models import ProductImage, Review
from site_app.models import Category, Brand, SocialNetwork, InfoFooter, FooterNavItem, VerticalMenu, VerticalMenuName


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')  # Отображаем имя и родительскую категорию
    list_filter = ('parent',)  # Фильтрация по родительской категории
    search_fields = ('name',)  # Поиск по имени категории


# Регистрация модели Category с настройками админки
admin.site.register(Category, CategoryAdmin)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Количество пустых форм для добавления новых изображений


admin.site.register(ProductImage)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'image', 'created_at', 'link']
    ordering = ['-created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'product_slug', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'product_slug')
    search_fields = ('author_name', 'review_text', 'product_slug')
    ordering = ('-created_at',)


@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name',)


@admin.register(FooterNavItem)
class FooterNavItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order')
    list_editable = ('order',)
    ordering = ('order',)
    search_fields = ('title', 'url')

class FooterNavItemInline(admin.TabularInline):
    model = InfoFooter.nav_items.through
    extra = 1

@admin.register(InfoFooter)
class InfoFooterAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'phone', 'email')
    inlines = [FooterNavItemInline]
    exclude = ('nav_items',)  # Чтобы избежать дублирования ManyToMany в форме
    fieldsets = (
        (None, {
            'fields': ('logo', 'svg_icon', 'copyright', 'phone', 'email')
        }),
    )

@admin.register(VerticalMenuName)
class VerticalMenuNameAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(VerticalMenu)
class VerticalMenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'link')
    search_fields = ('name',)