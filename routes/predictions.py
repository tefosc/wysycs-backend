from fastapi import APIRouter, Query
from typing import Optional
import random

router = APIRouter()

def get_weather_params_by_location(latitude: float, longitude: float):
    """
    Retorna parámetros climáticos aproximados según la zona geográfica de Perú
    """
    
    # Amazonía (húmedo, viento suave)
    if longitude < -73 and latitude > -10 and latitude < -2:
        return {
            'wind_speed': round(8 + random.uniform(0, 4), 1),  # 8-12 km/h
            'humidity': round(65 + random.uniform(0, 15)),     # 65-80%
            'wind_direction': round(90 + random.uniform(0, 45)), # Este-Sureste
            'region': 'Amazonía'
        }
    
    # Costa norte (seco, viento fuerte)
    elif longitude > -81 and longitude < -79 and latitude > -8:
        return {
            'wind_speed': round(20 + random.uniform(0, 10), 1), # 20-30 km/h
            'humidity': round(15 + random.uniform(0, 15)),      # 15-30%
            'wind_direction': round(180 + random.uniform(0, 30)), # Sur
            'region': 'Costa Norte'
        }
    
    # Costa sur (muy seco, viento moderado)
    elif longitude > -77 and latitude < -12:
        return {
            'wind_speed': round(15 + random.uniform(0, 8), 1),  # 15-23 km/h
            'humidity': round(10 + random.uniform(0, 20)),      # 10-30%
            'wind_direction': round(200 + random.uniform(0, 40)), # Sur-Suroeste
            'region': 'Costa Sur'
        }
    
    # Sierra (seco, viento variable)
    elif longitude > -78 and longitude < -73 and latitude > -12 and latitude < -6:
        return {
            'wind_speed': round(12 + random.uniform(0, 10), 1), # 12-22 km/h
            'humidity': round(30 + random.uniform(0, 25)),      # 30-55%
            'wind_direction': round(random.uniform(0, 360)),    # Variable
            'region': 'Sierra'
        }
    
    # Selva central (húmedo, viento leve)
    elif longitude < -75 and latitude > -12 and latitude < -8:
        return {
            'wind_speed': round(6 + random.uniform(0, 6), 1),   # 6-12 km/h
            'humidity': round(70 + random.uniform(0, 15)),      # 70-85%
            'wind_direction': round(45 + random.uniform(0, 90)), # Noreste-Este
            'region': 'Selva Central'
        }
    
    # Default (condiciones promedio)
    else:
        return {
            'wind_speed': round(12 + random.uniform(0, 8), 1),  # 12-20 km/h
            'humidity': round(40 + random.uniform(0, 30)),      # 40-70%
            'wind_direction': round(random.uniform(0, 360)),    # Variable
            'region': 'Zona mixta'
        }


@router.get("/fire/predict-spread")
async def predict_fire_spread(
    latitude: float = Query(..., description="Latitud del incendio"),
    longitude: float = Query(..., description="Longitud del incendio"),
    days_ahead: int = Query(3, ge=1, le=7, description="Días a predecir"),
    wind_speed: Optional[float] = Query(None, description="Velocidad del viento (km/h) - opcional"),
    humidity: Optional[float] = Query(None, description="Humedad (%) - opcional"),
    wind_direction: Optional[float] = Query(None, description="Dirección del viento (grados) - opcional")
):
    """
    Predice la propagación de un incendio usando modelo físico.
    Si no se proporcionan parámetros climáticos, se usan valores aproximados según la ubicación.
    """
    
    # Si no se proporcionan parámetros, usar datos según ubicación
    if wind_speed is None or humidity is None or wind_direction is None:
        weather_params = get_weather_params_by_location(latitude, longitude)
        wind_speed = weather_params['wind_speed']
        humidity = weather_params['humidity']
        wind_direction = weather_params['wind_direction']
        using_location_data = True
        region = weather_params['region']
    else:
        using_location_data = False
        region = None
    
    from datetime import datetime, timedelta
    import math
    
    predictions = []
    current_lat = latitude
    current_lon = longitude
    
    for day in range(1, days_ahead + 1):
        # Velocidad de propagación base (km/h)
        base_speed = 0.5
        
        # Factores de ajuste
        wind_factor = 1 + (wind_speed / 50)
        humidity_factor = max(0.3, 1 - (humidity / 150))
        vegetation_factor = 1.2  # Amazonía alta densidad
        
        # Velocidad final
        spread_speed = base_speed * wind_factor * humidity_factor * vegetation_factor
        
        # Distancia recorrida en 24 horas
        distance_km = spread_speed * 24
        
        # Nueva posición (simplificado, asume dirección del viento)
        wind_rad = math.radians(wind_direction)
        delta_lat = (distance_km / 111) * math.cos(wind_rad)
        delta_lon = (distance_km / (111 * math.cos(math.radians(current_lat)))) * math.sin(wind_rad)
        
        current_lat += delta_lat
        current_lon += delta_lon
        
        # Radio de propagación acumulado
        spread_radius_km = distance_km * day
        
        # Área afectada (circular)
        affected_area_ha = math.pi * (spread_radius_km ** 2) * 100
        
        # Impacto ambiental
        co2_tonnes = affected_area_ha * 120
        cars_equivalent = co2_tonnes / 4.6
        species_at_risk = int(affected_area_ha * 0.5)
        water_sources = max(1, int(spread_radius_km / 3))
        
        # Impacto poblacional (densidad Amazonía: ~5 personas/km²)
        area_km2 = math.pi * (spread_radius_km ** 2)
        people_at_risk = int(area_km2 * 5)
        indirect_impact = people_at_risk * 3
        families_affected = int(people_at_risk / 4.5)
        
        severity = "BAJA" if people_at_risk < 100 else "MODERADA" if people_at_risk < 500 else "ALTA"
        
        predictions.append({
            "day": day,
            "date": (datetime.now() + timedelta(days=day)).isoformat(),
            "fire_front": {
                "latitude": round(current_lat, 5),
                "longitude": round(current_lon, 5)
            },
            "spread_radius_km": round(spread_radius_km, 2),
            "affected_area_ha": round(affected_area_ha, 2),
            "environmental_impact": {
                "co2_tonnes": round(co2_tonnes, 2),
                "cars_equivalent": round(cars_equivalent, 1),
                "species_at_risk": species_at_risk,
                "water_sources_at_risk": water_sources
            },
            "population_impact": {
                "people_at_risk": people_at_risk,
                "indirect_impact": indirect_impact,
                "families_affected": families_affected,
                "severity": severity
            },
            "confidence": "ALTA" if day <= 3 else "MEDIA"
        })
    
    response = {
        "origin": {
            "latitude": latitude,
            "longitude": longitude
        },
        "predictions": predictions,
        "model": "Fire Spread Physical Model v1.0 - Location-based",
        "parameters": {
            "wind_speed_kmh": wind_speed,
            "wind_direction": wind_direction,
            "humidity_percent": humidity,
            "days_predicted": days_ahead,
            "using_location_data": using_location_data
        },
        "total_impact": {
            "max_area_ha": round(predictions[-1]["affected_area_ha"], 2),
            "max_radius_km": round(predictions[-1]["spread_radius_km"], 2)
        }
    }
    
    if using_location_data:
        response["location_info"] = {
            "region": region,
            "estimated_climate": f"Viento {wind_speed}km/h, Humedad {humidity}%, Dirección {wind_direction}°"
        }
    
    return response