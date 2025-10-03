from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from services.notifier import notification_service

router = APIRouter()

class TestEmailRequest(BaseModel):
    email: EmailStr
    guardian_name: str = "Guardián de Prueba"

@router.post("/test-email")
async def test_email(request: TestEmailRequest):
    """Endpoint para probar envío de emails"""
    
    # Enviar email de prueba (adopción)
    success = notification_service.send_adoption_email(
        guardian_name=request.guardian_name,
        guardian_email=request.email,
        forest_name="Bosque de Prueba - Pacaya-Samiria"
    )
    
    if success:
        return {
            "success": True,
            "message": f"Email de prueba enviado a {request.email}",
            "check": "Revisa tu bandeja de entrada"
        }
    else:
        raise HTTPException(status_code=500, detail="Error enviando email")

@router.post("/test-fire-alert")
async def test_fire_alert(request: TestEmailRequest):
    """Endpoint para probar alerta de incendio"""
    
    success = notification_service.send_fire_alert(
        guardian_email=request.email,
        forest_name="Bosque Pacaya-Samiria",
        distance_km=3.5
    )
    
    if success:
        return {
            "success": True,
            "message": f"Alerta de incendio enviada a {request.email}"
        }
    else:
        raise HTTPException(status_code=500, detail="Error enviando alerta")