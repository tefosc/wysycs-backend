from fastapi import APIRouter, HTTPException, Query
from services.earth_engine import earth_engine_service
from services.database import DatabaseService

router = APIRouter(prefix="/api/v1", tags=["Forest Health"])

@router.get("/forest/{forest_id}/health")
def get_forest_health(forest_id: str):
    """
    Obtener salud actual del bosque usando NDVI de NASA MODIS
    
    Returns:
        - ndvi_value: Valor NDVI (-1 a 1)
        - health_percentage: Porcentaje de salud (0-100)
        - status: Estado (Saludable, En riesgo, Deteriorado, Crítico)
        - color: Color hex para UI
        - source: Fuente de datos
        - is_real_data: Si son datos reales de NASA o estimación
    """
    try:
        # Obtener bosque de la base de datos
        forest = DatabaseService.get_forest_by_id(forest_id)
        
        if not forest:
            raise HTTPException(status_code=404, detail="Bosque no encontrado")
        
        # Obtener NDVI desde Google Earth Engine
        health_data = earth_engine_service.get_forest_ndvi(
            lat=forest['latitude'],
            lon=forest['longitude']
        )
        
        return {
            "forest_id": forest_id,
            "forest_name": forest['name'],
            "location": {
                "latitude": forest['latitude'],
                "longitude": forest['longitude']
            },
            **health_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forest/{forest_id}/history")
def get_forest_history(
    forest_id: str,
    months: int = Query(default=12, ge=1, le=24, description="Meses hacia atrás (1-24)")
):
    """
    Obtener histórico de NDVI del bosque
    
    Args:
        forest_id: ID del bosque
        months: Meses hacia atrás (1-24)
    
    Returns:
        Lista de valores NDVI históricos con fechas
    """
    try:
        # Obtener bosque
        forest = DatabaseService.get_forest_by_id(forest_id)
        
        if not forest:
            raise HTTPException(status_code=404, detail="Bosque no encontrado")
        
        # Obtener histórico
        history = earth_engine_service.get_ndvi_history(
            lat=forest['latitude'],
            lon=forest['longitude'],
            months=months
        )
        
        return {
            "forest_id": forest_id,
            "forest_name": forest['name'],
            "months_requested": months,
            "data_points": len(history),
            "history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/analyze/point")
def analyze_point(
    lat: float = Query(..., ge=-90, le=90, description="Latitud (-90 a 90)"),
    lon: float = Query(..., ge=-180, le=180, description="Longitud (-180 a 180)")
):
    """
    Analizar salud de vegetación en cualquier punto del mapa
    
    Args:
        lat: Latitud del punto
        lon: Longitud del punto
    
    Returns:
        Datos NDVI y salud del punto seleccionado
    """
    try:
        # Obtener NDVI del punto
        health_data = earth_engine_service.get_forest_ndvi(lat=lat, lon=lon)
        
        return {
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "analysis": health_data,
            "message": "Análisis de punto personalizado"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/point/history")
def analyze_point_history(
    lat: float = Query(..., ge=-90, le=90, description="Latitud"),
    lon: float = Query(..., ge=-180, le=180, description="Longitud"),
    months: int = Query(default=12, ge=1, le=24, description="Meses hacia atrás")
):
    """
    Obtener histórico NDVI de cualquier punto del mapa
    
    Args:
        lat: Latitud
        lon: Longitud
        months: Meses hacia atrás (1-24)
    
    Returns:
        Serie temporal de NDVI del punto
    """
    try:
        # Obtener histórico
        history = earth_engine_service.get_ndvi_history(
            lat=lat,
            lon=lon,
            months=months
        )
        
        return {
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "months_requested": months,
            "data_points": len(history),
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))