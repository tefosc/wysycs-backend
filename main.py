from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from routes import forests, adoption
from routes.fires import router as fires_router
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

@app.get("/")
def root():
    return {
        "message": "🌳 WYSYCS API funcionando",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)