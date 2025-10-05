from fastapi import APIRouter, HTTPException
from services.database import DatabaseService
from services.earth_engine import earth_engine_service
from typing import List, Dict
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["Forests"])

@router.get("/forests", response_model=List[Dict])
@router.get("/forests", response_model=List[Dict])

@router.get("/forests", response_model=List[Dict])
def get_all_forests():
    """
    Obtener todos los bosques con salud en tiempo real desde NASA
    """
    # Obtener todos los bosques de la BD
    forests = DatabaseService.get_all_forests()
    if not forests:
        raise HTTPException(status_code=404, detail="No forests found")
    
    # Agregar health_nasa a cada bosque
    for forest in forests:
        try:
            # Obtener NDVI real desde NASA
            health_data = earth_engine_service.get_forest_ndvi(
                lat=forest['latitude'],
                lon=forest['longitude']
            )
            
            forest['health_nasa'] = {
                "ndvi_value": health_data['ndvi_value'],
                "health_percentage": health_data['health_percentage'],
                "status": health_data['status'],
                "color": health_data['color'],
                "source": health_data['source'],
                "is_real_data": health_data['is_real_data'],
                "last_update": health_data['last_update']
            }
            
        except Exception as e:
            print(f"⚠️ Error obteniendo salud NASA para bosque {forest.get('id')}: {str(e)}")
            forest['health_nasa'] = {
                "ndvi_value": None,
                "health_percentage": forest.get('health', 50),
                "status": "NASA data not available",
                "color": "#6b7280",
                "source": "Local database",
                "is_real_data": False,
                "last_update": datetime.utcnow().isoformat()
            }
    
    return forests

@router.get("/forests/{forest_id}", response_model=Dict)
def get_forest_by_id(forest_id: str):
    """
    Obtener un bosque específico con salud en tiempo real desde NASA
    
    Combina:
    - Información básica del bosque (Supabase)
    - Salud actual NDVI (Google Earth Engine - NASA MODIS)
    """
    # Obtener datos básicos del bosque
    forest = DatabaseService.get_forest_by_id(forest_id)
    if not forest:
        raise HTTPException(status_code=404, detail=f"Forest {forest_id} not found")
    
    # Obtener salud en tiempo real desde NASA
    try:
        health_data = earth_engine_service.get_forest_ndvi(
            lat=forest['latitude'],
            lon=forest['longitude']
        )
        
        # Combinar datos básicos + salud NASA
        forest_complete = {
            **forest,  # Todos los datos básicos (id, name, co2_capture, etc.)
            "health_nasa": {
                "ndvi_value": health_data['ndvi_value'],
                "health_percentage": health_data['health_percentage'],
                "status": health_data['status'],
                "color": health_data['color'],
                "source": health_data['source'],
                "is_real_data": health_data['is_real_data'],
                "last_update": health_data['last_update']
            }
        }
        
        return forest_complete
        
    except Exception as e:
        # Si falla GEE, devolver solo datos básicos
        print(f"⚠️ Error obteniendo salud NASA: {str(e)}")
        forest['health_nasa'] = {
            "ndvi_value": None,
            "health_percentage": forest.get('health', 50),  # Fallback al valor BD
            "status": "NASA data not available",
            "color": "#6b7280",
            "source": "Local database",
            "is_real_data": False,
            "last_update": datetime.utcnow().isoformat()
        }
        return forest