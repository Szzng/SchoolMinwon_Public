# SchoolMinwon - AI-Powered School Complaint Management System

> 학교 민원을 효율적으로 관리하는 AI 기반 학생/학부모 민원 접수 및 처리 시스템

![License](https://img.shields.io/badge/license-GPL--3.0-blue)
![Vue](https://img.shields.io/badge/vue-3-green)
![Django](https://img.shields.io/badge/django-5.2-darkred)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Node](https://img.shields.io/badge/node-%3E%3D20-brightgreen)

## 🌟 주요 기능

### 🤖 AI 기반 자동 응답 (Upstage Solar LLM + RAG)
- **지능형 민원 분석**: 학생/학부모의 민원을 자동으로 분석하고 카테고리 분류
- **맥락 기반 응답**: 학교 공지사항 데이터베이스(RAG)를 활용한 자동 응답 생성
- **위험도 탐지**: 학교폭력, 성폭력 등 민감한 내용 자동 감지 및 관리자 알림

### 📋 민원 관리 워크플로우
- **단계별 상태 관리**: 접수 → 1차검토 → 2차검토 → 교무실처리 → 답변완료 → 종료
- **자동 상태 전환**: 특정 조건에서 자동으로 다음 단계로 진행
- **댓글 기반 상호작용**: 학생, 학부모, 교직원, AI가 참여하는 협업 환경

### 👥 다중 사용자 지원
- **학생/학부모**: 민원 접수, 진행상황 추적, 응답 확인
- **학교 교직원**: 대시보드에서 모든 민원 관리, 우선순위 지정, 답변 작성
- **AI 어시스턴트**: 자동 분류, 응답, 위험도 분석

### 📊 교육용 프로젝트
- **완전한 전체 스택**: 프론트엔드에서 백엔드, AI 통합까지 모든 기술 스택 포함
- **최신 웹 기술**: Vue 3 + TypeScript, Django REST Framework, Vite
- **학습용 예제**: 복잡한 시스템 구축의 모범 사례 제시

## 🛠️ 기술 스택

### Frontend
- **Vue 3** - 리액티브 UI 프레임워크
- **TypeScript** - 타입 안전성
- **Vite** - 초고속 빌드 도구
- **Tailwind CSS v4** - 유틸리티 기반 스타일링
- **Pinia** - 상태 관리 (localStorage 지속성)
- **Vue Router** - 클라이언트 라우팅
- **Vitest** - 단위 테스트
- **Playwright** - E2E 테스트

### Backend
- **Django 5.2.8** - Python 웹 프레임워크
- **Django REST Framework** - RESTful API 개발
- **Django SimpleJWT** - JWT 인증
- **django-cors-headers** - CORS 지원
- **django-fsm** - 상태 머신 관리

### AI/ML
- **Upstage Solar LLM** - 한글 최적화 대형 언어 모델
- **ChromaDB** - 임베딩 기반 벡터 데이터베이스 (RAG)
- **OpenAI 호환 API** - Upstage API

### Database & Infrastructure
- **SQLite** (개발)
- **MySQL/PostgreSQL** (프로덕션 준비)
- **Redis** - Celery 브로커 (백그라운드 작업)
- **Celery** - 비동기 작업 처리

## 🚀 빠른 시작

### 전제 조건
- Python 3.9+
- Node.js 20.19.0 이상 또는 22.12.0 이상
- Redis (선택사항, Celery 사용 시)

### 프론트엔드 설정

```bash
cd front
npm install
npm run dev
# http://localhost:5173 에서 접속 가능
```

### 백엔드 설정

```bash
cd back

# 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 설정
cp .env.example .env
# .env 파일을 열고 필요한 값 설정 (특히 UPSTAGE_API_KEY)

# 데이터베이스 마이그레이션
python manage.py migrate

# 개발 서버 실행
python manage.py runserver
# http://localhost:8000 에서 접속 가능
```

## 📝 환경 변수 설정

### Backend (.env)

```bash
# Django 설정
SECRET_KEY=your-secret-key
DEBUG=False  # 프로덕션에서는 False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# API 설정
UPSTAGE_API_KEY=your-upstage-api-key  # https://console.upstage.ai 에서 발급

# 데이터베이스 (SQLite 기본값)
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=school_minwon
# DB_USER=your_user
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=3306

# CORS 설정
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://yourdomain.com

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Frontend (.env.local)

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 🧪 테스트

### Frontend 단위 테스트
```bash
cd front
npm run test:unit                    # 모든 테스트 실행
npx vitest run src/__tests__/App.spec.ts  # 특정 파일만 테스트
npx vitest --ui                      # 대시보드 모드
```

### Frontend E2E 테스트
```bash
cd front
npx playwright install               # 첫 설치 시만 필요
npm run build && npm run test:e2e    # E2E 테스트 실행
npm run test:e2e -- --debug          # 디버그 모드
```

### Backend 테스트
```bash
cd back
python manage.py test                # 모든 테스트
python manage.py test accounts.tests.TestUserLogin  # 특정 테스트
```

## 📦 프로덕션 배포

### 프론트엔드 빌드
```bash
cd front
npm run build
# dist/ 디렉토리에 정적 파일 생성
# 웹 서버(Nginx, Apache 등)에 배포
```

### 백엔드 배포
```bash
cd back
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
# gunicorn으로 실행
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 🏗️ 프로젝트 구조

```
SchoolMinwon/
├── front/                    # Vue 3 SPA
│   ├── src/
│   │   ├── components/       # 재사용 가능한 컴포넌트
│   │   ├── views/            # 페이지 컴포넌트
│   │   ├── stores/           # Pinia 상태 관리
│   │   ├── router/           # Vue Router 설정
│   │   └── __tests__/        # 유닛 테스트
│   ├── e2e/                  # Playwright E2E 테스트
│   └── package.json
│
├── back/                     # Django REST API
│   ├── config/               # Django 프로젝트 설정
│   ├── accounts/             # 사용자 인증 앱
│   ├── minwon/               # 민원 관리 앱
│   │   ├── models.py         # 데이터 모델
│   │   ├── views.py          # API 뷰
│   │   ├── ai/               # AI 기능 (RAG, LLM)
│   │   └── migrations/       # DB 마이그레이션
│   ├── manage.py
│   └── requirements.txt
│
└── README.md
```

## 🤝 기여하기

이 프로젝트는 교육 목적의 오픈소스 프로젝트입니다. 개선 사항, 버그 리포트, 기능 제안을 환영합니다!

1. Fork 하기
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📄 라이선스

GNU General Public License v3.0 - [LICENSE](LICENSE) 파일 참고

라이선스의 주요 내용:
- 자유로운 수정 및 배포 가능
- 수정된 코드도 GPL-3.0 라이선스로 공개 필수 (Copyleft)
- 상업적 이용 가능

## 🔗 참고 자료

- [Vue 3 공식 문서](https://vuejs.org/)
- [Django 공식 문서](https://www.djangoproject.com/)
- [Upstage Solar LLM](https://www.upstage.ai/)
- [ChromaDB 문서](https://docs.trychroma.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)

## 👨‍💻 개발자

- https://szzng.zzolab.com/

## ❓ FAQ

**Q: Upstage API 키가 필요한가요?**
A: AI 자동 응답 기능이 필요하면 필요합니다. 없으면 수동 답변 처리로 사용 가능합니다.

**Q: 데이터베이스를 변경할 수 있나요?**
A: 네, 환경 변수로 MySQL, PostgreSQL 등 다양한 데이터베이스 지원합니다.

---

**마지막 업데이트**: 2025년 11월 19일
