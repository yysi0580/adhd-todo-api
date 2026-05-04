# ADHD Todo API

FastAPI 기반 ADHD 타깃 실행 보조 API입니다.

이 앱은 할 일을 관리하는 앱이 아니라, 선택 부담을 시스템이 대신 떠안는 앱입니다. 사용자는 정리되지 않은 생각을 그대로 Brain Dump로 입력하고, 시스템은 그 내용을 여러 개의 작은 행동 후보로 분해합니다. 사용자는 후보 중 하나를 선택하거나, 넘기거나, 더 작게 만들기만 하면 됩니다.

## 핵심 컨셉

- Brain Dump는 한 줄과 장문을 모두 허용합니다.
- 장문 입력은 2~5개의 micro-step suggestion으로 자동 분해합니다.
- 처음부터 행동 1개만 강제하지 않고 여러 suggestion을 제시합니다.
- `reaction=do`를 보내면 선택된 suggestion이 하나의 Action으로 수렴하고 응답에 `action` 객체가 포함됩니다.
- `completed`와 `aborted`는 성공/실패 압박이 아니라 다음 제안을 위한 패턴 데이터입니다.
- 현재 suggestion 생성은 rule-based를 기본값으로 사용하고, 환경변수로 AI generator를 선택적으로 켤 수 있습니다.

## 주요 기능

- Auth: 회원가입, 로그인, JWT access/refresh token 발급, access token 재발급, 내 정보 조회
- Brain Dump: 정리되지 않은 생각 저장
- 자동 분해: 쉼표, 줄바꿈, 마침표, "그리고", "또", "해야" 같은 표현 기준 분리
- Suggestions: 여러 개의 2~5분짜리 행동 후보 생성
- AI Suggestions: 기본값은 rule-based이며, OpenAI Structured Outputs 기반 generator로 교체/활성화 가능한 구조
- make_smaller: 부담스러운 suggestion을 1~3개의 더 작은 행동으로 재생성
- Feedback: `do`, `snooze`, `pass`, `make_smaller`, `capture_only` 반응 저장
- Action: 선택된 suggestion을 실행 상태로 전환하고 `complete` 또는 `abort`
- History: 내 최근 session, brain dump, action, feedback 요약 조회
- Login protection: 비밀번호 정책, 로그인 실패 5회 차단, 주요 API rate limit

## 코드 구조

```text
app/
  main.py
  api/
    deps.py
    v1/
      router.py
      endpoints/
        auth.py
        users.py
        history.py
        health.py
        sessions.py
        brain_dumps.py
        suggestions.py
        actions.py
        feedback.py
        ai.py
  core/
    config.py
    db.py
    exceptions.py
    security.py
  domain/
    enums.py
    time.py
  models/
    user.py
    session.py
    brain_dump.py
    suggestion.py
    action.py
    feedback.py
    ai.py
  schemas/
    auth.py
    user.py
    history.py
    session.py
    brain_dump.py
    suggestion.py
    action.py
    feedback.py
  repositories/
    user_repository.py
    session_repository.py
    brain_dump_repository.py
    suggestion_repository.py
    action_repository.py
    feedback_repository.py
    ai_usage_log_repository.py
  services/
    ai/
      client.py
      prompts.py
      schemas.py
      cache.py
      rate_limit.py
      budget.py
      cost.py
      exceptions.py
      usage_logger.py
    auth_service.py
    session_service.py
    brain_dump_service.py
    suggestion_service.py
    action_service.py
    feedback_service.py
    history_service.py
    suggestion/
      ai_generator.py
      splitter.py
      micro_step_builder.py
      safety_net.py
      smaller.py
      generator.py
```

수정 위치 기준:

- API 경로/HTTP 응답: `app/api/v1/endpoints/`
- 인증/JWT: `app/core/security.py`, `app/services/auth_service.py`
- Brain Dump 흐름: `app/services/brain_dump_service.py`
- Action 상태 변경: `app/services/action_service.py`
- Feedback 반응 흐름: `app/services/feedback_service.py`
- 문장 분해 규칙: `app/services/suggestion/splitter.py`
- 제안 문구 생성: `app/services/suggestion/micro_step_builder.py`
- AI 제안 생성: `app/services/ai/`, `app/services/suggestion/ai_generator.py`
- 더 작게 만들기: `app/services/suggestion/smaller.py`
- 안전망 행동: `app/services/suggestion/safety_net.py`
- DB 쿼리: `app/repositories/`
- 테이블 변경: `app/models/` + `alembic/versions/`

