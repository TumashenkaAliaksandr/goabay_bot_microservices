from rest_framework import serializers

from bot_app.models import VariantImage, ProductVariant, ProductImage, Product


class VariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = ['id', 'image']

class ProductVariantSerializer(serializers.ModelSerializer):
    additional_images = VariantImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'description', 'sku', 'size', 'color',
            'price', 'quantity', 'image', 'additional_images',
        ]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    additional_images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    # Теги и Категории передаем только id и name (или slug), например:
    tags = serializers.StringRelatedField(many=True)  # если __str__ реализован в Tag
    category = serializers.StringRelatedField(many=True)
    brand = serializers.StringRelatedField()  # если нужно просто имя бренда

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'model', 'brand', 'image', 'desc', 'additional_description',
            'price', 'discount', 'warranty_period', 'shelf_life', 'certification',
            'length', 'width', 'height', 'gross_weight', 'net_volume', 'color', 'aroma',
            'material_up', 'material', 'capacity', 'processor', 'internal_storage',
            'screen_size', 'battery_capacity', 'resolution', 'interface', 'power_consumption',
            'gender', 'age_group', 'sizes', 'clothing_fit', 'skin_type', 'hair_type',
            'effect', 'application_area', 'ingredients', 'calories', 'nutritional_value',
            'organic', 'vegan', 'gluten_free', 'additives', 'engine_type', 'fuel_type',
            'vehicle_compatibility', 'transmission', 'horsepower', 'torque', 'style',
            'barcode', 'upc', 'launch_date', 'energy_efficiency', 'reusability', 'eco_label',
            'quantity', 'show_quantity', 'stock_status', 'restock_date', 'rating', 'reviews_count',
            'meta_title', 'meta_description', 'tags', 'category',
            'is_popular', 'is_index', 'is_site_bar', 'is_sale', 'is_new_product', 'is_main_slider',
            'additional_images', 'variants',
        ]

