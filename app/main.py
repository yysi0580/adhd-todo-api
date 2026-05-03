from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.db import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="ADHD-focused todo API that turns brain dumps into selectable micro-actions.",
    lifespan=lifespan,
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def api_home(request: Request) -> str:
    routes = []
    for route in request.app.routes:
        methods = sorted(
            method for method in getattr(route, "methods", []) if method not in {"HEAD", "OPTIONS"}
        )
        path = getattr(route, "path", "")
        if not methods or not path:
            continue
        routes.append(
            {
                "path": path,
                "methods": methods,
                "name": getattr(route, "name", ""),
                "include_in_schema": getattr(route, "include_in_schema", False),
            }
        )

    route_rows = "\n".join(
        _route_row(route) for route in sorted(routes, key=lambda item: item["path"])
    )

    return f"""
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ADHD Todo API</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --text: #1f2937;
      --muted: #667085;
      --line: #d9dee8;
      --accent: #2563eb;
      --green: #047857;
      --orange: #b45309;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, sans-serif;
      line-height: 1.55;
    }}
    main {{
      width: min(1080px, calc(100% - 32px));
      margin: 32px auto;
    }}
    header {{
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 32px;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 20px;
    }}
    p {{
      margin: 0;
      color: var(--muted);
    }}
    .links {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }}
    a.button {{
      display: inline-flex;
      align-items: center;
      min-height: 38px;
      padding: 0 14px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--accent);
      text-decoration: none;
      font-weight: 700;
    }}
    section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin: 16px 0;
    }}
    .method {{
      display: inline-block;
      min-width: 58px;
      margin-right: 8px;
      color: white;
      text-align: center;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 700;
      line-height: 24px;
    }}
    .get {{ background: var(--green); }}
    .post {{ background: var(--accent); }}
    .patch {{ background: var(--orange); }}
    .put {{ background: #7c3aed; }}
    .delete {{ background: #dc2626; }}
    code {{
      font-family: Consolas, monospace;
      font-size: 14px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      padding: 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      background: #fbfcff;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>ADHD Todo API</h1>
      <p>FastAPI 앱에 실제 등록된 route 목록을 자동으로 읽어 보여줍니다.</p>
      <div class="links">
        <a class="button" href="/docs">Swagger API 문서</a>
        <a class="button" href="/redoc">ReDoc 문서</a>
        <a class="button" href="/openapi.json">OpenAPI JSON</a>
        <a class="button" href="/api/v1/health">Health Check</a>
      </div>
    </header>

    <section>
      <h2>실제 등록된 엔드포인트</h2>
      <table>
        <thead>
          <tr>
            <th>Method</th>
            <th>Path</th>
            <th>Route Name</th>
            <th>OpenAPI</th>
          </tr>
        </thead>
        <tbody>
          {route_rows}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


app.include_router(api_router, prefix="/api/v1")


def _route_row(route: dict) -> str:
    method_badges = " ".join(
        f'<span class="method {method.lower()}">{method}</span>' for method in route["methods"]
    )
    in_openapi = "yes" if route["include_in_schema"] else "no"
    return f"""
        <tr>
          <td>{method_badges}</td>
          <td><code>{route["path"]}</code></td>
          <td>{route["name"]}</td>
          <td>{in_openapi}</td>
        </tr>
        """
