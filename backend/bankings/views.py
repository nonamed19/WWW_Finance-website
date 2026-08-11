from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from finance_recommendation.settings import BANKINGS_KEY
from .models import DepositBaseList, DepositOptionList, SavingBaseList, SavingOptionList, ProductReview, ReviewComment
from .serializers import DepositBaseListSerializer, SavingBaseListSerializer, ProductReviewSerializer, ReviewCommentSerializer
import requests


API_URL_deposit = f"https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={BANKINGS_KEY}&topFinGrpNo=020000&pageNo=1"
API_URL_saving = f"https://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json?auth={BANKINGS_KEY}&topFinGrpNo=020000&pageNo=1"

## 예금
@api_view(['GET'])
def deposit_fetch_data(request):
    # Fetch data from the API
    response = requests.get(API_URL_deposit)
    
    data = response.json().get('result', {})
    base_list = data.get('baseList', [])
    option_list = data.get('optionList', [])
    
    # Store baseList data in the database
    for base in base_list:
        base_defaults = {
            "dcls_month": base.get("dcls_month"),
            "kor_co_nm": base.get("kor_co_nm"),
            "fin_prdt_nm": base.get("fin_prdt_nm"),
            "join_way": base.get("join_way"),
            "mtrt_int": base.get("mtrt_int"),
            "spcl_cnd": base.get("spcl_cnd"),
            "join_deny": base.get("join_deny"),
            "join_member": base.get("join_member"),
            "etc_note": base.get("etc_note"),
            "max_limit": base.get("max_limit"),
            "dcls_strt_day": base.get("dcls_strt_day"),
            "dcls_end_day": base.get("dcls_end_day"),
            "fin_co_subm_day": base.get("fin_co_subm_day"),
        }
        base_obj, _ = DepositBaseList.objects.update_or_create(
            fin_co_no=base['fin_co_no'], fin_prdt_cd=base['fin_prdt_cd'],
            defaults=base_defaults
        )
    
    # Store optionList data in the database
    for option in option_list:
        option_defaults = {
            "dcls_month": option.get("dcls_month"),
            "intr_rate_type": option.get("intr_rate_type"),
            "intr_rate_type_nm": option.get("intr_rate_type_nm"),
            "save_trm": option.get("save_trm"),
            "intr_rate": option.get("intr_rate", 0.0),  # 기본값 0.0
            "intr_rate2": option.get("intr_rate2", 0.0),  # 기본값 0.0
        }
        base_obj = DepositBaseList.objects.filter(fin_co_no=option['fin_co_no'], fin_prdt_cd=option['fin_prdt_cd']).first()
        if base_obj:
            DepositOptionList.objects.update_or_create(
                product=base_obj,
                save_trm=option['save_trm'],
                defaults=option_defaults
            )

    return Response({"message": "Data fetched and stored successfully."})


@api_view(['GET'])
def deposit_get_products(request):
    products = DepositBaseList.objects.all()
    serializer = DepositBaseListSerializer(products, many=True)
    return Response(serializer.data)


## 적금
@api_view(['GET'])
def saving_fetch_data(request):
    # Fetch data from the API
    response = requests.get(API_URL_saving)
    
    data = response.json().get('result', {})
    base_list = data.get('baseList', [])
    option_list = data.get('optionList', [])
    
    # Store baseList data in the database
    for base in base_list:
        base_defaults = {
            "dcls_month": base.get("dcls_month"),
            "kor_co_nm": base.get("kor_co_nm"),
            "fin_prdt_nm": base.get("fin_prdt_nm"),
            "join_way": base.get("join_way"),
            "mtrt_int": base.get("mtrt_int"),
            "spcl_cnd": base.get("spcl_cnd"),
            "join_deny": base.get("join_deny"),
            "join_member": base.get("join_member"),
            "etc_note": base.get("etc_note"),
            "max_limit": base.get("max_limit"),
            "dcls_strt_day": base.get("dcls_strt_day"),
            "dcls_end_day": base.get("dcls_end_day"),
            "fin_co_subm_day": base.get("fin_co_subm_day"),
        }
        base_obj, _ = SavingBaseList.objects.update_or_create(
            fin_co_no=base['fin_co_no'], fin_prdt_cd=base['fin_prdt_cd'],
            defaults=base_defaults
        )
    
    # Store optionList data in the database
    for option in option_list:
        option_defaults = {
            "dcls_month": option.get("dcls_month"),
            "intr_rate_type": option.get("intr_rate_type"),
            "intr_rate_type_nm": option.get("intr_rate_type_nm"),
            "save_trm": option.get("save_trm"),
            "intr_rate": option.get("intr_rate", 0.0),  # 기본값 0.0
            "intr_rate2": option.get("intr_rate2", 0.0),  # 기본값 0.0
        }
        base_obj = SavingBaseList.objects.filter(fin_co_no=option['fin_co_no'], fin_prdt_cd=option['fin_prdt_cd']).first()
        if base_obj:
            SavingOptionList.objects.update_or_create(
                product=base_obj,
                save_trm=option['save_trm'],
                defaults=option_defaults
            )

    return Response({"message": "Data fetched and stored successfully."})


@api_view(['GET'])
def saving_get_products(request):
    products = SavingBaseList.objects.all()
    serializer = SavingBaseListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def product_reviews(request):
    if request.method == 'GET':
        reviews = ProductReview.objects.all().order_by('-created_at')
        serializer = ProductReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ProductReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'DELETE'])
def review_detail(request, review_id):
    review = get_object_or_404(ProductReview, pk=review_id)
    
    if request.user != review.user:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'PUT':
        serializer = ProductReviewSerializer(review, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    elif request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def review_like(request, review_id):
    review = get_object_or_404(ProductReview, pk=review_id)
    if request.user in review.likes.all():
        review.likes.remove(request.user)
    else:
        review.likes.add(request.user)
    return Response({'likes_count': review.like_count()})


@api_view(['POST', 'PUT', 'DELETE'])
def review_comments(request, review_id):
    review = get_object_or_404(ProductReview, pk=review_id)
    
    if request.method == 'POST':
        serializer = ReviewCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user, review=review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    elif request.method in ['PUT', 'DELETE']:
        comment = get_object_or_404(ReviewComment, pk=request.data.get('comment_id'))
        if request.user != comment.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            serializer = ReviewCommentSerializer(comment, data=request.data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        
        else:  # DELETE
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def bank_products(request, bank_name):
    # 해당 은행의 예금 상품 조회
    deposit_products = DepositBaseList.objects.filter(kor_co_nm=bank_name)
    deposit_serializer = DepositBaseListSerializer(deposit_products, many=True)
    
    # 해당 은행의 적금 상품 조회  
    saving_products = SavingBaseList.objects.filter(kor_co_nm=bank_name)
    saving_serializer = SavingBaseListSerializer(saving_products, many=True)
    
    return Response({
        'deposit_products': deposit_serializer.data,
        'saving_products': saving_serializer.data
    })
