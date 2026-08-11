from rest_framework.decorators import api_view
from rest_framework.response import Response
from finance_recommendation.settings import STOCKS_KEY
from .models import StockList
from .serializers import StockListSerializer
import requests
import xmltodict


API_URL = f'http://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getStockMarketIndex?serviceKey={STOCKS_KEY}'

@api_view(['GET'])
def stock_fetch_data(request):
    # verify=False 옵션 추가
    response = requests.get(API_URL, verify=False)
    
    xml_data = response.content
    data_dict = xmltodict.parse(xml_data)
    items = data_dict.get("response", {}).get("body", {}).get("items", {}).get("item", [])
    
    for item in items:
        defaults = {
            "idx_csf": item.get("idxCsf"),
            "epy_itms_cnt": int(item.get("epyItmsCnt", 0)),
            "clpr": float(item.get("clpr", 0.0)),
            "vs": float(item.get("vs", 0.0)),
            "flt_rt": float(item.get("fltRt", 0.0)),
            "mkp": float(item.get("mkp", 0.0)),
            "hipr": float(item.get("hipr", 0.0)),
            "lopr": float(item.get("lopr", 0.0)),
            "trqu": int(item.get("trqu", 0)),
            "tr_prc": int(item.get("trPrc", 0)),
            "lstg_mrkt_tot_amt": int(item.get("lstgMrktTotAmt", 0)),
        }

        StockList.objects.update_or_create(
            bas_dt=item.get("basDt"),
            idx_nm=item.get("idxNm"),
            defaults=defaults
        )

    return Response({"message": "Data fetched and saved successfully."})


@api_view(['GET'])
def stock_get_data(request):
    stocks = StockList.objects.all()
    serializer = StockListSerializer(stocks, many=True)
    return Response(serializer.data)
