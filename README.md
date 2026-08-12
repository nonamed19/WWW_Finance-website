# WWW - Wealth With You

> 예·적금 비교부터 맞춤 추천, 환율·증시·금융 뉴스, AI 상담까지 한 곳에서 제공하는 개인 금융 플랫폼

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1?logo=mysql&logoColor=white)
![License](https://img.shields.io/badge/license-[LICENSE_TYPE]-lightgrey)

## 프로젝트 소개

**WWW(Wealth With You)** 는 국내 공공/금융 오픈 API를 통합해 개인 사용자가 금융 상품을 쉽게 비교하고 자신의 성향에 맞는 상품을 추천받을 수 있도록 만든 웹 서비스입니다.

- **백엔드**: FastAPI 기반 REST API 서버 (MySQL 영속화)
- **프런트엔드**: React + Vite 단일 페이지 애플리케이션(SPA)

외부에서 수집한 데이터(예·적금, 환율, 증시, 뉴스)를 자체 DB에 적재(upsert)한 뒤 클라이언트에 제공하는 구조로, 조회 시점의 외부 API 장애가 서비스 전체로 전파되지 않도록 설계되어 있습니다.

## 주요 기능

| 기능 | 설명 | 데이터 출처 |
| --- | --- | --- |
| 예·적금 상품 | 상품 목록 조회, 최대 3개 상품 금리 비교 | 금융감독원 금융상품 통합비교공시(Finlife) |
| 맞춤 추천 | 금융 성향 설문 기반 예·적금 상위 5개 추천 | 자체 설문 + DB 집계 |
| 환율 | 통화별 매매기준율 조회 및 환산 계산기 | 한국수출입은행 환율 API |
| 증시 | 국내 지수 데이터 수집/조회 | 공공데이터포털(data.go.kr) |
| 세계 증시 | S&P 500 / Nasdaq / Dow Jones / Kospi 실시간 지수 | Yahoo Finance(yfinance) |
| 금융 뉴스 | 경제·주식 관련 뉴스 검색/조회 | 네이버 검색 API |
| 커뮤니티 | 상품 리뷰 작성, 좋아요, 댓글 | 자체 DB |
| 상품 구독 | 관심 상품 구독 토글 및 목록 관리 | 자체 DB |
| AI 상담 | 금융 상담 챗봇(대화 이력 저장) | OpenAI `gpt-4o-mini` |

### 왜 유용한가

- **통합 데이터 계층**: 서로 다른 5개 외부 API를 하나의 스키마와 REST 인터페이스로 표준화합니다.
- **회복 탄력성**: 외부 호출은 재시도(`urllib3.Retry`, 429/5xx 대상)와 커넥션 풀을 사용하며, 실패는 502로 변환됩니다. 증시 지수는 60초 캐시로 중복 호출을 방지합니다.
- **DB 비가용 시 부분 동작**: MySQL이 중단되어도 문서(`/docs`)와 DB 비의존 라우트는 계속 동작하고, DB 라우트는 500이 아닌 503을 반환하며 MySQL 복구 시 자동으로 회복됩니다.

## 아키텍처

```
[React SPA (Vite)]  --/api--> [FastAPI]  --SQLAlchemy--> [MySQL]
        |                        |
        |                        +--> Finlife (예·적금)
        |                        +--> 한국수출입은행 (환율)
        |                        +--> data.go.kr (증시)
        |                        +--> 네이버 검색 (뉴스)
        |                        +--> yfinance (세계 증시)
        +--> Axios (Token 인증)   +--> OpenAI (AI 상담)
```

## 디렉터리 구조

> 아래 구조는 import 경로(`from app import ...`)와 실행 진입점(`main:app`), `config.py`의 `BASE_DIR = ...parent.parent` 기준으로 **추론한 형태**이며, 실제 레포지토리 배치에 맞게 검증이 필요합니다.

```
[REPO_ROOT]/
├── backend/
│   ├── main.py               # FastAPI 앱 진입점, 라우터 등록, CORS, /health
│   ├── run.py                # 로컬 개발 실행 (127.0.0.1:8000, reload)
│   ├── requirements.txt
│   ├── .env                  # 환경 변수 (직접 생성)
│   └── app/
│       ├── __init__.py
│       ├── config.py         # 환경 변수 로딩, 경로/키/CORS 설정
│       ├── database.py       # SQLAlchemy 엔진/세션, get_db 의존성
│       ├── models.py         # ORM 모델 전체
│       ├── security.py       # 비밀번호 해시(PBKDF2), 토큰 인증
│       ├── common.py         # body / model_data / get_or_404 헬퍼
│       ├── external.py       # 재시도 지원 HTTP 클라이언트
│       ├── accounts.py       # 계정/프로필
│       ├── bankings.py       # 예·적금 상품 + 리뷰/댓글
│       ├── currencies.py     # 환율
│       ├── stocks.py         # 증시
│       ├── economics.py      # 뉴스
│       ├── markets.py        # 세계 증시 지수
│       ├── surveys.py        # 금융 성향 설문
│       ├── recommendations.py# 맞춤 추천
│       ├── subscriptions.py  # 상품 구독
│       └── chats.py          # AI 상담
└── frontend/
    ├── index.html
    ├── package.json
    ├── package-lock.json
    └── src/
        ├── main.jsx          # React 진입점, BrowserRouter
        ├── App.jsx           # 라우팅 및 화면 컴포넌트 전체
        ├── api.js            # Axios 인스턴스, 토큰 인터셉터
        ├── styles.css
        └── assets/
            └── mainlogo.png  # index.html / Header에서 참조
```

## 시작하기

### 요구 사항

- Python 3.10 이상
- Node.js 18 이상 (Vite 5 요구 사항)
- MySQL 8.x (스키마: `utf8mb4`)

### 1. 백엔드 설정

```bash
# backend 디렉터리에서 실행
cd backend

# 가상 환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

`.env` 파일을 `backend/` 경로에 생성합니다. 실제 값은 절대 커밋하지 마세요.

```dotenv
# 데이터베이스 (mysql+pymysql 스킴 필수)
DATABASE_URL=mysql+pymysql://[DB_USER]:[DB_PASSWORD]@127.0.0.1:3306/[DB_NAME]?charset=utf8mb4
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_CONNECT_TIMEOUT=3

# 외부 API 키
BANKINGS_KEY=[YOUR_KEY]          # 금융감독원 Finlife
CURRENCIES_KEY=[YOUR_KEY]        # 한국수출입은행
STOCKS_KEY=[YOUR_KEY]            # 공공데이터포털
NAVER_CLIENT_ID=[YOUR_KEY]       # 네이버 검색 API
NAVER_CLIENT_SECRET=[YOUR_KEY]
CHATS_KEY=[YOUR_KEY]             # OpenAI API 키
RESEND_API_KEY=[YOUR_KEY]        # (설정만 존재, 현재 코드에서 미사용)

# CORS 허용 오리진 (콤마 구분)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

서버 실행:

```bash
python run.py
# http://127.0.0.1:8000 에서 기동, /docs 로 리다이렉트
```

> `DATABASE_URL`이 비어 있거나 `mysql+pymysql://` 스킴이 아니면 기동 시 예외가 발생합니다. 스키마와 인덱스는 서버 기동 시점에 자동 생성됩니다(`initialize_database`).

### 2. 프런트엔드 설정

```bash
# frontend 디렉터리에서 실행
cd frontend
npm install
npm run dev        # 개발 서버 (기본 포트 5173)
```

프런트엔드는 API 기본 경로로 `/api`를 사용하며, 배포 시 `VITE_API_URL` 환경 변수로 재정의할 수 있습니다.

```dotenv
# frontend/.env (선택)
VITE_API_URL=http://127.0.0.1:8000
```

> **주의**: `api.js`는 `/api` 접두사를 Vite가 FastAPI로 프록시한다고 가정하지만, 저장소에 `vite.config.js`가 없습니다. 개발 환경에서는 프록시 설정을 담은 `vite.config.js`를 추가하거나, `VITE_API_URL`을 백엔드 주소로 직접 지정해야 정상 동작합니다. (아래 체크리스트 참고)

## 사용 예시

### 회원가입 후 토큰 발급

```bash
curl -X POST http://127.0.0.1:8000/accounts/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tester","password1":"pw1234","password2":"pw1234","email":"a@b.com"}'
# => {"key": "<64자리 토큰>"}
```

### 인증이 필요한 요청

모든 보호 라우트는 `Authorization: Token <key>` 헤더를 요구합니다.

```bash
curl http://127.0.0.1:8000/accounts/user_info/ \
  -H "Authorization: Token <발급받은_토큰>"
```

> 로그인/회원가입 시 사용자당 기존 토큰은 삭제되고 새 토큰이 발급됩니다(사용자당 1개 활성 토큰).

### 환율 환산

```bash
curl -X POST http://127.0.0.1:8000/currencies/exchange-calculate/ \
  -H "Content-Type: application/json" \
  -d '{"amount":100,"from_currency":"USD","to_currency":"KRW"}'
```

## 환경 변수 요약

| 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `DATABASE_URL` | (없음, 필수) | `mysql+pymysql://` 스킴만 허용 |
| `DB_POOL_SIZE` | `5` | 커넥션 풀 크기 |
| `DB_MAX_OVERFLOW` | `10` | 풀 초과 허용 커넥션 수 |
| `DB_CONNECT_TIMEOUT` | `3` | 연결 타임아웃(초) |
| `BANKINGS_KEY` | `""` | Finlife 인증키 |
| `CURRENCIES_KEY` | `""` | 한국수출입은행 인증키 |
| `STOCKS_KEY` | `""` | 공공데이터포털 서비스키 |
| `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` | `""` | 네이버 검색 API 자격증명 |
| `CHATS_KEY` | `""` | OpenAI API 키 |
| `RESEND_API_KEY` | `""` | 설정만 존재, 현재 미사용 |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | 허용 오리진(콤마 구분) |
| `VITE_API_URL` (프런트) | `/api` | API 베이스 URL |

## API 요약

대화형 문서는 서버 기동 후 `http://127.0.0.1:8000/docs`에서 확인할 수 있습니다. 아래는 주요 엔드포인트입니다(🔒 = 토큰 인증 필요).

### 계정 (`/accounts`)

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| POST | `/accounts/signup/` | 회원가입, 토큰 발급 |
| POST | `/accounts/login/` | 로그인, 토큰 발급 |
| POST 🔒 | `/accounts/logout/` | 토큰 폐기 |
| GET | `/accounts/user_all/` | 전체 사용자 조회 |
| GET 🔒 | `/accounts/user_info/` | 내 정보 조회 |
| PATCH 🔒 | `/accounts/user_update/` | 정보 수정(프로필 이미지 포함) |
| DELETE 🔒 | `/accounts/user_delete/` | 계정 삭제 |

### 예·적금 및 커뮤니티 (`/bankings`)

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | `/bankings/deposit-fetch-data/` | Finlife 예금 수집/적재 |
| GET | `/bankings/deposit-get-products/` | 예금 상품 조회 |
| GET | `/bankings/saving-fetch-data/` | Finlife 적금 수집/적재 |
| GET | `/bankings/saving-get-products/` | 적금 상품 조회 |
| GET | `/bankings/bank-products/{bank_name}/` | 은행별 상품 조회 |
| GET 🔒 | `/bankings/reviews/` | 리뷰 목록 |
| POST 🔒 | `/bankings/reviews/` | 리뷰 작성 |
| PUT 🔒 | `/bankings/reviews/{review_id}/` | 리뷰 수정 |
| DELETE 🔒 | `/bankings/reviews/{review_id}/` | 리뷰 삭제 |
| POST 🔒 | `/bankings/reviews/{review_id}/like/` | 좋아요 토글 |
| POST 🔒 | `/bankings/reviews/{review_id}/comments/` | 댓글 작성 |
| PUT 🔒 | `/bankings/reviews/{review_id}/comments/` | 댓글 수정 |
| DELETE 🔒 | `/bankings/reviews/{review_id}/comments/` | 댓글 삭제 |

### 그 외 도메인

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | `/currencies/exchange-fetch-data/` | 환율 수집/적재 |
| GET | `/currencies/exchange-get-data/` | 환율 조회(KRW 보정 포함) |
| POST | `/currencies/exchange-calculate/` | 환율 환산 |
| GET | `/stocks/stock-fetch-data/` | 증시 수집/적재 |
| GET | `/stocks/stock-get-data/` | 증시 조회 |
| GET | `/economics/news-fetch-data/` | 뉴스 수집/적재 |
| GET | `/economics/news-get-data/` | 뉴스 조회 |
| GET | `/markets/indices/` | 세계 증시 지수(60초 캐시) |
| POST 🔒 | `/surveys/submit-survey/` | 금융 성향 설문 제출 |
| GET 🔒 | `/recommendations/recommend/` | 맞춤 추천 |
| POST 🔒 | `/subscriptions/subscribe/` | 구독 토글 |
| GET 🔒 | `/subscriptions/my-subscriptions/` | 내 구독 목록 |
| POST 🔒 | `/chats/chat-message/` | AI 상담 메시지 |
| GET 🔒 | `/chats/chat-history/` | 상담 이력 조회 |
| GET | `/health/` | 헬스 체크(DB 상태 포함) |

## 기술 스택

**백엔드**: FastAPI 0.115, Uvicorn, SQLAlchemy 2.0, PyMySQL, python-dotenv, python-multipart, requests, xmltodict, yfinance, openai

**프런트엔드**: React 18.3, react-router-dom 6.28, Axios 1.7, Vite 5.4

## 도움말 및 문의

- 대화형 API 문서: 서버 기동 후 `/docs` (Swagger UI)
- 이슈 및 버그 제보: [REPO_URL]/issues
- 추가 문서: `docs/` (예정)

## 기여

기여를 환영합니다. 자세한 개발 규칙과 절차는 `CONTRIBUTING.md`를 참고해 주세요(현재 준비 중).

- 유지보수: [MAINTAINER_NAME] ([MAINTAINER_EMAIL])

## 라이선스

이 프로젝트는 [LICENSE_TYPE] 라이선스를 따릅니다. 전문은 `LICENSE` 파일을 참고하세요.

---

## 검증 체크리스트

문서 작성 과정에서 확인이 필요하거나 코드에서 채울 수 없었던 항목입니다.

**플레이스홀더 (코드만으로 결정 불가)**
- [ ] `[REPO_URL]` - 저장소 URL
- [ ] `[MAINTAINER_NAME]` / `[MAINTAINER_EMAIL]` - 유지보수 담당자
- [ ] `[LICENSE_TYPE]` - 라이선스 종류
- [ ] `[DB_USER]` / `[DB_PASSWORD]` / `[DB_NAME]` - MySQL 접속 정보
- [ ] `[REPO_ROOT]` - 실제 루트 디렉터리 명칭

**누락 파일**
- [ ] `LICENSE` - 라이선스 전문
- [ ] `CONTRIBUTING.md` - 기여 가이드
- [ ] `vite.config.js` - `/api` 프록시 설정이 없어 개발 환경에서 API 호출이 실패할 수 있음
- [ ] `.env.example` - `config.py` 주석은 `.env.example` 복사를 안내하지만 파일이 확인되지 않음

**코드-문서 확인 필요 사항**
- [ ] **디렉터리 구조는 추론값**입니다. `main.py`는 `from app import ...`로 import하고 `run.py`는 `main:app`을 실행하므로, `main.py`가 `app/` 패키지의 상위(=`backend/`)에 위치한다고 가정했습니다. 실제 배치를 확인해 주세요.
- [ ] **프런트엔드 프록시**: `api.js`의 기본 baseURL `/api`는 Vite 프록시를 전제로 하지만 `vite.config.js`가 없습니다. 프록시를 추가하거나 `VITE_API_URL`을 명시해야 합니다.
- [ ] **`RESEND_API_KEY`**: `config.py`에 정의되어 있으나 제공된 코드에서 사용처가 없습니다. 이메일 발송 기능이 별도 모듈에 있는지 확인 필요.
- [ ] **AI 상담 외부 의존성**: `chats.py`는 OpenAI `gpt-4o-mini`를 호출합니다. 폐쇄망/온프레미스 요건이 있는 경우 이 부분이 제약이 될 수 있습니다.
- [ ] **프런트엔드 소스 레이아웃**: `index.html`이 `./src/main.jsx`를, `App.jsx`가 `/src/assets/mainlogo.png`를 참조하므로 `src/` 및 `src/assets/` 존재를 가정했습니다.