from rest_framework import serializers
from .models import DepositBaseList, DepositOptionList, SavingBaseList, SavingOptionList, ReviewComment, ProductReview


class DepositBaseListSerializer(serializers.ModelSerializer):
    class OptionForProductSerializer(serializers.ModelSerializer):
        class Meta:
            model = DepositOptionList
            fields = '__all__'
            
    deposit_options = OptionForProductSerializer(many=True, read_only=True)

    class Meta:
        model = DepositBaseList
        fields = '__all__'


class DepositOptionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOptionList
        fields = '__all__'


class SavingBaseListSerializer(serializers.ModelSerializer):
    class OptionForProductSerializer(serializers.ModelSerializer):
        class Meta:
            model = SavingOptionList
            fields = '__all__'
    
    saving_options = OptionForProductSerializer(many=True, read_only=True)

    class Meta:
        model = SavingBaseList
        fields = '__all__'


class SavingOptionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingOptionList
        fields = '__all__'


class ReviewCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = ReviewComment
        fields = ('id', 'content', 'username', 'created_at', 'updated_at', 'is_owner')
        read_only_fields = ('user', 'review')

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.user


class ProductReviewSerializer(serializers.ModelSerializer):
    comments = ReviewCommentSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = ('id', 'product_type', 'product_name', 'title', 'content', 
                    'rating', 'created_at', 'updated_at', 'username', 'comments',
                    'like_count', 'is_liked', 'is_owner')
        read_only_fields = ('user',)

    def get_is_liked(self, obj):
        request = self.context.get('request')
        return request and request.user in obj.likes.all()

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.user

