from django.http import JsonResponse
import yfinance as yf

def get_indices_data(request):
    indices = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Dow Jones": "^DJI",
        "Kospi": "^KS11"
    }

    data = {}
    try:
        for name, ticker in indices.items():
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")  # 최근 5일 데이터 가져오기
            # 최근 유효 데이터 찾기
            if hist.empty:
                print(f"No data available for {name}")
                data[name] = {"current_price": "N/A", "percentage_change": 0.0}
                continue

            last_valid_row = hist.iloc[-1]  # 마지막 유효 데이터
            current_price = last_valid_row['Close']
            prev_close = hist['Close'].iloc[-2]
            change = current_price - prev_close
            percentage_change = (change / prev_close) * 100

            data[name] = {
                "current_price": round(current_price, 2),
                "percentage_change": round(percentage_change, 2)
            }
        print("Market Data fetched and saved successfully.")

    except Exception as e:
        print(f"Error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(data)
