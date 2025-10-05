from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from services.database import DatabaseService, supabase
from services.notifier import notification_service
from typing import Optional
from services.earth_engine import earth_engine_service

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
        # ✅ VALIDACIÓN: Verificar si ya adoptó este bosque
        existing_adoption = supabase.table('adopted_forests') \
            .select('id') \
            .eq('forest_id', request.forest_id) \
            .eq('guardian_email', request.guardian_email) \
            .eq('is_active', True) \
            .execute()
        
        if existing_adoption.data:
            raise HTTPException(
                status_code=400, 
                detail=f"You have already adopted this forest"
            )
        
        # Proceder con la adopción
        adoption = DatabaseService.adopt_forest(
            forest_id=request.forest_id,
            guardian_name=request.guardian_name,
            guardian_email=request.guardian_email,
            telegram_chat_id=request.telegram_chat_id
        )
        
        # Asignar puntos iniciales por adopción
        initial_points = 10
        new_level = "Seedling"
        
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
            "message": "Forest adopted successfully!",
            "adoption_id": adoption['id'],
            "email_sent": True,
            "points_earned": initial_points,
            "guardian_level": new_level
        }   
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise  # Re-lanzar HTTPException para que FastAPI la maneje
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/guardian/{email}")
def get_guardian_info(email: str):
    """Info del guardián con salud NASA de bosques adoptados"""
    forests = DatabaseService.get_guardian_forests(email)
    
    if not forests:
        return {
            "guardian_email": email,
            "adopted_forests": [],
            "total_forests": 0,
            "total_points": 0,
            "guardian_level": "Seedling"
        }
    
    # Agregar salud NASA a cada bosque adoptado
    forests_with_nasa = []
    for forest in forests:
        try:
            # ✅ FIX: Acceder a lat/lon desde el objeto 'forests' anidado
            forest_data = forest.get('forests', {})
            lat = forest_data.get('latitude')
            lon = forest_data.get('longitude')
            
            if lat is None or lon is None:
                raise ValueError("Missing coordinates")
            
            # Obtener salud NASA en tiempo real
            health_data = earth_engine_service.get_forest_ndvi(lat=lat, lon=lon)
            
            # Agregar health_nasa al bosque
            forest['health_nasa'] = {
                'ndvi_value': health_data['ndvi_value'],
                'health_percentage': health_data['health_percentage'],
                'status': health_data['status'],
                'color': health_data['color'],
                'is_real_data': health_data['is_real_data'],
                'last_update': health_data['last_update']
            }
        except Exception as e:
            print(f"⚠️ Error obteniendo salud NASA para bosque {forest.get('forest_id')}: {e}")
            # Fallback si falla GEE
            forest['health_nasa'] = {
                'ndvi_value': None,
                'health_percentage': forest_data.get('health', 50),
                'status': 'Data not available',
                'color': '#6b7280',
                'is_real_data': False
            }
        
        forests_with_nasa.append(forest)
    
    # Calcular puntos totales
    total_points = sum([f.get('points', 0) for f in forests_with_nasa])
    
    return {
        "guardian_email": email,
        "guardian_name": forests_with_nasa[0]['guardian_name'],
        "adopted_forests": forests_with_nasa,
        "total_forests": len(forests_with_nasa),
        "total_points": total_points,
        "guardian_level": forests_with_nasa[0].get('guardian_level', 'Seedling')
    }