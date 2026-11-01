import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import engine, Base, check_db_health
import backend.app.models  # ensure models are registered
from backend.app.api.v1.routes import (
    auth,
    students,
    faculty,
    applications,
    documents,
    academic_records,
    results,
    audit,
    admin,
    communication,
    chat,
    roster,
    website,
)
import logging

logger = logging.getLogger("pocketuni.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure storage subdirectories exist
    for sub in ["resumes", "application_documents", "institutional_documents", "profile_assets", "temporary"]:
        os.makedirs(os.path.join(settings.STORAGE_DIR, sub), exist_ok=True)
    
    # Verify database connection on startup
    db_info = check_db_health()
    logger.info(f"Database readiness verified: {db_info['driver']} -> {db_info['database']} ({db_info['url']})")
    yield


app = FastAPI(
    title=f"{settings.PROJECT_NAME} Backend API",
    description="PocketUni Modular Backend (Module 1: Foundation, Auth, Super Admin & Document Management)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/api/health", tags=["System"])
def health_check():
    db_status = check_db_health()
    return {
        "status": "HEALTHY",
        "service": "PocketUni Backend",
        "module": "1 of 3 (Foundation, Auth, Super Admin, Doc Management)",
        "environment": settings.ENVIRONMENT,
        "database": db_status
    }

# API v1 routes
api_prefix = settings.API_V1_STR
app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
app.include_router(students.router, prefix=f"{api_prefix}/students", tags=["Students"])
app.include_router(faculty.router, prefix=f"{api_prefix}/faculty", tags=["Faculty"])
app.include_router(applications.router, prefix=f"{api_prefix}/applications", tags=["Applications"])
app.include_router(documents.router, prefix=f"{api_prefix}/documents", tags=["Documents"])
app.include_router(academic_records.router, prefix=f"{api_prefix}/academic-records", tags=["Academic Records"])
app.include_router(results.router, prefix=f"{api_prefix}/results", tags=["Results & Marks"])
app.include_router(audit.router, prefix=f"{api_prefix}/audit", tags=["Audit Logs"])
app.include_router(admin.router, prefix=f"{api_prefix}/admin", tags=["Super Admin"])
app.include_router(communication.router, prefix=f"{api_prefix}/communication", tags=["Communication"])
app.include_router(chat.router, prefix=f"{api_prefix}/chat", tags=["AI Chat & Conversations"])
app.include_router(roster.router, prefix=f"{api_prefix}/admin/roster", tags=["Master Roster Management"])
app.include_router(website.router, prefix=f"{api_prefix}/website", tags=["Website Ingestion & Portals"])
