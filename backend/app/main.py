# backend/app/main.py

from fastapi import FastAPI
from app.api.routes_health import router as health_router
from app.core.logging_config import setup_logging
from app.api.routes_production import router as production_router
from app.api.routes_downtime import router as downtime_router
from app.api.routes_tickets import router as tickets_router
from app.api.routes_auth import router as auth_router
from app.api.routes_chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware




setup_logging()

app = FastAPI(
    title="ProdOps AI Backend",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(health_router)
app.include_router(production_router)
app.include_router(downtime_router)
app.include_router(tickets_router)
app.include_router(auth_router)
app.include_router(chat_router)