## 로컬 실행

백엔드:

```powershell
cd C:\ytheory\adhd-todo-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m alembic upgrade head
uvicorn app.main:app --reload
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

## 환경변수

`.env.example`을 복사해서 `.env`를 만들고 로컬 secret을 입력합니다. `.env`는 Git에 올리지 않습니다.

Windows CMD:

```cmd
copy .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

```text
DATABASE_URL=sqlite:///./adhd_todo.db
AUTO_CREATE_TABLES=true
JWT_SECRET_KEY=change-this-secret-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=14
LOGIN_FAILURE_LIMIT=5
LOGIN_BLOCK_MINUTES=5
LOGIN_RATE_LIMIT_PER_MINUTE=20
BRAIN_DUMP_RATE_LIMIT_PER_MINUTE=60
OPENAI_API_KEY=
AI_SUGGESTION_ENABLED=false
AI_MODEL=gpt-4.1-mini
AI_TIMEOUT_SECONDS=30
AI_MAX_OUTPUT_TOKENS=700
AI_PROMPT_VERSION=v1
AI_RATE_LIMIT_PER_USER_PER_MINUTE=10
AI_RATE_LIMIT_PER_USER_PER_DAY=100
AI_RATE_LIMIT_ANONYMOUS_PER_IP_PER_MINUTE=5
AI_DAILY_GLOBAL_LIMIT=1000
AI_DAILY_GLOBAL_COST_LIMIT_USD=5.0
AI_PER_USER_DAILY_COST_LIMIT_USD=1.0
AI_MONTHLY_GLOBAL_COST_LIMIT_USD=50.0
AI_CACHE_ENABLED=true
AI_CACHE_TTL_MINUTES=30
AI_COST_LOG_ENABLED=true
AI_COST_INPUT_PER_1M=0.40
AI_COST_CACHED_INPUT_PER_1M=0.10
AI_COST_OUTPUT_PER_1M=1.60
```

운영에서는 `JWT_SECRET_KEY`를 반드시 안전한 값으로 바꾸고, `DATABASE_URL`은 PostgreSQL을 권장합니다.
`AI_SUGGESTION_ENABLED=true`와 `OPENAI_API_KEY`가 모두 설정된 경우에만 AI suggestion generator가 사용됩니다.
프론트엔드 `.env`에는 `OPENAI_API_KEY`를 넣지 않습니다. React는 OpenAI API를 직접 호출하지 않고 FastAPI 백엔드 API만 호출합니다.

```text
DATABASE_URL=postgresql+psycopg://user:password@host:5432/adhd_todo
AUTO_CREATE_TABLES=false
```

## API 흐름 예시

1. 회원가입

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "me@example.com",
  "password": "password123",
  "nickname": "시열"
}
```

`nickname`은 2~30자이며 앞뒤 공백은 제거됩니다. 기존 계정처럼 nickname이 없는 사용자는
`/api/v1/users/me`에서 `nickname: null`로 응답할 수 있고, 프론트엔드는 email 앞부분으로
안전하게 표시합니다. nickname은 아직 unique가 아니며, 수정 API는 다음 단계 TODO입니다.

2. 로그인 후 access/refresh token 받기

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "me@example.com",
  "password": "password123"
}
```

이후 보호 API에는 헤더를 붙입니다.

```http
Authorization: Bearer {access_token}
```

