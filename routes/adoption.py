from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from services.database import DatabaseService, supabase
from services.notifier import notification_service
from typing import Optional

router = APIRouter(prefix="/api/v1", tags=["Adoption"])

class AdoptionRequest(BaseModel):
    forest_id: str
    guardian_name: str
    guardian_email: EmailStr
    telegram_chat_id: Optional[str] = None

@router.post("/adopt")
def adopt_forest(request: AdoptionRequest):
    """Adoptar un bosque"""
    try:
        adoption = DatabaseService.adopt_forest(
            forest_id=request.forest_id,
            guardian_name=request.guardian_name,
            guardian_email=request.guardian_email,
            telegram_chat_id=request.telegram_chat_id
        )
        
        # Asignar puntos iniciales por adopción
        initial_points = 10
        new_level = "Sembrador"
        
        # Actualizar adopción con puntos
        supabase.table('adopted_forests') \
            .update({
                'points': initial_points,
                'guardian_level': new_level
            }) \
            .eq('id', adoption['id']) \
            .execute()
        
        # Obtener info del bosque para el email
        forest = DatabaseService.get_forest_by_id(request.forest_id)
        
        # Enviar email de confirmación
        try:
            notification_service.send_adoption_email(
                guardian_name=request.guardian_name,
                guardian_email=request.guardian_email,
                forest_name=forest['name']
            )
        except Exception as email_error:
            print(f"Error enviando email: {email_error}")
            # No fallar la adopción si el email falla
        
        return {
            "success": True,
            "message": "¡Bosque adoptado exitosamente!",
            "adoption_id": adoption['id'],
            "email_sent": True,
            "points_earned": initial_points,
            "guardian_level": new_level
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/guardian/{email}")
def get_guardian_info(email: str):
    """Info del guardián"""
    forests = DatabaseService.get_guardian_forests(email)
    
    if not forests:
        return {
            "guardian_email": email,
            "adopted_forests": [],
            "total_forests": 0,
            "total_points": 0,
            "guardian_level": "Sembrador"
        }
    
    # Calcular puntos totales
    total_points = sum([f.get('points', 0) for f in forests])
    
    return {
        "guardian_email": email,
        "guardian_name": forests[0]['guardian_name'],
        "adopted_forests": forests,
        "total_forests": len(forests),
        "total_points": total_points,
        "guardian_level": forests[0].get('guardian_level', 'Sembrador')
    }