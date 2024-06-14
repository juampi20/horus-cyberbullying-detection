import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from .api.config import settings, app_configs
from .api.router import classification_router

app = FastAPI(**app_configs)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse("/api/v1/docs")


app.include_router(classification_router, prefix="/api/v1/classification", tags=["classification"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # CLI: uvicorn src_fastapi.app.main:app --reload --port 8000
