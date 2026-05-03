# ADHD Todo API

ADHD 사용자를 위한 투두앱 백엔드 MVP입니다.

이 앱은 "할 일 목록을 관리하는 앱"이 아니라, 사용자의 결정 부담을 줄이고 실행 가능한 작은 행동 후보를 제시하는 앱입니다. 사용자는 생각을 정리해서 입력하지 않아도 되고, 시스템이 여러 micro-step suggestion으로 분해한 뒤 그중 하나를 선택해 Action으로 실행합니다.

핵심 원칙:

- 처음부터 행동 1개만 강제하지 않고 여러 suggestion을 제시합니다.
- 입력은 한 줄 또는 장문 모두 허용합니다.
- 장문 입력은 2~5개의 micro-step suggestion으로 자동 분해합니다.
- 사용자는 suggestion 중 하나를 선택하거나, 전부 패스하거나, 더 작게 만들기를 요청할 수 있습니다.
- 실행은 suggestion 선택 후 하나의 Action으로 수렴합니다.
- completed/aborted는 압박용 성공/실패가 아니라 다음 제안을 조절하기 위한 패턴 데이터입니다.

## 기술 스택

- Python
- FastAPI
- SQLAlchemy
- SQLite 기본값, PostgreSQL 운영 권장
- Alembic 마이그레이션
- Docker 배포 가능

## 현재 구현 범위

현재 제안 생성은 AI가 아니라 `RuleBasedSuggestionService` 기반입니다.

- 쉼표, 줄바꿈, 마침표, "그리고", "해야 하고", "또", "먼저" 같은 표현을 기준으로 입력을 나눕니다.
- 메일/문서/공유 같은 키워드에 따라 2~5분짜리 micro-step을 만듭니다.
- 추후 LLM 기반 구현은 같은 `SuggestionService` 인터페이스를 구현해서 교체하면 됩니다.

핵심 기능:

- Brain Dump: 사용자가 생각을 정리하지 않고 그대로 입력합니다.
- 자동 분해: 장문 입력을 여러 micro-step으로 분해합니다.
- 다중 제시: 처음부터 여러 개의 행동 후보를 제시합니다.
- 선택 기반 실행: 여러 후보 중 하나를 선택하면 Action으로 전환합니다.
- 평가 없는 반응: 실패/성공 압박 없이 reaction만 저장합니다.
- make_smaller: 부담스러운 제안을 1~3개의 더 작은 행동으로 재생성합니다.

## 코드 구조

```text
app/
  main.py                    # FastAPI 앱 생성, route introspection 페이지
  api/
    v1/
      router.py              # v1 endpoint 묶음
      endpoints/             # HTTP 요청/응답만 담당
        health.py
        sessions.py
        brain_dumps.py
        suggestions.py
        actions.py
        feedback.py
  core/
    config.py                # 환경변수 설정
    db.py                    # SQLAlchemy engine/session
    exceptions.py            # 공통 HTTP 예외 helper
  domain/
    enums.py                 # 상태/반응 enum
    time.py                  # 공통 시간 함수
  models/                    # SQLAlchemy 테이블 모델
    session.py
    brain_dump.py
    suggestion.py
    action.py
    feedback.py
  schemas/                   # Pydantic 요청/응답 스키마
    common.py
    session.py
    brain_dump.py
    suggestion.py
    action.py
    feedback.py
  repositories/              # DB 접근만 담당
    session_repository.py
    brain_dump_repository.py
    suggestion_repository.py
    action_repository.py
    feedback_repository.py
  services/                  # 비즈니스 흐름 담당
    brain_dump_service.py
    suggestion_service.py
    action_service.py
    feedback_service.py
    suggestion/              # 제안 생성 세부 로직
      splitter.py
      micro_step_builder.py
      safety_net.py
      smaller.py
      generator.py
```

수정 위치 기준:

- API 경로/HTTP 응답 수정: `app/api/v1/endpoints/`
- Brain Dump 생성 흐름 수정: `app/services/brain_dump_service.py`
- Action 상태 변경 수정: `app/services/action_service.py`
- Feedback 저장 수정: `app/services/feedback_service.py`
- 문장 분해 규칙 수정: `app/services/suggestion/splitter.py`
- 제안 문구 수정: `app/services/suggestion/micro_step_builder.py`
- 더 작은 단계 생성 수정: `app/services/suggestion/smaller.py`
- 안전망 행동 수정: `app/services/suggestion/safety_net.py`
- DB 쿼리 수정: `app/repositories/`
- 테이블 구조 수정: `app/models/` + `alembic/versions/`

