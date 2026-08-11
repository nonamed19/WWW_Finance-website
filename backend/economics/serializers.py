from rest_framework import serializers
from .models import NewsList

class NewsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsList
        fields = '__all__'
