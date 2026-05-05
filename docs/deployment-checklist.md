# Deployment Checklist

This checklist is for the production-style MVP deployment:

```text
https://yangtheory.site      -> React static frontend
https://yangtheory.site/api  -> FastAPI reverse proxy
```

Port-based URLs such as `:5173` and `:8001` are development/demo only.

## Pre-Deploy

1. Pull the latest backend and frontend repositories.
2. Confirm backend `.env` exists and is not tracked by Git.
3. Confirm `DATABASE_URL` points to PostgreSQL in production.
4. Confirm `AUTO_CREATE_TABLES=false` in production.
5. Confirm `ENVIRONMENT=production`.
6. Confirm `JWT_SECRET_KEY` is not `change-this-secret-in-production`.
7. Confirm `CORS_ORIGINS=https://yangtheory.site`.
8. Confirm `OPENAI_API_KEY` exists only in the backend environment, not the frontend.
9. Confirm `AI_SUGGESTION_ENABLED` is intentionally set.
10. Confirm DB backup/restore policy before applying migrations.

## Backend Deploy

1. Install dependencies.
2. Run `python -m alembic upgrade head`.
3. Run backend checks:

```powershell
python -m ruff check app tests alembic
python -m black --check app tests alembic
python -m pytest
```

4. Restart the backend process or systemd service.
5. Check backend directly:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

## Frontend Deploy

1. Set production `.env`:

```text
VITE_API_BASE_URL=https://yangtheory.site/api/v1
VITE_USE_MOCKS=false
```

2. Run checks:

```powershell
npm ci
npm run test:run
npm run build
```

3. Copy the built `dist` directory to `/var/www/adhd-todo-web/dist`.
4. Reload nginx.
5. Apply or renew HTTPS with certbot:

```bash
sudo certbot --nginx -d yangtheory.site -d www.yangtheory.site
```

## Production Smoke Verification

Do not run repeated real AI quality tests as part of the default deployment check.
OpenAI smoke tests are opt-in only with `RUN_REAL_AI_SMOKE=true`.

1. `curl https://yangtheory.site/api/v1/health`.
2. Open `https://yangtheory.site/today`.
3. Open `/today`, `/settings`, `/history`, `/actions/1`, and `/sessions/1/suggestions` directly and confirm React Router fallback serves the app.
4. Register or login.
5. Create a Brain Dump.
6. Confirm 2-5 Suggestions appear.
7. Select a suggestion and confirm Action creation.
8. Complete or record an abort.
9. Confirm History shows the recent flow without pressure language.
10. Create a Routine and start an Action from it.
11. Update nickname in Settings.
12. Change password in Settings, log out, and log back in with the new password.

## Troubleshooting

- `.env` should be UTF-8. If values look wrong on Windows, save the file as UTF-8 and restart the server.
- `CORS_ORIGINS` supports comma-separated strings, for example `https://yangtheory.site,http://yangtheory.site:5173`.
- DB Browser for SQLite changes are local only. Click "Write Changes" in DB Browser if you edit SQLite manually.
- `adhd_todo.db` and `*.db` are local database files and must not be committed.
- `OPENAI_API_KEY` belongs only in backend `.env` or server environment variables.
- If AI is disabled, rate-limited, budget-limited, or unavailable, the service continues with the rule-based suggestion generator.
