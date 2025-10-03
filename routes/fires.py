from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict
from services.nasa_firms import nasa_firms_service
from services.database import supabase

router = APIRouter(prefix="/api/v1/fires", tags=["Fires"])

@router.get("/peru")
async def get_fires_peru(
    days: int = Query(default=1, ge=1, le=10, description="Días hacia atrás (1-10)")
) -> Dict:
    """
    Obtiene todos los incendios activos en Perú
    
    - **days**: Número de días hacia atrás (máximo 10)
    
    Retorna lista de incendios con coordenadas, brillo, confianza, etc.
    """
    fires = nasa_firms_service.get_fires_peru(days)
    
    return {
        "success": True,
        "count": len(fires),
        "days_queried": days,
        "source": "NASA FIRMS - VIIRS",
        "fires": fires
    }

@router.get("/forest/{forest_id}")
async def get_fires_near_forest(
    forest_id: str,
    radius_km: float = Query(default=20, ge=1, le=100, description="Radio de búsqueda en km"),
    days: int = Query(default=1, ge=1, le=10, description="Días hacia atrás")
) -> Dict:
    """
    Obtiene incendios cerca de un bosque específico
    
    - **forest_id**: ID del bosque
    - **radius_km**: Radio de búsqueda en kilómetros (1-100)
    - **days**: Días hacia atrás (1-10)
    
    Retorna incendios dentro del radio especificado ordenados por distancia.
    """
    
    # Obtener datos del bosque desde Supabase
    result = supabase.table('forests').select('*').eq('id', forest_id).execute()
    
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail=f"Bosque con ID {forest_id} no encontrado")
    
    forest = result.data[0]
    
    # Obtener incendios cercanos
    nearby_fires = nasa_firms_service.get_fires_near_location(
        latitude=forest['latitude'],
        longitude=forest['longitude'],
        radius_km=radius_km,
        days=days
    )
    
    # Calcular nivel de riesgo
    risk_level = "BAJO"
    if len(nearby_fires) > 0:
        closest_distance = nearby_fires[0]['distance_km']
        if closest_distance < 5:
            risk_level = "CRÍTICO"
        elif closest_distance < 10:
            risk_level = "ALTO"
        elif closest_distance < 20:
            risk_level = "MODERADO"
    
    return {
        "success": True,
        "forest": {
            "id": forest['id'],
            "name": forest['name'],
            "latitude": forest['latitude'],
            "longitude": forest['longitude']
        },
        "search_parameters": {
            "radius_km": radius_km,
            "days_queried": days
        },
        "risk_assessment": {
            "level": risk_level,
            "fires_detected": len(nearby_fires),
            "closest_fire_km": nearby_fires[0]['distance_km'] if nearby_fires else None
        },
        "fires": nearby_fires
    }

@router.get("/stats")
async def get_fire_statistics(days: int = Query(default=7, ge=1, le=30)) -> Dict:
    """
    Obtiene estadísticas generales de incendios en Perú
    
    - **days**: Período de análisis en días
    
    Retorna resumen estadístico de incendios.
    """
    fires = nasa_firms_service.get_fires_peru(days)
    
    if not fires:
        return {
            "success": True,
            "period_days": days,
            "total_fires": 0,
            "message": "No se detectaron incendios en el período"
        }
    
    # Calcular estadísticas
    total_fires = len(fires)
    high_confidence = len([f for f in fires if f['confidence'] in ['high', 'h']])
    avg_brightness = sum(f['brightness'] for f in fires) / total_fires
    
    # Incendios por día
    fires_by_date = {}
    for fire in fires:
        date = fire['acq_date']
        fires_by_date[date] = fires_by_date.get(date, 0) + 1
    
    return {
        "success": True,
        "period_days": days,
        "total_fires": total_fires,
        "high_confidence_fires": high_confidence,
        "average_brightness": round(avg_brightness, 2),
        "fires_by_date": fires_by_date,
        "source": "NASA FIRMS - VIIRS"
    }

