from rest_framework import serializers
from .models import SubscribedProduct

class SubscribedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribedProduct
        fields = ['id', 'product_id', 'product_name', 'subscribed_at']
