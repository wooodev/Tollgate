from fastapi import FastAPI

from app.api import admin, health

app = FastAPI(title="llm-gateway")
app.include_router(health.router)
app.include_router(admin.router)
