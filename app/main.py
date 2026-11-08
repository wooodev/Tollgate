from fastapi import FastAPI

from app.api import health

app = FastAPI(title="llm-gateway")
app.include_router(health.router)
