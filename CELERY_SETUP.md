# Celery AI 응답 자동 생성 설정 가이드

이 문서는 Celery를 사용하여 민원 생성 시 백그라운드에서 AI 응답을 자동으로 생성하도록 설정하는 방법을 설명합니다.

## 구현 개요

민원 제출 시:
1. **백엔드**: 민원을 생성하고 즉시 응답 (상태: `AI응답대기`)
2. **Celery Task**: 백그라운드에서 `generate_ai_response_task` 실행
   - `get_ai_response()` 호출하여 AI 응답 생성
   - `complaint.ai_response` 필드에 저장
   - 상태를 `AI응답완료`로 전환
3. **프론트엔드**: 상태가 `AI응답대기`일 때 3초마다 폴링
   - AI 응답 완료되면 자동으로 표시
   - 폴링 중지

## 설치된 파일 및 수정 사항

### 백엔드 (Django)

**새 파일:**
- `back/config/celery.py` - Celery 앱 설정
- `back/minwon/tasks.py` - `generate_ai_response_task` 구현

**수정된 파일:**
- `back/config/__init__.py` - Celery 앱 import
- `back/config/settings.py` - Celery 설정 추가
- `back/minwon/views.py` - `ComplaintViewSet.create()` 수정, `tasks.py` import

**설치된 패키지:**
- celery 5.5.3
- redis 7.0.1

### 프론트엔드 (Vue)

**수정된 파일:**
- `front/src/views/ComplaintStatusDetail.vue` - 폴링 로직 추가

## 실행 방법

### 1단계: Redis 서버 시작

```bash
# macOS (Homebrew 설치된 경우)
redis-server

# 또는 Docker 사용
docker run -d -p 6379:6379 redis:latest
```

### 2단계: Celery Worker 시작

별도의 터미널에서:

```bash
cd /Users/szzng/myproject/SchoolMinwon/back
source venv/bin/activate
celery -A config worker -l info
```

**예상 출력:**
```
[2024-11-14 14:30:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2024-11-14 14:30:00,100: INFO/MainProcess] mingle() finished with 0 tasks
[2024-11-14 14:30:00,200: INFO/MainProcess] celery@hostname.com ready.
```

### 3단계: Django 개발 서버 시작

```bash
cd /Users/szzng/myproject/SchoolMinwon/back
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### 4단계: Vue 개발 서버 시작

```bash
cd /Users/szzng/myproject/SchoolMinwon/front
npm run dev
```

## 사용 흐름

### 민원 생성 시:

1. 사용자가 `http://localhost:5173/comp/form`에서 민원 폼 작성
2. 제출 버튼 클릭
3. **백엔드 응답** (즉시):
   - 민원 생성 (ID: abc123...)
   - 상태: `AI응답대기`
   - `generate_ai_response_task.delay(complaint_id)` 호출
4. **프론트엔드 리다이렉트**:
   - `/comp/status/abc123` 상세 페이지로 이동
   - "AI가 초기 응답을 생성 중입니다..." 메시지 표시
   - 3초마다 폴링 시작
5. **Celery Worker 처리** (백그라운드):
   - `generate_ai_response_task` 실행
   - `get_ai_response()` 호출
   - AI 응답을 `complaint.ai_response` 필드에 저장
   - 상태 전환: `AI응답대기` → `AI응답완료`
6. **폴링 자동 반영** (프론트엔드):
   - 상태가 `AI응답완료`로 변경 감지
   - AI 응답 섹션 표시
   - 폴링 자동 중지

## 파일 상세 설명

### `back/config/celery.py`

```python
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()  # tasks.py 자동 발견
```

- Celery 앱 인스턴스 생성
- Django 설정에서 Celery 설정 로드
- `tasks.py`의 `@shared_task` 자동 발견

### `back/minwon/tasks.py`

```python
@shared_task(bind=True, max_retries=3)
def generate_ai_response_task(self, complaint_id):
    # 1. Complaint 조회
    # 2. get_ai_response() 호출
    # 3. complaint.ai_response 필드에 저장
    # 4. 상태 전환: AI응답완료
    # 5. 실패 시 최대 3회 재시도
```

**주요 특징:**
- `bind=True`: 재시도 기능 사용
- `max_retries=3`: 최대 3회 재시도
- 실패해도 민원은 유지 (상태: `AI응답대기`)
- 상세한 로깅

### `back/config/settings.py`

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30분
```

**설정 의미:**
- `BROKER_URL`: 작업 큐 저장소 (Redis)
- `RESULT_BACKEND`: 작업 결과 저장소 (Redis)
- `TASK_SERIALIZER`: JSON 직렬화
- `TIMEZONE`: 한국 시간대
- `TASK_TIME_LIMIT`: 각 작업은 최대 30분 내 완료

### `back/minwon/views.py`

```python
def create(self, request, *args, **kwargs):
    # ... 민원 생성 ...
    complaint = serializer.save()

    # AI 응답 비동기 생성 (Celery task)
    generate_ai_response_task.delay(complaint.id)

    # 즉시 응답 반환
    return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
```

- `.delay()`: 비동기 태스크 큐에 추가 (즉시 반환)
- 사용자 응답 시간 단축

### `front/src/views/ComplaintStatusDetail.vue`

```typescript
// 3초마다 폴링
function startPolling(id: string) {
  pollingInterval.value = setInterval(async () => {
    await store.fetchComplaintDetail(id)
    const updatedComplaint = store.getById(id)

    // AI 응답 완료되면 폴링 중지
    if (updatedComplaint?.status === 'AI응답완료') {
      stopPolling()
    }
  }, 3000)
}
```

**주요 특징:**
- 3초 주기로 최신 데이터 조회
- 상태가 `AI응답완료`되면 자동 중지
- 컴포넌트 언마운트 시 정리

## 문제 해결

### Celery Worker가 작업을 처리하지 않음

**확인 사항:**
1. Redis 서버 실행 여부: `redis-cli ping` → `PONG`
2. Worker 로그 확인: `celery -A config worker -l debug`
3. Django 설정에서 `CELERY_BROKER_URL` 확인

### "Error: getaddrinfo ENOTFOUND redis"

Redis 서버가 실행되지 않음
```bash
redis-server
```

### 작업이 3번 재시도 후 실패해도 계속 시도

설정된 동작이 맞음. 상태는 `AI응답대기` 유지되므로 수동으로 다시 시도 가능

### AI 응답 생성 느림

`get_ai_response()`가 3초 이상 걸리는 경우:
- ChromaDB 임베딩 시간
- LLM API 응답 시간
- 네트워크 지연

프론트엔드 폴링 주기(3초)를 조정 가능

## 프로덕션 배포 시 주의사항

1. **Redis 설정**:
   ```python
   CELERY_BROKER_URL = 'redis://username:password@redis-host:6379/0'
   ```

2. **Celery Worker 데몬화**:
   - systemd service 작성
   - supervisor로 관리
   - Docker 컨테이너화

3. **모니터링**:
   - Flower: `pip install flower`
   - 실행: `celery -A config flower`
   - 접속: `http://localhost:5555`

4. **로그 수집**:
   - 모든 작업 로그 저장
   - ELK Stack, Sentry 등으로 모니터링

## 참고 자료

- [Celery 공식 문서](https://docs.celeryproject.org/)
- [Django + Celery 통합](https://docs.celeryproject.org/en/stable/django/)
- [Redis 문서](https://redis.io/documentation)