## 로컬 실행

```powershell
cd C:\ytheory\adhd-todo-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

## 핵심 API

```http
GET /api/v1/health
POST /api/v1/sessions
POST /api/v1/brain-dumps
GET /api/v1/sessions/{session_id}/suggestions
POST /api/v1/suggestions/{suggestion_id}/make-smaller
POST /api/v1/actions
PATCH /api/v1/actions/{action_id}
POST /api/v1/actions/{action_id}/complete
POST /api/v1/actions/{action_id}/abort
POST /api/v1/feedback
```

## 예시 요청

```http
POST /api/v1/brain-dumps
Content-Type: application/json

{
  "raw_text": "프로젝트 발표 준비해야 하는데 자료도 없고 교수님 메일도 보내야 하고 팀 일정도 공유해야 함"
}
```

응답은 새 세션, Brain Dump, 2~5개의 행동 제안을 함께 반환합니다.

make_smaller 예시:

```http
POST /api/v1/suggestions/{suggestion_id}/make-smaller
```

응답은 1~3개의 더 작은 suggestion 배열입니다.

Action 완료/중단 예시:

```http
POST /api/v1/actions/{action_id}/complete
Content-Type: application/json

{
  "note": "부담 없이 완료"
}
```

```http
POST /api/v1/actions/{action_id}/abort
Content-Type: application/json

{
  "reason": "지금은 너무 크게 느껴짐"
}
```

Feedback reaction:

```text
do | snooze | pass | make_smaller | capture_only
```

## 배포 방식

가장 단순한 배포 흐름:

1. GitHub에 이 프로젝트를 올립니다.
2. Render 같은 Docker 지원 서비스에서 새 Web Service를 만듭니다.
3. 이 repo를 연결합니다.
4. Health check path를 `/api/v1/health`로 둡니다.

초기 MVP는 SQLite로 실행할 수 있지만, 실제 운영에서는 `DATABASE_URL`을 PostgreSQL로 바꾸는 것을 권장합니다.

PostgreSQL 예시:

```text
DATABASE_URL=postgresql+psycopg://user:password@host:5432/adhd_todo
AUTO_CREATE_TABLES=false
```

마이그레이션:

```bash
alembic upgrade head
```

로컬 SQLite에서 빠르게 확인할 때는 `AUTO_CREATE_TABLES=true`를 유지하면 앱 시작 시 테이블을 자동 생성합니다. 운영에서는 `AUTO_CREATE_TABLES=false`로 두고 Alembic을 사용하세요.

## yangtheory.site로 열기

현재 `yangtheory.site`와 `www.yangtheory.site`가 어떤 공인 IP를 바라보고 있다면, 그 서버에서 이 API를 실행하고 80/443 포트를 연결하면 됩니다.

서버에서 API 실행:

```bash
cd /path/to/adhd-todo-api
python -m venv .venv
source .venv/bin/activate
pip install .
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Nginx 리버스 프록시 예시는 `deploy/nginx.yangtheory.site.conf`에 있습니다.

```bash
sudo cp deploy/nginx.yangtheory.site.conf /etc/nginx/sites-available/adhd-todo-api
sudo ln -s /etc/nginx/sites-available/adhd-todo-api /etc/nginx/sites-enabled/adhd-todo-api
sudo nginx -t
sudo systemctl reload nginx
```

HTTPS 적용:

```bash
sudo certbot --nginx -d yangtheory.site -d www.yangtheory.site
```

이후 접속 주소:

```text
https://yangtheory.site/
https://yangtheory.site/docs
```

## 다음 개발 순서

1. 사용자 인증 추가
2. Render/Railway/Fly 배포 시 PostgreSQL 연결
3. 제안 생성 로직을 LLM 서비스 구현체로 추가
4. 세션별 반응 패턴 기반 난이도 조절
5. 프론트엔드에서 Brain Dump 입력과 Suggestion 선택 UI 연결
