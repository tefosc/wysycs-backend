import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math

class FirePropagationPredictor:
    """Predice propagación de incendios basado en factores físicos"""
    
    @staticmethod
    def calculate_spread_distance(wind_speed_kmh: float, humidity_percent: float, 
                                   days: int, vegetation_density: float = 0.7) -> float:
        """
        Calcula distancia de propagación en km
        
        Modelo simplificado basado en:
        - Velocidad del viento (principal factor)
        - Humedad (reduce propagación)
        - Densidad de vegetación (combustible)
        """
        # Factor de viento (km/día base)
        wind_factor = wind_speed_kmh * 0.4
        
        # Factor de humedad (reduce velocidad)
        humidity_factor = 1 - (humidity_percent / 100)
        
        # Factor de vegetación (aumenta velocidad)
        vegetation_factor = 0.5 + (vegetation_density * 0.5)
        
        # Distancia por día
        daily_spread = wind_factor * humidity_factor * vegetation_factor
        
        # Total acumulado (no lineal, se desacelera con el tiempo)
        total_spread = daily_spread * days * (1 - (days * 0.05))
        
        return max(0, total_spread)
    
    @staticmethod
    def predict_fire_path(fire_lat: float, fire_lon: float, 
                          wind_direction_deg: float, spread_distance_km: float) -> Tuple[float, float]:
        """Calcula nueva ubicación del frente de fuego"""
        # Conversión: 1 grado latitud ≈ 111 km
        # 1 grado longitud ≈ 111 km * cos(latitud)
        
        lat_change = (spread_distance_km * math.cos(math.radians(wind_direction_deg))) / 111
        lon_change = (spread_distance_km * math.sin(math.radians(wind_direction_deg))) / (111 * math.cos(math.radians(fire_lat)))
        
        new_lat = fire_lat + lat_change
        new_lon = fire_lon + lon_change
        
        return new_lat, new_lon
    
    @staticmethod
    def estimate_environmental_impact(affected_area_ha: float, forest_density: float = 0.8) -> Dict:
        """Calcula impacto ambiental estimado"""
        # CO2 emisiones (ton/hectárea para bosque amazónico)
        co2_per_ha = 120
        total_co2 = affected_area_ha * co2_per_ha * forest_density
        
        # Equivalente en autos (1 auto = ~4.6 ton CO2/año)
        cars_equivalent = total_co2 / 4.6
        
        # Especies afectadas (estimación: 50 especies/km² en Amazonía)
        species_at_risk = int((affected_area_ha / 100) * 50)
        
        # Agua afectada (ríos/nacientes)
        water_sources_at_risk = int(affected_area_ha / 500)  # 1 fuente cada 500 ha
        
        return {
            'co2_tonnes': round(total_co2, 2),
            'cars_equivalent': round(cars_equivalent, 1),
            'species_at_risk': species_at_risk,
            'water_sources_at_risk': water_sources_at_risk
        }
    
    @staticmethod
    def estimate_population_impact(affected_area_ha: float, region: str = "amazonia") -> Dict:
        """Estima población afectada"""
        # Densidad poblacional por región (personas/km²)
        densities = {
            "amazonia": 5,      # Baja densidad
            "selva_alta": 25,   # Media densidad
            "costa": 50         # Alta densidad
        }
        
        density = densities.get(region, 5)
        affected_area_km2 = affected_area_ha / 100
        
        # Población directamente afectada
        direct_impact = int(affected_area_km2 * density)
        
        # Población indirectamente afectada (3x el área)
        indirect_impact = int(direct_impact * 3)
        
        # Familias (promedio 4.5 personas/familia)
        families_affected = int(direct_impact / 4.5)
        
        return {
            'people_at_risk': direct_impact,
            'indirect_impact': indirect_impact,
            'families_affected': families_affected,
            'severity': 'CRITICAL' if direct_impact > 1000 else 'HIGH' if direct_impact > 500 else 'MODERATE'
        }
    
    @staticmethod
    async def predict_spread(
        fire_lat: float,
        fire_lon: float,
        days_ahead: int = 3,
        wind_speed_kmh: float = 15,
        humidity_percent: float = 30,
        wind_direction_deg: float = 90  # Este (predominante en Amazonía)
    ) -> Dict:
        """Genera predicción completa de propagación"""
        
        predictions = []
        current_lat = fire_lat
        current_lon = fire_lon
        cumulative_area = 0
        
        for day in range(1, days_ahead + 1):
            # Calcular propagación del día
            daily_spread = FirePropagationPredictor.calculate_spread_distance(
                wind_speed_kmh, humidity_percent, 1
            )
            
            # Nueva ubicación del frente
            new_lat, new_lon = FirePropagationPredictor.predict_fire_path(
                current_lat, current_lon, wind_direction_deg, daily_spread
            )
            
            # Área afectada (circular)
            total_spread = FirePropagationPredictor.calculate_spread_distance(
                wind_speed_kmh, humidity_percent, day
            )
            affected_area_ha = math.pi * (total_spread ** 2) * 100
            cumulative_area = affected_area_ha
            
            # Impactos
            env_impact = FirePropagationPredictor.estimate_environmental_impact(affected_area_ha)
            pop_impact = FirePropagationPredictor.estimate_population_impact(affected_area_ha)
            
            predictions.append({
                'day': day,
                'date': (datetime.now() + timedelta(days=day)).isoformat(),
                'fire_front': {
                    'latitude': round(new_lat, 6),
                    'longitude': round(new_lon, 6)
                },
                'spread_radius_km': round(total_spread, 2),
                'affected_area_ha': round(affected_area_ha, 2),
                'environmental_impact': env_impact,
                'population_impact': pop_impact,
                'confidence': 'HIGH' if day <= 2 else 'MEDIUM' if day <= 5 else 'LOW'
            })
            
            # Actualizar posición para siguiente iteración
            current_lat = new_lat
            current_lon = new_lon
        
        return {
            'origin': {
                'latitude': fire_lat,
                'longitude': fire_lon
            },
            'predictions': predictions,
            'model': 'Fire Spread Physical Model v1.0',
            'parameters': {
                'wind_speed_kmh': wind_speed_kmh,
                'wind_direction': wind_direction_deg,
                'humidity_percent': humidity_percent,
                'days_predicted': days_ahead
            },
            'total_impact': {
                'max_area_ha': round(cumulative_area, 2),
                'max_radius_km': round(total_spread, 2)
            }
        }

# Instancia
fire_predictor = FirePropagationPredictor()