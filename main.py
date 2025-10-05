from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from routes import forests, adoption, notifications, health, predictions, gamification
from routes.fires import router as fires_router
from datetime import datetime

import logging

logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(
    title="WYSYCS API",
    description="What You See, You Can Save",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(forests.router)
app.include_router(adoption.router)
app.include_router(fires_router)
app.include_router(notifications.router, prefix="/api/v1", tags=["Notifications"])
app.include_router(health.router)
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
app.include_router(gamification.router)

@app.get("/")
def root():
    return {
        "message": "🌳 WYSYCS API running",
        "version": "1.0.0",
        "endpoints": {
            "forests": "/api/v1/forests",
            "adopt": "/api/v1/adopt",
            "guardian": "/api/v1/guardian/{email}"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/cron/check-fires")
async def cron_check_fires():
    """Endpoint para ejecutar verificación de incendios (llamado por cron externo)"""
    try:
        from tasks.check_fires import check_fires_and_alert
        check_fires_and_alert()
        return {
            "success": True,
            "message": "Fire check completed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)