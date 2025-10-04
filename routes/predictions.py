from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from services.predictor import predictor_service
from services.earth_engine import earth_engine_service
from services.database import DatabaseService

router = APIRouter(prefix="/api/v1", tags=["Predictions"])

@router.get("/forest/{forest_id}/prediction")
def predict_forest_future(
    forest_id: str,
    days_ahead: int = Query(default=90, ge=1, le=365, description="Días a predecir (1-365)")
):
    """
    Predecir salud futura del bosque usando Machine Learning (Prophet)
    
    Args:
        forest_id: ID del bosque
        days_ahead: Días hacia adelante para predecir
    
    Returns:
        Predicciones con tendencia y evaluación de riesgo
    """
    try:
        # Obtener bosque
        forest = DatabaseService.get_forest_by_id(forest_id)
        if not forest:
            raise HTTPException(status_code=404, detail="Bosque no encontrado")
        
        # Obtener datos históricos
        historical = earth_engine_service.get_ndvi_history(
            lat=forest['latitude'],
            lon=forest['longitude'],
            months=12
        )
        
        if len(historical) < 3:
            raise HTTPException(
                status_code=400, 
                detail="Datos históricos insuficientes para predicción"
            )
        
        # Generar predicción
        prediction = predictor_service.predict_forest_health(
            historical_data=historical,
            days_ahead=days_ahead
        )
        
        return {
            'forest_id': forest_id,
            'forest_name': forest['name'],
            'days_ahead': days_ahead,
            **prediction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/point/prediction")
def predict_point_future(
    lat: float = Query(..., ge=-90, le=90, description="Latitud"),
    lon: float = Query(..., ge=-180, le=180, description="Longitud"),
    days_ahead: int = Query(default=90, ge=1, le=365, description="Días a predecir")
):
    """
    Predecir salud futura de cualquier punto del mapa
    
    Args:
        lat: Latitud
        lon: Longitud
        days_ahead: Días hacia adelante
    
    Returns:
        Predicciones ML del punto seleccionado
    """
    try:
        # Obtener histórico
        historical = earth_engine_service.get_ndvi_history(
            lat=lat,
            lon=lon,
            months=12
        )
        
        if len(historical) < 3:
            raise HTTPException(
                status_code=400,
                detail="Datos históricos insuficientes para predicción"
            )
        
        # Predicción
        prediction = predictor_service.predict_forest_health(
            historical_data=historical,
            days_ahead=days_ahead
        )
        
        return {
            'location': {'latitude': lat, 'longitude': lon},
            'days_ahead': days_ahead,
            **prediction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FireImpactRequest(BaseModel):
    fire_area_ha: float
    scenarios: List[int] = [1, 2, 7]

@router.post("/simulate-impact")
def simulate_fire_impact(request: FireImpactRequest):
    """
    Simular impacto de incendio en diferentes escenarios temporales
    
    Body:
        - fire_area_ha: Área actual del incendio en hectáreas
        - scenarios: Lista de días para simular (ej: [1, 2, 7])
    
    Returns:
        Simulaciones de impacto ambiental, social y recomendaciones
    """
    try:
        if request.fire_area_ha <= 0:
            raise HTTPException(
                status_code=400,
                detail="El área del incendio debe ser mayor a 0"
            )
        
        simulation = predictor_service.simulate_fire_impact(
            fire_area_ha=request.fire_area_ha,
            scenarios=request.scenarios
        )
        
        return {
            'initial_fire_area_ha': request.fire_area_ha,
            **simulation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))