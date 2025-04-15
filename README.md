# World Wide Wealth (WWW)
<p align="center">
  <img src="./readimg/logoimage.png" width="300" alt="World Wide Wealth Logo"/>
</p>

SSAFY 관통 프로젝트 - 금융 상품 추천 플랫폼<br>
개발 기간 : 2024/11/18 ~ 2024/11/26 (약 2주)

## 프로젝트 소개
World Wide Wealth는 사용자 맞춤형 금융 상품 추천 시스템으로, 예금 및 적금 상품의 실시간 비교, 챗봇 기반의 설문 조사, 맞춤형 금융 상품 추천, 환율 계산기, 주변 은행 위치 검색 등의 기능을 제공합니다.

외부 금융기관의 API를 활용하여 실시간 정보를 제공하며, 사용자는 로그인 후 개인 자산 정보, 선호도를 기반으로 적절한 상품을 추천받을 수 있습니다. 또한 금융 상품에 대한 리뷰 및 커뮤니티 기능을 통해 정보 공유가 가능합니다.

### 배포 주소
개발 버전: `배포 X`<br>
Frontend 서버: `배포 X`<br>
Backend 서버: `배포 X`<br>

### 팀 소개
| 이름   | 역할         | GitHub 링크 | 비고 |
|--------|--------------|-------------|------|
| 박진수 | 팀장, 백엔드 | 🔧 | Vue.js 기반 프론트엔드 개발 |
| 김찬호 | 팀원, 프론트 | [@nonamed19](https://github.com/nonamed19) | Django 기반 백엔드 개발 |

## 시작 가이드

### Requirements
For building and running the application you need:
```
- Python 3.9.13
- Django 4.2.16
- Node.js LTS (16+)
- Vue 3
```
### Installation

```bash
$ git clone https://github.com/🔧/world-wide-wealth.git
$ cd world-wide-wealth
```
#### Backend
```bash
$ cd final-pjt-back
$ python -m venv venv
$ source venv\Scripts\activate
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py runserver
```
#### Frontend
```bash
$ cd ../final-pjt-front
$ npm install
$ npm run dev
```

## 기술 스택

### Environment
- OS: Windows
- DB: SQLite
- API: OpenAI, 금융감독원, 한국수출입은행, 네이버 뉴스, 카카오맵

### Config
- dotenv: 환경변수 관리
- Resend API: 이메일 발송

### Development
- Backend: Django + Django REST Framework
- Frontend: Vue 3 + Composition API + Pinia
- ML(AI): RandomForestClassifier

### Communication
- GitHub
- GitLab
- Notion


## 화면 구성

| 메인 페이지 | 금융상품 리스트 | 금융상품 상세 | 금융상품 추천 |
|:------------:|:------------:|:------------:|:------------:|
| <img src="./readimg/main_page.jpg" height="200px" title="main_page"/> | <img src="./readimg/bankings_list.jpg" height="200px" title="bankings_list"/> | <img src="./readimg/bankingsdetail.png" height="200px" title="bankings_detail"/> | <img src="./readimg/bankings_recommend.jpg" height="200px" title="bankings_recommend"/> |
| 금융상품 비교 | 근처 은행 찾기 | 환율 정보 | 경제 뉴스 |
| <img src="./readimg/bankings_comparison.jpg" height="200px" title="bankings_comparison"/> | <img src="./readimg/bank_locations.jpg" height="200px" title="bank_locations"/> | <img src="./readimg/currencies.jpg" height="200px" title="currencies"/> | <img src="./readimg/bankings_news.jpg" height="200px" title="bankings_news"/> |
|  |  |  |  | 

## 주요 기능

- 맞춤형 금융 상품 추천 (설문 기반 + ML 기반)
- 예금/적금 상품 비교 및 상세 조회
- 챗봇 UI 기반 설문 인터페이스
- 사용자 기반 리뷰 작성, 댓글, 좋아요
- 환율 계산기 기능 (한국수출입은행 API)
- 카카오맵을 활용한 주변 은행 검색
- 금융 뉴스 실시간 제공 (네이버 API)
- 구독 기능 및 이메일 알림

## 아키텍쳐

### API 명세서
<p>
  <img src="./readimg/function.PNG" alt="API 명세서"/>
</p>

### ERD
<p align="center">
  <img src="./readimg/erd_black.png" alt="ERD"/>
</p>

## 기타 추가 사항들

보안 관련: API Key는 `.env` 파일로 관리하며 `.gitignore`에 포함되어 있습니다.

향후 계획:
- 예/적금 외의 투자 상품 확장
- 딥러닝 기반 추천 고도화
- 글로벌 서비스 확장 준비

### 느낀 점, 후기
**박진수** : 머신러닝 분류 작업에서 기준치에 대한 명확한 이해가 부족했다 사료돼, 예측의 정확도가 아쉬웠다. 객체를 학습하는 과정을 발전시키고싶은 욕심이 생겼다.
백엔드의 필드들을 미리 정리하고 필요한 부분을 표시해가며 개발해야하는 필요성을 뼈저리게 느꼈다. 또한 디자인과 배치를 좀 더 미리 설정하고 구현할 수 있도록 피그마나 프론트엔드 측면에서 다른 배움의 과정의 진행할 예정이다.

**김찬호** : Python 및 Django를 활용하여 Back 개발을 수행하며 django app 및 각 models의 관리가 철저하게 관리 되어야 함을 학습하였으며, 초기 기획 단계에서 얼마나 프로젝트를 구체적으로 계획하느냐에 따라 향후 개발 프로젝트 수행 중에 마주할 문제점들을 최소화할 수 있다는 것을 경험하였습니다. 뿐만 아니라, 개발 프로젝트 진행 시에는 back과 front로 업무를 분할하여 코드 작성을 진행하지만, 개발 프로세스를 고려하면 분업보다 협동의 마음가짐으로 협력이 중요하다는 것을 학습하였습니다.