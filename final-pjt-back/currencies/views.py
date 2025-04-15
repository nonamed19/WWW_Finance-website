from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from finance_recommendation.settings import CURRENCIES_KEY
from .models import ExchangeList
from .serializers import ExchangeListSerializer
import requests

# API_URL = f'http://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={CURRENCIES_KEY}&data=AP01'
API_URL = f'http://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={CURRENCIES_KEY}&searchdate=20241126&data=AP01'


@api_view(['GET'])
def exchange_fetch_data(request):
    response = requests.get(API_URL)

    data = response.json()

    for item in data:
        defaults = {
            'ttb': item.get('ttb', ''),  # 전신환(송금) 받으실 때
            'tts': item.get('tts', ''),  # 전신환(송금) 보내실 때
            'deal_bas_r': item.get('deal_bas_r', ''),  # 매매기준율
            'bkpr': item.get('bkpr', ''),  # 장부가격
            'yy_efee_r': item.get('yy_efee_r', ''),  # 연이율 수수료율
            'ten_dd_efee_r': item.get('ten_dd_efee_r', ''),  # 10일 수수료율
            'kftc_bkpr': item.get('kftc_bkpr', ''),  # KFTC 장부가격
            'kftc_deal_bas_r': item.get('kftc_deal_bas_r', ''),  # KFTC 매매기준율
            'cur_nm': item.get('cur_nm', ''),  # 통화명
        }

        ExchangeList.objects.update_or_create(
            cur_unit=item.get('cur_unit', ''),  # 통화 단위로 고유값 결정
            defaults=defaults
        )

    return Response({"message": "Exchange rates fetched and stored successfully."})


@api_view(['GET'])
def exchange_get_data(request):
    exchanges = ExchangeList.objects.all()
    serializer = ExchangeListSerializer(exchanges, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def exchange_calculate(request):
    try:
        amount = float(request.data.get('amount', 0))
        from_currency = request.data.get('from_currency')
        to_currency = request.data.get('to_currency')

        if not all([amount, from_currency, to_currency]):
            return Response({'error': 'Required parameters missing'}, 
                        status=status.HTTP_400_BAD_REQUEST)

        # 통화 정보 조회
        from_currency_obj = ExchangeList.objects.filter(cur_unit=from_currency).first()
        to_currency_obj = ExchangeList.objects.filter(cur_unit=to_currency).first()

        if not from_currency_obj or not to_currency_obj:
            return Response({'error': 'Invalid currency'}, 
                        status=status.HTTP_400_BAD_REQUEST)

        # 환율 계산
        from_rate = float(from_currency_obj.deal_bas_r.replace(',', ''))
        to_rate = float(to_currency_obj.deal_bas_r.replace(',', ''))
        
        # KRW로 변환 후 목표 통화로 변환
        converted_amount = (amount * from_rate) / to_rate

        return Response({
            'from_amount': amount,
            'from_currency': from_currency,
            'to_currency': to_currency,
            'converted_amount': round(converted_amount, 2)
        })

    except ValueError:
        return Response({'error': 'Invalid amount'}, 
                    status=status.HTTP_400_BAD_REQUEST)