access token이 만료되면 refresh token으로 새 토큰을 받습니다.

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "{refresh_token}"
}
```

3. Brain Dump 입력

```http
POST /api/v1/brain-dumps
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "raw_text": "프로젝트 발표 준비해야 하는데 자료 정리하고 교수님 메일 보내고 팀 일정 공유해야 함"
}
```

응답은 새 session, brain dump, 2~5개의 suggestion을 함께 반환합니다.

4. suggestion 선택을 feedback으로 전송

```http
POST /api/v1/feedback
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "session_id": 1,
  "suggestion_id": 1,
  "reaction": "do"
}
```

`reaction=do`이면 Action이 자동 생성되고 응답에 `action_id`와 `action` 객체가 포함됩니다.

```json
{
  "feedback": {
    "reaction": "do",
    "action_id": 1
  },
  "action_id": 1,
  "action": {
    "id": 1,
    "status": "active",
    "title": "교수님 메일 초안",
    "micro_step": "메일 첫 줄만 쓰기"
  },
  "smaller_suggestions": []
}
```

5. Action 완료 또는 중단

```http
POST /api/v1/actions/{action_id}/complete
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "note": "부담 없이 완료"
}
```

```http
POST /api/v1/actions/{action_id}/abort
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "reason": "지금은 너무 크게 느껴짐"
}
```

6. 부담스러우면 더 작게 만들기

```http
POST /api/v1/feedback
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "session_id": 1,
  "suggestion_id": 1,
  "reaction": "make_smaller"
}
```

응답의 `smaller_suggestions`에 1~3개의 파생 suggestion이 포함됩니다.

## 핵심 API

```http
GET  /api/v1/health
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/users/me
POST /api/v1/auth/refresh
POST /api/v1/sessions
GET  /api/v1/sessions/{session_id}
GET  /api/v1/sessions/{session_id}/brain-dumps
GET  /api/v1/sessions/{session_id}/suggestions
GET  /api/v1/sessions/{session_id}/actions
GET  /api/v1/sessions/{session_id}/feedback
GET  /api/v1/me/history
POST /api/v1/brain-dumps
POST /api/v1/suggestions/{suggestion_id}/make-smaller
POST /api/v1/actions
GET  /api/v1/actions/{action_id}
POST /api/v1/actions/{action_id}/complete
POST /api/v1/actions/{action_id}/abort
POST /api/v1/feedback
GET  /api/v1/ai/status
GET  /api/v1/ai/usage/me
```

`GET /api/v1/users/me` 응답에는 `id`, `email`, `nickname`, `created_at`, `updated_at`이 포함됩니다.
비밀번호 해시나 token secret은 응답하지 않습니다.

`PATCH /api/v1/actions/{action_id}`는 제거되었습니다. Action 상태 변경은 `complete`와 `abort` 전용 API만 사용합니다.
`GET /api/v1/actions/{action_id}`는 본인 action만 조회할 수 있으며, 다른 사용자의 action 접근은 403으로 응답합니다.

## 보안 정책

- access token은 `ACCESS_TOKEN_EXPIRE_MINUTES` 설정에 따라 만료됩니다.
- refresh token은 `/api/v1/auth/refresh`에서 access token 재발급에 사용합니다.
- 비밀번호는 bcrypt로 해시 저장하며, 8자 이상 + 문자/숫자 포함을 요구합니다.
- 로그인 실패가 5회 반복되면 기본 5분 동안 차단합니다.
- login과 brain dump 생성에는 in-memory rate limit이 적용됩니다.
- 모든 session, brain dump, suggestion, action, feedback은 `user_id` 기준으로 보호됩니다.
- 다른 사용자의 리소스 접근은 `PERMISSION_DENIED` 계열 403 응답으로 처리합니다.

## AI suggestion

현재는 rule-based suggestion generator를 fallback으로 유지하면서, OpenAI Responses API + Structured Outputs 기반 AI generator를 선택적으로 사용할 수 있습니다. 운영 또는 실험 환경에서 아래 설정을 켜면 AI generator가 Brain Dump와 make_smaller suggestion 생성을 보조합니다.

```text
OPENAI_API_KEY=발급받은키
AI_SUGGESTION_ENABLED=true
AI_MODEL=gpt-4.1-mini
```

Windows에서 환경변수로 넣는 경우:

```cmd
setx OPENAI_API_KEY "발급받은키"
```

새 환경변수는 기존 터미널/서버 프로세스에 자동 반영되지 않으므로 백엔드 서버를 재시작합니다. 실제 키는 GitHub에 올리지 않습니다.

AI 응답은 Structured Outputs 기반 JSON으로만 받습니다.

```json
{
  "suggestions": [
    {
      "title": "string",
      "micro_step": "string",
      "effort_level": "quiet | gentle | neutral",
      "reason": "string"
    }
  ]
}
```

AI는 사용자를 평가하거나 우선순위를 강요하지 않고, 사용자가 고를 수 있는 작은 행동 후보만 생성하도록 설계되어 있습니다. OpenAI API 오류, timeout, 비어 있는 응답, 유효하지 않은 structured output이 발생하면 API 요청은 실패하지 않고 rule-based generator로 fallback합니다. Suggestion 응답의 `source` 값은 `ai` 또는 `rule_based`입니다.

AI 비용 통제:

- 로그인 사용자는 기본 분당 10회, 하루 100회로 AI 호출이 제한됩니다.
- 비로그인 사용자는 추후 확장을 위해 IP 기준 분당 5회 구조를 준비했습니다.
- 전체 일일 호출 수는 `actual_openai_call=true`인 실제 OpenAI 호출만 기준으로 계산합니다.
- 전체 일일 예상 비용, 사용자별 일일 예상 비용, 전체 월간 예상 비용 제한을 적용합니다.
- 동일 사용자/모델/prompt version/입력 hash 기준으로 기본 30분 캐시합니다.
- 캐시 hit이면 OpenAI를 다시 호출하지 않고 `actual_openai_call=false`, `source=ai_cache`로 기록합니다.
- rule-based fallback은 사용자 흐름을 유지하기 위한 안전장치이며 실제 호출 제한을 소모하지 않습니다.
- AI 성공, 실패, fallback, cache hit 사용량은 `AiUsageLog` DB 테이블에 저장합니다.
- 예상 비용은 token usage와 환경변수 가격으로 계산합니다.
- Settings 화면과 운영 점검용으로 `/api/v1/ai/status`, `/api/v1/ai/usage/me`를 제공합니다. API key 문자열은 응답하지 않습니다.

OpenAI 가격은 변경될 수 있습니다. 실제 배포 전 반드시 현재 OpenAI pricing을 확인하고 `AI_COST_*` 값을 조정하세요.

AI 실패/제한 처리:

- API key 없음 또는 `AI_SUGGESTION_ENABLED=false`: rule-based generator 사용
- OpenAI API 오류, timeout, invalid structured output, empty suggestions: rule-based fallback
- AI rate/budget limit 초과: OpenAI 호출 없이 rule-based fallback
- fallback이 발생해도 Brain Dump → Suggestions → Feedback → Action 응답 shape는 유지

`AiUsageLog.source`는 운영 분석용으로 `ai`, `ai_cache`, `fallback`, `rule_based` 값을 사용할 수 있습니다. Suggestion 응답의 `source`는 기존 프론트 호환을 위해 `ai` 또는 `rule_based` 중심으로 유지합니다.
`today`/`monthly` 필드는 API 호환을 위해 이름을 유지하지만, 실제 기준은 calendar day/month가 아니라 최근 24시간과 최근 30일입니다. calendar day 기준 집계가 필요하면 추후 timezone 기반 집계를 추가합니다.

AI status 응답 예:

```json
{
  "enabled": true,
  "model": "gpt-4.1-mini",
  "structuredOutput": true,
  "cacheEnabled": true,
  "rateLimitEnabled": true,
  "budgetLimitEnabled": true,
  "fallback": "rule_based",
  "promptVersion": "v1"
}
```

AI usage 응답 예:

```json
{
  "todayCalls": 0,
  "todayEstimatedCost": 0.0,
  "monthlyEstimatedCost": 0.0,
  "cacheHits": 0,
  "fallbackCount": 0,
  "fallbackReasons": {
    "AI_BUDGET_EXCEEDED": 1,
    "AI_INVALID_RESPONSE": 1
  },
  "lastUsedAt": null
}
```

## Feedback reaction

```text
do | snooze | pass | make_smaller | capture_only
```

- `do`: suggestion 기반 Action 생성, feedback에 `action_id` 연결
- `make_smaller`: parent suggestion을 가진 smaller suggestion 1~3개 생성
- `snooze`: 지금은 feedback만 저장, 추후 `snoozed_until` 확장 가능
- `pass`: 세션 안에서 넘겼다는 반응만 저장
- `capture_only`: 실행 없이 기록만 저장

## 테스트

```powershell
python -m black app tests alembic
python -m ruff check app tests alembic --fix
python -m pytest
```

테스트는 메모리 SQLite DB를 사용해서 로컬 개발 DB를 건드리지 않습니다. 현재 핵심 테스트에는 action 상세 조회, 타인 action 403, feedback `do` 응답의 `action` 포함 검증이 들어 있습니다.
AI 테스트는 실제 OpenAI API를 호출하지 않고 mock client로 검증합니다. 현재 포함된 항목은 AI disabled/key missing fallback, AI success, invalid output fallback, make_smaller fallback, cache 재사용, rate limit, 비용 계산, key 하드코딩 방지입니다.

실제 OpenAI smoke test는 opt-in입니다. 기본 `pytest`에서는 실제 OpenAI 호출이 발생하지 않습니다.

PowerShell:

```powershell
$env:RUN_REAL_AI_SMOKE="true"
$env:AI_SUGGESTION_ENABLED="true"
python -m pytest tests/smoke/test_real_ai.py
```

macOS/Linux:

```bash
RUN_REAL_AI_SMOKE=true AI_SUGGESTION_ENABLED=true python -m pytest tests/smoke/test_real_ai.py
```

`OPENAI_API_KEY`가 없거나 smoke flag가 없으면 smoke test는 skip됩니다.

## 반복 사용 검증

MVP 안정화 시 아래 흐름을 반복 확인합니다.

1. Brain Dump를 여러 번 생성해 session/suggestions가 섞이지 않는지 확인
2. 같은 suggestion에서 `make_smaller`를 반복 클릭해 nested 구조가 중복처럼 보이지 않는지 확인
3. 완료된 action을 다시 완료/중단할 수 없는지 확인
4. 다른 계정으로 session/action 접근 시 403이 반환되는지 확인
5. access token 만료 후 refresh token으로 재발급되는지 확인
6. AI rate/budget limit을 낮춘 테스트 설정에서 OpenAI 호출 없이 rule-based fallback이 유지되는지 확인
7. OpenAI 오류를 mock으로 발생시켜 rule-based fallback이 유지되는지 확인

## AI 운영 가이드

- `.env`는 UTF-8로 저장합니다. Windows에서 인코딩 문제가 있으면 파일을 UTF-8로 다시 저장한 뒤 서버를 재시작합니다.
- `CORS_ORIGINS`는 쉼표 문자열 또는 JSON 배열 형태를 모두 지원합니다.
- AI 제한에 걸리면 사용자 흐름은 기본 제안기로 계속 진행되고, 내부 사용량 로그에는 제한 코드가 남습니다.
- 비용 제한은 예상 token 비용 기준입니다. 실제 청구 금액과 차이가 날 수 있으니 운영 전 OpenAI pricing을 확인합니다.
- 프론트엔드는 OpenAI를 직접 호출하지 않습니다. `OPENAI_API_KEY`는 백엔드 `.env` 또는 서버 환경변수에만 둡니다.

## 배포

가장 단순한 배포 흐름:

1. GitHub에 이 프로젝트를 올립니다.
2. Render 같은 Docker 지원 서비스에서 새 Web Service를 만듭니다.
3. 이 repo를 연결합니다.
4. `DATABASE_URL`은 PostgreSQL로 설정합니다.
5. `JWT_SECRET_KEY`를 운영용 secret으로 설정합니다.
6. 배포 전 `python -m alembic upgrade head`를 실행합니다.
7. Health check path를 `/api/v1/health`로 둡니다.

초기 MVP는 SQLite로 실행할 수 있지만, 실제 운영에서는 PostgreSQL을 권장합니다.

## 배포 확인

현재 테스트용 주소:

```text
Frontend: http://yangtheory.site:5173
Backend:  http://yangtheory.site:8001
```

Health check:

```bash
curl http://yangtheory.site:8001/api/v1/health
```

브라우저 확인:

```text
http://yangtheory.site:5173/today
```

로그인 후 Brain Dump를 입력하고 `/sessions/{session_id}/suggestions`,
`/actions/{action_id}`, `/history` 흐름을 확인합니다. 백엔드 CORS에는
`http://yangtheory.site:5173` origin이 포함되어야 합니다.

## yangtheory.site로 열기

서버에서 API 실행:

```bash
cd /path/to/adhd-todo-api
python -m venv .venv
source .venv/bin/activate
pip install .
python -m alembic upgrade head
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

## 다음 개발 순서

1. PostgreSQL 운영 DB 연결 및 배포 파이프라인 정리
2. AI suggestion 품질 평가와 프롬프트 버전 관리
3. feedback 패턴 기반 난이도 조절
4. 프론트엔드에서 Brain Dump 입력과 Suggestion 선택 UI 연결
