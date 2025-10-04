import ee
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class EarthEngineService:
    def __init__(self):
        """Inicializar Earth Engine con service account"""
        try:
            # Intentar cargar desde variable de entorno primero (Railway)
            gee_json = os.getenv('GEE_SERVICE_ACCOUNT_JSON')
            
            if gee_json:
                # Producción: Leer de variable de entorno
                credentials_info = json.loads(gee_json)
            else:
                # Local: Leer desde archivo
                credentials_path = 'credentials/gee-service-account.json'
                with open(credentials_path, 'r') as f:
                    credentials_info = json.load(f)
            
            credentials = ee.ServiceAccountCredentials(
                email=credentials_info['client_email'],
                key_data=credentials_info['private_key']
            )
            
            ee.Initialize(credentials)
            self.initialized = True
            print("✅ Earth Engine inicializado correctamente")
            
        except Exception as e:
            print(f"⚠️ Error inicializando Earth Engine: {e}")
            self.initialized = False
    
    def get_forest_ndvi(self, lat: float, lon: float) -> Dict:
        """
        Obtener NDVI actual de un bosque
        
        Args:
            lat: Latitud del bosque
            lon: Longitud del bosque
        
        Returns:
            Dict con NDVI y estado de salud
        """
        if not self.initialized:
            return self._get_fallback_health(lat, lon)
        
        try:
            # Punto de interés
            point = ee.Geometry.Point([lon, lat])
            
            # Obtener imagen MODIS más reciente (últimos 30 días)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            modis = ee.ImageCollection('MODIS/061/MOD13Q1') \
                .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
                .filterBounds(point) \
                .select('NDVI') \
                .first()
            
            # Obtener valor NDVI en el punto
            ndvi_raw = modis.sample(point, 250).first().get('NDVI').getInfo()
            
            # MODIS NDVI viene en escala -2000 a 10000, convertir a -1 a 1
            ndvi_value = ndvi_raw / 10000.0
            
            # Calcular porcentaje de salud (0-100)
            # NDVI > 0.6 = Excelente (100%)
            # NDVI 0.4-0.6 = Bueno (70-90%)
            # NDVI 0.2-0.4 = Regular (40-70%)
            # NDVI < 0.2 = Crítico (0-40%)
            
            if ndvi_value > 0.6:
                health_percentage = int(90 + (ndvi_value - 0.6) * 25)
            elif ndvi_value > 0.4:
                health_percentage = int(70 + (ndvi_value - 0.4) * 100)
            elif ndvi_value > 0.2:
                health_percentage = int(40 + (ndvi_value - 0.2) * 150)
            else:
                health_percentage = int(max(0, ndvi_value * 200))
            
            # Determinar estado y color
            if health_percentage >= 70:
                status = "Saludable"
                color = "#10b981"  # Verde
            elif health_percentage >= 50:
                status = "En riesgo"
                color = "#f59e0b"  # Amarillo
            elif health_percentage >= 30:
                status = "Deteriorado"
                color = "#f97316"  # Naranja
            else:
                status = "Crítico"
                color = "#ef4444"  # Rojo
            
            return {
                "ndvi_value": round(ndvi_value, 3),
                "health_percentage": health_percentage,
                "status": status,
                "color": color,
                "source": "MODIS/061/MOD13Q1 (NASA)",
                "is_real_data": True,
                "last_update": end_date.isoformat()
            }
            
        except Exception as e:
            print(f"Error obteniendo NDVI: {e}")
            return self._get_fallback_health(lat, lon)
    
    def _get_fallback_health(self, lat: float, lon: float) -> Dict:
        """Estimación de salud cuando GEE no está disponible"""
        # Estimación basada en ubicación (bosques amazónicos suelen tener NDVI alto)
        if -10 < lat < -2 and -80 < lon < -70:  # Amazonía peruana
            base_health = 65
        else:
            base_health = 55
        
        # Agregar variación basada en coordenadas
        variation = int((lat + lon) * 10) % 20
        health = base_health + variation
        
        if health >= 70:
            status = "Saludable"
            color = "#10b981"
        elif health >= 50:
            status = "En riesgo"
            color = "#f59e0b"
        else:
            status = "Deteriorado"
            color = "#f97316"
        
        return {
            "ndvi_value": round(health / 100.0, 3),
            "health_percentage": health,
            "status": status,
            "color": color,
            "source": "Estimación (GEE no disponible)",
            "is_real_data": False,
            "last_update": datetime.now().isoformat()
        }
    
    def get_ndvi_history(self, lat: float, lon: float, months: int = 12) -> List[Dict]:
        """
        Obtener histórico de NDVI
        
        Args:
            lat: Latitud
            lon: Longitud
            months: Meses hacia atrás (default 12)
        
        Returns:
            Lista de valores NDVI históricos
        """
        if not self.initialized:
            return self._get_fallback_history(months)
        
        try:
            point = ee.Geometry.Point([lon, lat])
            
            # Calcular fechas
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            # Obtener colección MODIS
            modis = ee.ImageCollection('MODIS/061/MOD13Q1') \
                .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
                .filterBounds(point) \
                .select('NDVI')
            
            # Extraer valores
            def extract_ndvi(image):
                date = ee.Date(image.get('system:time_start'))
                ndvi = image.sample(point, 250).first().get('NDVI')
                return ee.Feature(None, {
                    'date': date.format('YYYY-MM-dd'),
                    'ndvi': ee.Number(ndvi).divide(10000)
                })
            
            features = modis.map(extract_ndvi).getInfo()
            
            history = []
            for feature in features['features']:
                props = feature['properties']
                ndvi_val = props['ndvi']
                health = int(min(100, max(0, ndvi_val * 150)))
                
                history.append({
                    'date': props['date'],
                    'ndvi': round(ndvi_val, 3),
                    'health': health
                })
            
            return sorted(history, key=lambda x: x['date'])
            
        except Exception as e:
            print(f"Error obteniendo histórico: {e}")
            return self._get_fallback_history(months)
    
    def _get_fallback_history(self, months: int) -> List[Dict]:
        """Histórico simulado cuando GEE no disponible"""
        history = []
        base_ndvi = 0.65
        
        for i in range(months):
            date = datetime.now() - timedelta(days=(months - i) * 30)
            # Simular variación estacional
            variation = 0.1 * (i % 4 - 2) / 2
            ndvi = base_ndvi + variation
            health = int(min(100, max(0, ndvi * 150)))
            
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'ndvi': round(ndvi, 3),
                'health': health
            })
        
        return history


# Instancia global
earth_engine_service = EarthEngineService()