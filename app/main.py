# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import BusinessError
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging(settings.debug)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}

@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
from app.routers import auth, posts,tag

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(tag.router)