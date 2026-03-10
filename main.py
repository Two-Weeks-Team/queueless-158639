import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from routes import router

app = FastAPI()


@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)

@app.get("/health", response_model=dict)
async def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root():
    html = """
    <html>
      <head>
        <title>Queueless</title>
        <style>
          body { background-color:#111; color:#eee; font-family:Arial,Helvetica,sans-serif; padding:2rem; }
          h1 { color:#0ff; }
          a { color:#0bf; }
          .section { margin-bottom:2rem; }
          .endpoint { margin-left:1rem; }
        </style>
      </head>
      <body>
        <h1>Queueless</h1>
        <p>Transform wait times into seamless experiences.</p>
        <div class="section">
          <h2>API Endpoints</h2>
          <ul>
            <li class="endpoint"><strong>GET</strong> /health – health check</li>
            <li class="endpoint"><strong>GET</strong> /queue – list current queue entries</li>
            <li class="endpoint"><strong>GET</strong> /wait-time?location_id=&lt;id&gt; – AI‑predicted wait time</li>
            <li class="endpoint"><strong>GET</strong> /recommendations?customer_id=&lt;id&gt; – AI‑generated menu suggestions</li>
          </ul>
        </div>
        <div class="section">
          <h2>Tech Stack</h2>
          <ul>
            <li>FastAPI 0.115.0 (Python 3.12+)</li>
            <li>PostgreSQL via SQLAlchemy 2.0.35</li>
            <li>DigitalOcean Serverless Inference (openai‑gpt‑oss‑120b)</li>
            <li>Tailwind CSS, Next.js 15 (frontend – not shown here)</li>
          </ul>
        </div>
        <div class="section">
          <a href="/docs">OpenAPI Docs</a> | <a href="/redoc">ReDoc</a>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)
