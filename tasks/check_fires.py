import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database import supabase
from services.nasa_firms import nasa_firms_service
from services.notifier import notification_service
from math import radians, cos, sin, asin, sqrt

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcular distancia entre dos puntos en km (Haversine)"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return 6371 * c  # Radio de la Tierra en km

def check_fires_and_alert():
    """Verificar incendios y enviar alertas"""
    print(f"\n{'='*60}")
    print(f"🔍 WYSYCS - Verificación de Incendios")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        # 1. Obtener incendios activos de NASA FIRMS
        print("📡 Consultando NASA FIRMS API...")
        fires = nasa_firms_service.get_fires_peru(days=2)
        print(f"✅ {len(fires)} incendios detectados en Perú\n")
        
        if not fires:
            print("ℹ️  No hay incendios activos. Finalizando.\n")
            return
        
        # 2. Obtener bosques adoptados activos
        print("🌳 Consultando bosques adoptados...")
        result = supabase.table('adopted_forests') \
            .select('*, forests(*)') \
            .eq('is_active', True) \
            .execute()
        
        adopted_forests = result.data
        print(f"✅ {len(adopted_forests)} bosques bajo vigilancia\n")
        
        if not adopted_forests:
            print("ℹ️  No hay bosques adoptados. Finalizando.\n")
            return
        
        # 3. Verificar distancias y enviar alertas
        print("🔍 Analizando proximidad de incendios...\n")
        alerts_sent = 0
        
        for adoption in adopted_forests:
            forest = adoption.get('forests')
            if not forest:
                continue
            
            forest_lat = forest['latitude']
            forest_lon = forest['longitude']
            forest_name = forest['name']
            guardian_email = adoption['guardian_email']
            guardian_name = adoption['guardian_name']
            
            # Verificar incendios cercanos (< 20km)
            for fire in fires:
                distance = calculate_distance(
                    forest_lat, forest_lon,
                    fire['latitude'], fire['longitude']
                )
                
                if distance < 20:  # Alerta si está a menos de 20km
                    print(f"⚠️  ALERTA DETECTADA:")
                    print(f"   Bosque: {forest_name}")
                    print(f"   Guardián: {guardian_name} ({guardian_email})")
                    print(f"   Distancia: {distance:.1f} km")
                    print(f"   Confianza: {fire.get('confidence', 'N/A')}")
                    
                    # Verificar si ya enviamos alerta para este bosque hoy
                    today = datetime.now().date()
                    existing_alert = supabase.table('alerts_sent') \
                        .select('*') \
                        .eq('forest_id', adoption['forest_id']) \
                        .eq('guardian_email', guardian_email) \
                        .gte('sent_at', today.isoformat()) \
                        .execute()
                    
                    if existing_alert.data:
                        print(f"   ℹ️  Alerta ya enviada hoy. Omitiendo.\n")
                        continue
                    
                    # Enviar email de alerta
                    try:
                        notification_service.send_fire_alert(
                            guardian_email=guardian_email,
                            forest_name=forest_name,
                            distance_km=distance
                        )
                        
                        # Registrar alerta enviada
                        supabase.table('alerts_sent').insert({
                            'forest_id': adoption['forest_id'],
                            'guardian_email': guardian_email,
                            'alert_type': 'fire',
                            'severity': 'CRÍTICO' if distance < 10 else 'ALTO',
                            'alert_data': {
                                'distance_km': distance,
                                'fire_confidence': fire.get('confidence'),
                                'fire_brightness': fire.get('brightness')
                            }
                        }).execute()
                        
                        alerts_sent += 1
                        print(f"   ✅ Alerta enviada exitosamente\n")
                        
                    except Exception as email_error:
                        print(f"   ❌ Error enviando email: {email_error}\n")
        
        # 4. Resumen final
        print(f"{'='*60}")
        print(f"📊 RESUMEN:")
        print(f"   Incendios detectados: {len(fires)}")
        print(f"   Bosques monitoreados: {len(adopted_forests)}")
        print(f"   Alertas enviadas: {alerts_sent}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}\n")
        raise

if __name__ == "__main__":
    check_fires_and_alert()