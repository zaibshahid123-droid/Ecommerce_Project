from rest_framework import serializers
from django.urls import reverse
from .models import Item


class ItemSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    category = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=2000, required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(min_value=0)
    discount_percent = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    is_on_sale = serializers.BooleanField(read_only=True)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            url = reverse('item_image', kwargs={'pk': str(obj.id)})
            return request.build_absolute_uri(url) if request else url
        return None

    def create(self, validated_data):
        return Item(**validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance