import axios from "axios";

const API_URL = "http://127.0.0.1:8000"; // Django API URL

// 환율 데이터 가져오기
export const getExchangeData = function () {
  return axios({
    method: "get",
    url: `${API_URL}/currencies/exchange-get-data/`,
  })
    .then((response) => {
      console.log("환율 데이터 가져오기 성공:", response.data);
      return response.data;
    })
    .catch((err) => {
      console.error("환율 데이터 가져오기 실패:", err);
      throw err;
    });
};

// 환율 데이터 갱신
export const fetchExchangeData = function () {
  return axios({
    method: "get",
    url: `${API_URL}/currencies/exchange-fetch-data/`,
  })
    .then((response) => {
      console.log("환율 데이터 갱신 성공:", response.data);
      return response.data;
    })
    .catch((err) => {
      console.error("환율 데이터 갱신 실패:", err);
      throw err;
    });
};

export const calculateExchange = function (amount, fromCurrency, toCurrency) {
  return axios({
    method: "post",
    url: `${API_URL}/currencies/exchange-calculate/`,
    data: {
      amount,
      from_currency: fromCurrency,
      to_currency: toCurrency
    }
  })
    .then((response) => {
      console.log("환율 계산 성공:", response.data);
      return response.data;
    })
    .catch((err) => {
      console.error("환율 계산 실패:", err);
      throw err;
    });
};