import ee
import os
from config.settings import get_settings

settings = get_settings()

print("🧪 Test rápido de Google Earth Engine")
print("-" * 50)

# Verificar que existe el archivo JSON
json_path = settings.gee_private_key_path
print(f"📁 Buscando: {json_path}")

if os.path.exists(json_path):
    print("✅ Archivo JSON encontrado")
else:
    print("❌ Archivo JSON NO encontrado")
    print(f"   Verifica que existe: {os.path.abspath(json_path)}")
    exit(1)

# Intentar inicializar Earth Engine
try:
    print(f"\n🔑 Service Account: {settings.gee_service_account}")
    
    credentials = ee.ServiceAccountCredentials(
        settings.gee_service_account,
        json_path
    )
    ee.Initialize(credentials)
    
    print("✅ Earth Engine inicializado correctamente!")
    
    # Test simple
    print("\n🧪 Test: Obtener info básica...")
    test_string = ee.String('Hello NASA!').getInfo()
    print(f"✅ Respuesta de GEE: {test_string}")
    
    print("\n🎉 ¡TODO FUNCIONA! Listo para usar datos NASA mañana")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPosibles causas:")
    print("- El proyecto no está registrado en Earth Engine")
    print("- El service account no tiene permisos")
    print("- El archivo JSON es incorrecto")

print("-" * 50)