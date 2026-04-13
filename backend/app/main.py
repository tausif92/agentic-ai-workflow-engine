from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import setup_logging, get_logger
from app.core.config import settings

# 🔹 Import routers
from app.api.routes.health import router as health_router
from app.api.routes.workflow import router as workflow_router
from app.api.routes.agents import router as agents_router

# =========================
# 🔹 Initialize Logging
# =========================
setup_logging()
logger = get_logger(__name__)

# =========================
# 🔹 Create FastAPI App
# =========================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)

# =========================
# 🔹 Middleware (CORS)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🔹 Root Endpoint
# =========================


@app.get("/")
def root():
    logger.info("Root endpoint called")

    return {
        "message": "Agentic AI Workflow Engine Running",
        "env": settings.ENV
    }


# =========================
# 🔹 Register Routers
# =========================
app.include_router(health_router, prefix="")
app.include_router(workflow_router, prefix="/workflow")
app.include_router(agents_router, prefix="/agents")

# =========================
# 🔹 Startup Event
# =========================


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Application startup complete")
    logger.info(f"Environment: {settings.ENV}")

# =========================
# 🔹 Shutdown Event
# =========================


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Application shutdown initiated")
