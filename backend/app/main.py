from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import api_router
from app.core.config import get_settings
from app.services.errors import AppError

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError): return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.get("/health")
async def health(): return {"status": "ok"}

app.include_router(api_router, prefix=settings.api_v1_prefix)
