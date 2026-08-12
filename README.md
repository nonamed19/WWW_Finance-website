# WWW - Wealth With You

> 나를 위한 똑똑한 금융, 예·적금 비교부터 맞춤 추천, 환율, 증시, AI 상담까지 한 곳에서

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)
![API Version](https://img.shields.io/badge/API-v1.0.0-informational)
![License](https://img.shields.io/badge/License-[LICENSE_TYPE]-lightgrey)

WWW는 한국의 실제 금융 공공 데이터를 모아 사용자가 예금·적금 상품을 비교하고, 금융 성향 설문을 바탕으로 맞춤 상품을 추천받으며, 환율과 국내외 증시를 확인하고, 리뷰 커뮤니티와 AI 금융 상담까지 이용할 수 있는 풀스택 금융 정보 플랫폼입니다. FastAPI 백엔드 API와 React (Vite) 단일 페이지 애플리케이션으로 구성됩니다.

## 목차

- [WWW - Wealth With You](#www---wealth-with-you)
  - [목차](#목차)
  - [주요 기능](#주요-기능)
  - [기술 스택](#기술-스택)
  - [아키텍처](#아키텍처)
  - [디렉터리 구조](#디렉터리-구조)
  - [시작하기](#시작하기)
    - [사전 요구 사항](#사전-요구-사항)
    - [백엔드 설정](#백엔드-설정)
    - [프론트엔드 설정](#프론트엔드-설정)
  - [환경 변수](#환경-변수)
  - [사용 예시](#사용-예시)
  - [API 요약](#api-요약)
  - [외부 데이터 제공자](#외부-데이터-제공자)
  - [도움 받기](#도움-받기)
  - [기여하기](#기여하기)
  - [유지 관리자](#유지-관리자)
  - [라이선스](#라이선스)
  - [설정 확인 체크리스트](#설정-확인-체크리스트)

## 주요 기능

- **예·적금 상품 비교**: 금융감독원 금융상품통합비교공시 데이터를 가져와 은행별 상품과 기간별 최고 금리를 한눈에 비교하고, 최대 3개 상품을 선택해 금리 차트로 비교합니다.
- **맞춤 상품 추천**: 16개 문항의 금융 성향 설문을 저장하고, 예금·적금 각각 최고 금리 기준 상위 5개 상품을 추천합니다. 순위 계산과 상위 5개 제한을 DB 쿼리 수준에서 처리해 불필요한 로딩을 줄입니다.
- **환율 정보 및 계산기**: 한국수출입은행 환율을 조회하고, 매매기준율(`deal_bas_r`) 기반으로 통화 간 금액을 변환합니다. 원본 API가 생략하는 KRW를 기본 통화로 자동 보정합니다.
- **국내외 증시**: `yfinance`로 글로벌 지수(S&P 500, Nasdaq, Dow Jones, Kospi)를 60초 캐시와 함께 제공하고, 공공데이터포털 API로 국내 주가지수를 저장·조회합니다.
- **금융 뉴스**: 네이버 뉴스 검색 API로 경제·금융 뉴스를 수집하며, HTML 태그를 정리해 저장합니다.
- **리뷰 커뮤니티**: 상품 리뷰 작성·수정·삭제, 좋아요, 댓글 기능을 제공합니다.
- **관심 상품 구독**: 예·적금 상품을 토글 방식으로 구독하고 마이페이지에서 관리합니다.
- **AI 금융 상담**: OpenAI `gpt-4o-mini` 기반 챗봇으로, 대화 기록을 저장하고 불러올 수 있습니다.
- **회원 및 프로필 관리**: 토큰 기반 인증(PBKDF2-SHA256), 프로필 이미지 업로드, 금융 정보 관리, 회원 탈퇴를 지원합니다.
- **장애 격리 설계**: MySQL이 중단되어도 API 서버는 기동되며, DB 의존 라우트만 503을 반환합니다. 외부 데이터 제공자 장애는 재시도 후 502로 변환됩니다.

## 기술 스택

**백엔드**
- Python 3.10+, FastAPI 0.115.6, Uvicorn 0.34.0 (standard)
- SQLAlchemy 2.0.51 (ORM), PyMySQL 1.1.1 (MySQL 드라이버)
- python-dotenv, python-multipart, requests, xmltodict, yfinance 0.2.50, openai 1.55.0

**프론트엔드**
- React 18.3.1, react-router-dom 6.28.0, axios 1.7.7
- Vite 5.4.11 (개발 서버 및 번들러, 자동 JSX 런타임)

**데이터베이스**
- MySQL (`utf8mb4`), 커넥션 풀 및 `pool_pre_ping` 사용

## 아키텍처

```
[ React SPA (Vite :5173) ]
        │  axios, /api 프리픽스 → Vite 프록시가 :8000 으로 전달
        ▼
[ FastAPI 애플리케이션 (:8000) ]
   ├─ accounts / surveys / recommendations / subscriptions / chats  → 인증(토큰) 필요
   ├─ bankings / currencies / stocks / economics / markets           → 데이터 조회 및 수집
   ├─ SQLAlchemy ORM  ──────────────► [ MySQL ]
   └─ external.py (재시도 세션) ────► [ 외부 공공/상용 API ]
```

프론트엔드는 개발 시 `/api` 프리픽스로 요청하고, Vite 프록시가 이를 `http://127.0.0.1:8000`으로 전달하며 프리픽스를 제거합니다. 배포 환경에서는 `VITE_API_URL` 환경 변수로 백엔드 주소를 지정할 수 있습니다.

## 디렉터리 구조

> 아래 구조는 코드의 import 경로와 파일 참조를 기반으로 **추론한 것**이며, 실제 저장소 배치와 다를 수 있으니 확인이 필요합니다. 제공된 파일은 단일 폴더에 모여 있지만, `main.py`의 `from app import ...`와 각 라우터의 상대 import(`from . import ...`)로 미루어 다음과 같이 두 패키지로 분리되어야 동작합니다.

```
.
├── backend/
│   ├── main.py               # FastAPI 진입점, 라우터 등록, CORS, /media 정적 마운트
│   ├── run.py                # 로컬 개발 실행기 (uvicorn main:app, 127.0.0.1:8000)
│   ├── requirements.txt
│   ├── .env                  # 직접 생성 (환경 변수 참고)
│   └── app/
│       ├── __init__.py
│       ├── config.py         # 환경 변수 로딩, 경로/키 설정
│       ├── database.py       # 엔진, 세션, get_db 의존성, 스키마 초기화
│       ├── models.py         # SQLAlchemy 모델 (User, 예·적금, 리뷰, 환율, 주식, 뉴스 등)
│       ├── security.py       # 비밀번호 해싱, 토큰 발급, current_user 의존성
│       ├── common.py         # body 파서, model_data 직렬화, get_or_404
│       ├── external.py       # 재시도 세션 기반 HTTP 클라이언트 (get_json/get_content)
│       ├── accounts.py       # 회원가입/로그인/프로필
│       ├── bankings.py       # 예·적금 상품, 리뷰, 댓글
│       ├── currencies.py     # 환율 조회 및 계산
│       ├── stocks.py         # 국내 주가지수
│       ├── economics.py      # 금융 뉴스
│       ├── markets.py        # 글로벌 지수 (yfinance)
│       ├── surveys.py        # 금융 성향 설문
│       ├── recommendations.py# 맞춤 상품 추천
│       ├── subscriptions.py  # 관심 상품 구독
│       └── chats.py          # AI 금융 상담
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js        # 제공된 파일명은 vite_config.js 이며 실제로는 vite.config.js 여야 함
    └── src/
        ├── main.jsx          # React 진입점 (BrowserRouter)
        ├── App.jsx           # 라우팅 및 전체 화면 컴포넌트
        ├── api.js            # axios 인스턴스, 인증 헤더, 세션 정리
        ├── styles.css
        └── assets/
            └── mainlogo.png  # index.html 및 Header가 참조 (저장소에 포함 필요)
```

## 시작하기

### 사전 요구 사항

- Python 3.10 이상
- Node.js 18 이상 및 npm
- 실행 중인 MySQL 인스턴스 (`utf8mb4` 권장)
- 각 외부 API 키 (아래 [환경 변수](#환경-변수) 참고). 키가 없어도 서버는 기동되며, 해당 기능만 503을 반환합니다.

### 백엔드 설정

```bash
# 1. backend 디렉터리로 이동
cd backend

# 2. 가상 환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. .env 파일 작성 (아래 환경 변수 표 참고)
#    최소한 DATABASE_URL 을 설정해야 DB 기능이 활성화됩니다.

# 5. 개발 서버 실행 (127.0.0.1:8000, 자동 리로드)
python run.py
```

기동 후:
- 대화형 API 문서: `http://127.0.0.1:8000/docs`
- 헬스 체크: `http://127.0.0.1:8000/health/`

> 스키마는 애플리케이션 기동 시 `Base.metadata.create_all`로 생성되며, 선언된 인덱스도 idempotent하게 추가됩니다. 별도의 마이그레이션 도구는 사용하지 않습니다.

### 프론트엔드 설정

```bash
# 1. frontend 디렉터리로 이동
cd frontend

# 2. 의존성 설치
npm install

# 3. 개발 서버 실행 (기본 5173 포트)
npm run dev

# 프로덕션 빌드 / 미리보기
npm run build
npm run preview
```

개발 서버는 `/api` 요청을 `http://127.0.0.1:8000`으로 프록시합니다. 백엔드를 먼저 실행해 두세요.

## 환경 변수

백엔드 `.env` 파일(`backend/.env`)에 다음 값을 설정합니다. 보안에 민감한 값은 절대 저장소에 커밋하지 마세요.

| 변수 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `DATABASE_URL` | 권장 | (없음) | `mysql+pymysql://user:[YOUR_PASSWORD]@127.0.0.1:3306/db?charset=utf8mb4` 형식. 미설정 시 DB 기능 비활성화 |
| `DB_POOL_SIZE` | 아니오 | `5` | 커넥션 풀 크기 |
| `DB_MAX_OVERFLOW` | 아니오 | `10` | 풀 초과 허용 커넥션 수 |
| `DB_CONNECT_TIMEOUT` | 아니오 | `3` | DB 연결 타임아웃(초) |
| `BANKINGS_KEY` | 기능별 | (없음) | 금융감독원 금융상품통합비교공시 API 키 |
| `CURRENCIES_KEY` | 기능별 | (없음) | 한국수출입은행 환율 API 키 |
| `STOCKS_KEY` | 기능별 | (없음) | 공공데이터포털 주가지수 API 키 |
| `NAVER_CLIENT_ID` | 기능별 | (없음) | 네이버 검색 API 클라이언트 ID |
| `NAVER_CLIENT_SECRET` | 기능별 | (없음) | 네이버 검색 API 클라이언트 시크릿 |
| `CHATS_KEY` | 기능별 | (없음) | OpenAI API 키 (`gpt-4o-mini` 상담) |
| `RESEND_API_KEY` | 아니오 | (없음) | `config.py`에 로딩되나 현재 코드에서 사용되지 않음 (아래 체크리스트 참고) |
| `CORS_ORIGINS` | 아니오 | `http://localhost:5173,http://127.0.0.1:5173` | 쉼표로 구분된 허용 오리진 |

프론트엔드 환경 변수:

| 변수 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `VITE_API_URL` | 아니오 | `/api` | 배포 시 백엔드 베이스 URL (예: `https://api.example.com`) |

`.env` 예시:

```dotenv
DATABASE_URL=mysql+pymysql://www_user:[YOUR_PASSWORD]@127.0.0.1:3306/www_financial?charset=utf8mb4
BANKINGS_KEY=[YOUR_KEY]
CURRENCIES_KEY=[YOUR_KEY]
STOCKS_KEY=[YOUR_KEY]
NAVER_CLIENT_ID=[YOUR_CLIENT_ID]
NAVER_CLIENT_SECRET=[YOUR_CLIENT_SECRET]
CHATS_KEY=[YOUR_OPENAI_KEY]
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## 사용 예시

인증이 필요한 엔드포인트는 `Authorization: Token <key>` 헤더를 사용합니다. 토큰은 회원가입 또는 로그인 응답의 `key` 값입니다.

**회원가입**

```bash
curl -X POST http://127.0.0.1:8000/accounts/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tester","password1":"[YOUR_PASSWORD]","password2":"[YOUR_PASSWORD]","email":"tester@example.com","name":"홍길동"}'
# → {"key": "..."}
```

**로그인 후 내 정보 조회**

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tester","password":"[YOUR_PASSWORD]"}' | python -c "import sys,json;print(json.load(sys.stdin)['key'])")

curl http://127.0.0.1:8000/accounts/user_info/ \
  -H "Authorization: Token $TOKEN"
```

**예금 상품 수집 후 조회**

```bash
curl http://127.0.0.1:8000/bankings/deposit-fetch-data/   # 외부 API에서 수집·저장
curl http://127.0.0.1:8000/bankings/deposit-get-products/ # 저장된 상품 조회
```

**환율 계산**

```bash
curl -X POST http://127.0.0.1:8000/currencies/exchange-calculate/ \
  -H "Content-Type: application/json" \
  -d '{"amount":100,"from_currency":"USD","to_currency":"KRW"}'
```

## API 요약

전체 요청·응답 스키마는 서버 실행 후 `/docs`(Swagger UI)에서 확인할 수 있습니다. 아래는 라우터별 개요입니다. 🔒 표시는 인증이 필요합니다.

| 그룹 (prefix) | 주요 엔드포인트 | 설명 |
| --- | --- | --- |
| `accounts` | `POST /signup/`, `POST /login/`, `POST /logout/` 🔒, `GET /user_info/` 🔒, `PATCH /user_update/` 🔒, `DELETE /user_delete/` 🔒, `GET /user_all/` | 회원 및 프로필 관리 |
| `bankings` | `GET /deposit-fetch-data/`, `GET /deposit-get-products/`, `GET /saving-fetch-data/`, `GET /saving-get-products/`, `GET /bank-products/{bank_name}/`, `GET|POST /reviews/` 🔒, `PUT|DELETE /reviews/{id}/` 🔒, `POST /reviews/{id}/like/` 🔒, 리뷰 댓글 CRUD 🔒 | 예·적금 상품, 리뷰, 댓글 |
| `currencies` | `GET /exchange-fetch-data/`, `GET /exchange-get-data/`, `POST /exchange-calculate/` | 환율 조회 및 계산 |
| `stocks` | `GET /stock-fetch-data/`, `GET /stock-get-data/` | 국내 주가지수 |
| `economics` | `GET /news-fetch-data/`, `GET /news-get-data/` | 금융 뉴스 |
| `markets` | `GET /indices/` | 글로벌 지수 (60초 캐시) |
| `surveys` | `POST /submit-survey/` 🔒 | 금융 성향 설문 저장 |
| `recommendations` | `GET /recommend/` 🔒 | 설문 기반 상위 5개 예·적금 추천 |
| `subscriptions` | `POST /subscribe/` 🔒, `GET /my-subscriptions/` 🔒 | 관심 상품 구독(토글) |
| `chats` | `POST /chat-message/` 🔒, `GET /chat-history/` 🔒 | AI 금융 상담 |
| `health` | `GET /health/`, `GET /` | 상태 확인, `/`는 `/docs`로 리다이렉트 |

## 외부 데이터 제공자

| 기능 | 제공자 | 엔드포인트 |
| --- | --- | --- |
| 예·적금 상품 | 금융감독원 금융상품통합비교공시 | `finlife.fss.or.kr` (`topFinGrpNo=020000`, 은행) |
| 환율 | 한국수출입은행 | `koreaexim.go.kr` (`data=AP01`) |
| 국내 주가지수 | 공공데이터포털 | `apis.data.go.kr` (`getStockMarketIndex`) |
| 금융 뉴스 | 네이버 검색 API | `openapi.naver.com/v1/search/news.json` |
| 글로벌 지수 | Yahoo Finance | `yfinance` (S&P 500, Nasdaq, Dow Jones, Kospi) |
| AI 상담 | OpenAI | `gpt-4o-mini` |

## 도움 받기

- **API 레퍼런스**: 서버 실행 후 `/docs`(Swagger UI) 또는 `/redoc`
- **이슈 및 버그 리포트**: [`[REPO_URL]`](/)의 Issues 탭
- **기여 가이드**: [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)

## 기여하기

기여를 환영합니다. 브랜치 전략, 코드 스타일, PR 절차 등 자세한 내용은 [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)를 참고하세요. (해당 파일은 아직 준비되지 않았습니다. 체크리스트 참고)

## 유지 관리자

- **[MAINTAINER_NAME]** - [MAINTAINER_EMAIL]

## 라이선스

이 프로젝트는 `[LICENSE_TYPE]` 라이선스로 배포됩니다. 자세한 내용은 [`LICENSE`](LICENSE) 파일을 참고하세요. (해당 파일은 아직 준비되지 않았습니다.)

## 설정 확인 체크리스트

문서 작성 중 코드만으로 확정할 수 없었던 항목과 확인이 필요한 불일치 사항입니다.

- [ ] `[REPO_URL]` - 저장소 URL 입력
- [ ] `[MAINTAINER_NAME]`, `[MAINTAINER_EMAIL]` - 유지 관리자 정보 입력
- [ ] `[LICENSE_TYPE]` - 라이선스 종류 확정 및 `LICENSE` 파일 추가
- [ ] `docs/CONTRIBUTING.md` 파일 작성
- [ ] **디렉터리 구조 확인**: 위 구조는 import 경로로 추론한 것입니다. `main.py`/`run.py`가 `backend/` 루트에, 나머지 모듈이 `backend/app/` 패키지에 위치해야 `from app import ...`와 상대 import가 함께 동작합니다. 실제 배치를 확인하세요.
- [ ] **`vite_config.js` 파일명 확인**: Vite는 `vite.config.js`(또는 `.mjs`/`.ts`)를 인식합니다. 제공된 `vite_config.js`는 실제로 `vite.config.js`여야 합니다.
- [ ] **`src/assets/mainlogo.png` 확인**: `index.html`과 `Header`가 참조하지만 제공된 파일 목록에는 없습니다. 저장소에 포함되어야 합니다.
- [ ] **`RESEND_API_KEY` 확인**: `config.py`에서 로딩하지만 어떤 라우터에서도 사용되지 않습니다. 향후 기능용이라면 유지하고, 아니라면 제거를 검토하세요.
- [ ] **Node.js 최소 버전 확인**: `package.json`에 `engines`가 없어 18 이상으로 가정했습니다. 실제 지원 버전을 명시하세요.
- [ ] **모델의 Django 스타일 테이블명 확인**: `accounts_user`, `bankings_depositbaselist` 등 테이블명과 `User` 모델의 `is_superuser`/`is_staff`/`date_joined` 필드는 기존 Django 스키마와의 호환을 위한 것으로 보입니다. 신규 DB 생성인지 기존 DB 연동인지 확인하세요.