# ADHD Todo API

ADHD 사용자를 위한 투두앱 백엔드 MVP입니다.

핵심 방향은 일반적인 할 일 목록 관리가 아니라, 무질서한 입력을 받아 지금 선택할 수 있는 작은 행동 후보를 제시하는 것입니다.

## 기술 스택

- Python
- FastAPI
- SQLAlchemy
- SQLite 기본값
- Docker 배포 가능

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

## 배포 방식

가장 단순한 배포 흐름:

1. GitHub에 이 프로젝트를 올립니다.
2. Render 같은 Docker 지원 서비스에서 새 Web Service를 만듭니다.
3. 이 repo를 연결합니다.
4. Health check path를 `/api/v1/health`로 둡니다.

초기 MVP는 SQLite로 실행할 수 있지만, 실제 운영에서는 `DATABASE_URL`을 PostgreSQL로 바꾸는 것을 권장합니다.

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
2. PostgreSQL 전환 및 마이그레이션 도입
3. 제안 생성 로직을 LLM 서비스로 분리
4. 세션별 반응 패턴 기반 난이도 조절
5. 프론트엔드에서 Brain Dump 입력과 Suggestion 선택 UI 연결
