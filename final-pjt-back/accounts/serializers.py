from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)  # 프로필 이미지 처리

    class Meta:
        model = User
        fields = [
            'id', 'username', 'name', 'email', 'age', 'money', 'salary',
            'desire_amount_deposit', 'deposit_period',
            'desire_amount_saving', 'saving_period', 'profile_image'
        ]  # 필요한 필드만 포함

        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if instance.profile_image and request:
            data['profile_image'] = request.build_absolute_uri(instance.profile_image.url)
        else:
            data['profile_image'] = None
        return data

    def validate_age(self, value):
        if value and value < 0:
            raise serializers.ValidationError("Age cannot be negative.")
        return value

    def validate(self, data):
        if data.get('money') and data['money'] < 0:
            raise serializers.ValidationError("Money cannot be negative.")
        if data.get('salary') and data['salary'] < 0:
            raise serializers.ValidationError("Salary cannot be negative.")
        return data


class CustomRegisterSerializer(RegisterSerializer):
    name = serializers.CharField(required=False)
    
    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['name'] = self.validated_data.get('name', '')
        return data

    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data.get('name', '')
        user.save()
        return user