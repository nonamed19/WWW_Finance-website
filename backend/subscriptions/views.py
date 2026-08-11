from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_405_METHOD_NOT_ALLOWED
from finance_recommendation.settings import RESEND_API_KEY
from .models import SubscribedProduct
from .serializers import SubscribedProductSerializer
import resend


@api_view(['POST'])
def toggle_subscribed_product(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            product_id = data.get('product_id')
            product_name = data.get('product_name')

            if not product_id or not product_name:
                return Response({"error": "Product ID and name are required."}, status=HTTP_400_BAD_REQUEST)

            # 이미 구독된 상품인지 확인
            existing_subscription = SubscribedProduct.objects.filter(
                user=request.user,
                product_id=product_id
            ).first()

            if existing_subscription:
                # 이미 구독된 경우 -> DB에서 삭제
                existing_subscription.delete()
                return Response({"message": f"'{product_name}' 구독이 취소되었습니다."}, status=HTTP_200_OK)
            else:
                # 구독되지 않은 경우 -> DB에 추가
                subscribed_product = SubscribedProduct.objects.create(
                    user=request.user,
                    product_id=product_id,
                    product_name=product_name
                )

                serializer = SubscribedProductSerializer(subscribed_product)

                # 이메일 내용
                subject = "구독 완료 알림"
                html_content = (
                    f"<h1>안녕하세요, {request.user.name or request.user.username}님.</h1>"
                    f"<p>'{product_name}' 금융 상품을 성공적으로 구독하셨습니다.</p>"
                    f"<p>자세한 내용은 프로필 페이지에서 확인하실 수 있습니다.</p>"
                    f"<p>감사합니다.</p>"
                )
                from_email = "onboarding@resend.dev"  # 발신 이메일 주소
                to_email = request.user.email  # 수신 이메일 주소

                # Resend 이메일 전송
                try:
                    resend.api_key = RESEND_API_KEY  # Resend API 키
                    r = resend.Emails.send(
                        {
                            "from": from_email,
                            "to": to_email,
                            "subject": subject,
                            "html": html_content,
                        }
                    )
                except Exception as e:
                    print(f"Resend Email Error: {e}")
                    return Response(
                        {"error": "구독은 완료되었지만 이메일 전송에 실패했습니다."},
                        status=HTTP_201_CREATED,
                    )

                return Response(serializer.data, status=HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)

    return Response({"error": "Invalid request method."}, status=HTTP_405_METHOD_NOT_ALLOWED)


## 사용자 구독 목록 조회 API
@api_view(['GET'])
def my_subscribed_products(request):
    if request.method == 'GET':
        subscribed_products = SubscribedProduct.objects.filter(user=request.user)
        serializer = SubscribedProductSerializer(subscribed_products, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    return Response({"error": "Invalid request method."}, status=HTTP_405_METHOD_NOT_ALLOWED)
