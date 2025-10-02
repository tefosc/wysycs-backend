from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from services.database import DatabaseService
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
        
        return {
            "success": True,
            "message": "¡Bosque adoptado exitosamente!",
            "adoption_id": adoption['id']
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
            "total_forests": 0
        }
    
    return {
        "guardian_email": email,
        "guardian_name": forests[0]['guardian_name'],
        "adopted_forests": forests,
        "total_forests": len(forests)
    }