from rest_framework import serializers
from .models import ExchangeList


class ExchangeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeList
        fields = '__all__'
