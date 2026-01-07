from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, Auth, user, api_key, analysis, analysis_history, analysis_result, analysis_upload, analysis_worker
from app.routes import admin_users, admin_subscription, admin_api_keys, admin_usage, admin_analytics, subscription, migrate
from app.routes.test import core_test
app = FastAPI()
# Configure CORS - FIXED VERSION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(Auth.router)
app.include_router(user.router)
app.include_router(api_key.router)
app.include_router(core_test.router)
app.include_router(analysis.router)
app.include_router(analysis_history.router)
app.include_router(analysis_result.router)
app.include_router(analysis_upload.router)
# app.include_router(analysis_worker.router)
app.include_router(admin_users.router)
app.include_router(admin_subscription.router)
app.include_router(admin_api_keys.router)
app.include_router(admin_usage.router)
app.include_router(admin_analytics.router)
app.include_router(subscription.router)
app.include_router(migrate.router)