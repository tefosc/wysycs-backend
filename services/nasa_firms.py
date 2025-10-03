import requests
from typing import List, Dict
from config.settings import get_settings

settings = get_settings()

class NASAFIRMSService:
    """Servicio para obtener datos de incendios de NASA FIRMS API"""
    
    def __init__(self):
        self.api_key = settings.nasa_firms_api_key
        self.base_url = "https://firms.modaps.eosdis.nasa.gov/api"
    
    def get_fires_peru(self, days: int = 1) -> List[Dict]:
        """
        Obtiene incendios activos en Perú usando MODIS
        
        Args:
            days: Número de días hacia atrás (1-10)
        
        Returns:
            Lista de incendios
        """
        try:
            # Coordenadas de Perú: oeste, sur, este, norte
            peru_bounds = "-81.3,-18.3,-68.7,-0.0"
            
            url = f"{self.base_url}/area/csv/{self.api_key}/MODIS_NRT/{peru_bounds}/{days}"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Procesar CSV
            lines = response.text.strip().split('\n')
            
            if len(lines) < 2:
                return []
            
            fires = []
            for line in lines[1:]:  # Saltar header
                if not line.strip():
                    continue
                
                try:
                    values = line.split(',')
                    
                    fire = {
                        'latitude': float(values[0]),
                        'longitude': float(values[1]),
                        'brightness': float(values[2]),
                        'scan': float(values[3]),
                        'track': float(values[4]),
                        'acq_date': values[5],
                        'acq_time': values[6],
                        'satellite': values[7],
                        'instrument': values[8],
                        'confidence': values[9],
                        'version': values[10],
                        'bright_t31': float(values[11]),
                        'frp': float(values[12]),
                        'daynight': values[13]
                    }
                    
                    fires.append(fire)
                except (ValueError, IndexError) as e:
                    continue
            
            return fires
            
        except Exception as e:
            print(f"Error al obtener incendios: {str(e)}")
            return []
    
    def get_fires_near_location(
        self, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 20,
        days: int = 1
    ) -> List[Dict]:
        """
        Obtiene incendios cerca de una ubicación específica
        """
        all_fires = self.get_fires_peru(days)
        
        nearby_fires = []
        
        for fire in all_fires:
            distance = self._calculate_distance(
                latitude, 
                longitude,
                fire['latitude'],
                fire['longitude']
            )
            
            if distance <= radius_km:
                fire['distance_km'] = round(distance, 2)
                nearby_fires.append(fire)
        
        nearby_fires.sort(key=lambda x: x['distance_km'])
        
        return nearby_fires
    
    def _calculate_distance(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calcula distancia entre dos puntos usando fórmula Haversine
        """
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        r = 6371
        
        return c * r

nasa_firms_service = NASAFIRMSService()