@router.get("/analyze")
async def analyze_location(
    lat: float = Query(..., ge=-90, le=90, description="Latitud"),
    lon: float = Query(..., ge=-180, le=180, description="Longitud"),
    radius_km: float = Query(default=20, ge=1, le=100, description="Radio de búsqueda en km"),
    days: int = Query(default=1, ge=1, le=10, description="Días hacia atrás")
) -> Dict:
    """
    Analiza incendios en cualquier punto del mapa (sin necesidad de adopción)
    
    - **lat**: Latitud del punto (-90 a 90)
    - **lon**: Longitud del punto (-180 a 180)
    - **radius_km**: Radio de búsqueda en kilómetros (1-100)
    - **days**: Días hacia atrás (1-10)
    
    Perfecto para exploración libre en el mapa.
    """
    
    # Obtener incendios cercanos a las coordenadas
    nearby_fires = nasa_firms_service.get_fires_near_location(
        latitude=lat,
        longitude=lon,
        radius_km=radius_km,
        days=days
    )
    
    # Calcular nivel de riesgo
    risk_level = "BAJO"
    risk_color = "#10b981"  # Verde
    risk_description = "No se detectaron incendios en el área"
    
    if len(nearby_fires) > 0:
        closest_distance = nearby_fires[0]['distance_km']
        
        if closest_distance < 5:
            risk_level = "CRÍTICO"
            risk_color = "#ef4444"  # Rojo
            risk_description = f"¡PELIGRO! Incendio a solo {closest_distance}km"
        elif closest_distance < 10:
            risk_level = "ALTO"
            risk_color = "#f97316"  # Naranja
            risk_description = f"Riesgo alto. Incendio cercano a {closest_distance}km"
        elif closest_distance < 20:
            risk_level = "MODERADO"
            risk_color = "#fbbf24"  # Amarillo
            risk_description = f"Vigilar. Incendio detectado a {closest_distance}km"
        else:
            risk_level = "BAJO"
            risk_color = "#10b981"  # Verde
            risk_description = f"Incendio lejano ({closest_distance}km). Área segura"
    
    # Estadísticas adicionales
    high_confidence_fires = len([f for f in nearby_fires if f['confidence'] in ['high', 'h']])
    
    return {
        "success": True,
        "location": {
            "latitude": lat,
            "longitude": lon,
            "description": "Punto de análisis seleccionado"
        },
        "search_parameters": {
            "radius_km": radius_km,
            "days_queried": days
        },
        "risk_assessment": {
            "level": risk_level,
            "color": risk_color,
            "description": risk_description,
            "fires_detected": len(nearby_fires),
            "high_confidence_fires": high_confidence_fires,
            "closest_fire_km": nearby_fires[0]['distance_km'] if nearby_fires else None
        },
        "fires": nearby_fires,
        "recommendations": _generate_recommendations(risk_level, len(nearby_fires))
    }

def _generate_recommendations(risk_level: str, fire_count: int) -> List[str]:
    """Genera recomendaciones según el nivel de riesgo"""
    
    if risk_level == "CRÍTICO":
        return [
            "🚨 Alertar a autoridades locales inmediatamente",
            "👥 Preparar evacuación preventiva de comunidades",
            "💧 Verificar acceso a fuentes de agua",
            "📞 Contactar con bomberos y defensa civil"
        ]
    elif risk_level == "ALTO":
        return [
            "⚠️ Monitorear constantemente la situación",
            "👨‍🚒 Informar a brigadas contra incendios",
            "🎒 Preparar kit de emergencia",
            "📡 Mantener comunicación con autoridades"
        ]
    elif risk_level == "MODERADO":
        return [
            "👀 Vigilar evolución de los incendios",
            "🌳 Evitar actividades que puedan generar chispas",
            "💧 Identificar fuentes de agua cercanas",
            "📱 Adoptar este bosque para recibir alertas automáticas"
        ]
    else:  # BAJO
        return [
            "✅ Área actualmente segura",
            "🌳 Considera adoptar este bosque para monitoreo continuo",
            "📊 Revisar predicciones de riesgo futuro",
            "🤝 Unirte a la comunidad de guardianes"
        ]