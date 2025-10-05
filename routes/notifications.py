from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from services.notifier import notification_service

router = APIRouter()

class TestEmailRequest(BaseModel):
    email: EmailStr
    guardian_name: str = "Test Guardian"

@router.post("/test-email")
async def test_email(request: TestEmailRequest):
    """Endpoint para probar envío de emails"""
    
    # Enviar email de prueba (adopción)
    success = notification_service.send_adoption_email(
        guardian_name=request.guardian_name,
        guardian_email=request.email,
        forest_name="Test Forest - Pacaya-Samiria"
    )
    
    if success:
        return {
            "success": True,
            "message": f"Test email sent to {request.email}",
            "check": "Check your inbox"
        }
    else:
        raise HTTPException(status_code=500, detail="Error sending email")

@router.post("/test-fire-alert")
async def test_fire_alert(request: TestEmailRequest):
    """Endpoint para probar alerta de incendio"""
    
    success = notification_service.send_fire_alert(
        guardian_email=request.email,
        forest_name="Pacaya-Samiria Forest",
        distance_km=3.5
    )
    
    if success:
        return {
            "success": True,
            "message": f"Fire alert sent to {request.email}"
        }
    else:
        raise HTTPException(status_code=500, detail="Error sending alert")