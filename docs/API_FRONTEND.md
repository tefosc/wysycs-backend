# WYSYCS Backend API - Documentación para Frontend

**Última actualización:** Viernes 4 Oct 2025, 21:00  
**Versión:** 1.0.0  
**Estado:** ✅ Producción

---

## 🌐 URLs Base

### Producción

```
https://web-production-7dae.up.railway.app/api/v1
```

### Documentación Interactiva (Swagger)

```
https://web-production-7dae.up.railway.app/docs
```

### Local (Desarrollo)

```
http://localhost:8000/api/v1
```

---

## 📡 Endpoints Disponibles (22 total)

### 🌳 BOSQUES (2 endpoints)

#### 1. Listar todos los bosques

```http
GET /forests
```

**Descripción:** Obtiene la lista completa de 10 bosques disponibles para adoptar.

**Respuesta:** Array de objetos (sin datos NASA en tiempo real)

```json
[
  {
    "id": "1",
    "name": "Bosque de Neblina Pacaya-Samiria",
    "latitude": -4.5,
    "longitude": -74.2,
    "health": 45,
    "co2_capture": "8,400 toneladas/año",
    "species_count": 342,
    "community": "Comunidad Kukama Kukamiria",
    "fun_facts": [
      "🦜 Alberga al guacamayo rojo en peligro de extinción",
      "💧 Filtra agua para 50,000 personas del río Marañón",
      "🌳 Contiene 120,000 árboles de caoba y cedro"
    ],
    "created_at": "2025-10-02T03:02:24.344938"
  },
  {
    "id": "2",
    "name": "Selva Alta Cordillera Azul",
    "latitude": -5.8,
    "longitude": -76.5,
    "health": 62,
    "co2_capture": "12,100 toneladas/año",
    "species_count": 287,
    "community": "Comunidad Awajún",
    "fun_facts": [
      "🐆 Hogar del oso de anteojos andino",
      "💧 Protege nacientes de 7 ríos",
      "🌺 347 especies de orquídeas nativas"
    ],
    "created_at": "2025-10-02T03:02:24.344938"
  }
  // ... 8 bosques más
]
```

**Nota:** El campo `health` es un valor histórico de la base de datos. Para salud en tiempo real, usar el endpoint individual.

---

#### 2. Obtener bosque específico con salud NASA en tiempo real ⭐

```http
GET /forests/{id}
```

**Parámetros:**

- `id` (path): ID del bosque (1-10)

**Descripción:** Obtiene información completa del bosque + salud en tiempo real desde satélites NASA MODIS.

**Respuesta:** Objeto único con datos NASA integrados

```json
{
  "id": "1",
  "name": "Bosque de Neblina Pacaya-Samiria",
  "latitude": -4.5,
  "longitude": -74.2,
  "health": 45,
  "co2_capture": "8,400 toneladas/año",
  "species_count": 342,
  "community": "Comunidad Kukama Kukamiria",
  "fun_facts": [
    "🦜 Alberga al guacamayo rojo en peligro de extinción",
    "💧 Filtra agua para 50,000 personas del río Marañón",
    "🌳 Contiene 120,000 árboles de caoba y cedro"
  ],
  "created_at": "2025-10-02T03:02:24.344938",
  "health_nasa": {
    "ndvi_value": 0.829,
    "health_percentage": 95,
    "status": "Saludable",
    "color": "#10b981",
    "source": "MODIS/061/MOD13Q1 (NASA)",
    "is_real_data": true,
    "last_update": "2025-10-04T17:11:04.268731"
  }
}
```

**Campos importantes:**

| Campo                           | Descripción                                                   |
| ------------------------------- | ------------------------------------------------------------- |
| `health`                        | Valor histórico de base de datos (puede estar desactualizado) |
| `health_nasa.health_percentage` | **Salud en tiempo real desde satélite NASA** ⭐               |
| `health_nasa.ndvi_value`        | Índice de vegetación (0-1)                                    |
| `health_nasa.status`            | Estado: Saludable / En riesgo / Deteriorado / Crítico         |
| `health_nasa.color`             | Color hexadecimal para UI                                     |
| `health_nasa.is_real_data`      | `true` = datos NASA, `false` = estimación (GEE falló)         |

**Estados de salud y colores:**

| Estado      | Salud  | Color    | Hex       |
| ----------- | ------ | -------- | --------- |
| Saludable   | ≥70%   | Verde    | `#10b981` |
| En riesgo   | 50-69% | Amarillo | `#f59e0b` |
| Deteriorado | 30-49% | Naranja  | `#f97316` |
| Crítico     | <30%   | Rojo     | `#ef4444` |

**Recomendación Frontend:**

- Para listar bosques: usar `GET /forests`
- Para mostrar detalles y salud actual: usar `GET /forests/{id}`
- Siempre usar `health_nasa.health_percentage` para indicadores de salud
- Ignorar el campo `health` (está desactualizado)

---

**Ejemplo de integración React:**

```javascript
// Listar bosques
const forests = await fetch(
  "https://web-production-7dae.up.railway.app/api/v1/forests"
).then((res) => res.json());

// Obtener detalle con NASA
const forestDetail = await fetch(
  "https://web-production-7dae.up.railway.app/api/v1/forests/1"
).then((res) => res.json());

// Usar datos NASA
const healthColor = forestDetail.health_nasa.color;
const healthPercent = forestDetail.health_nasa.health_percentage;
const isRealData = forestDetail.health_nasa.is_real_data;
```

### 🤝 ADOPCIÓN (2 endpoints)

#### 3. Adoptar un bosque

```http
POST /adopt
```

**Body:**

```json
{
  "forest_id": "1",
  "guardian_name": "María López",
  "guardian_email": "maria@email.com",
  "telegram_chat_id": "123456789" // Opcional
}
```

**Respuesta:**

```json
{
  "success": true,
  "message": "¡Bosque adoptado exitosamente!",
  "adoption_id": "uuid-here",
  "email_sent": true,
  "points_earned": 10,
  "guardian_level": "Sembrador"
}
```

**Nota:** Email solo funciona con: `asolism17_1@unc.edu.pe` (limitación plan gratuito Resend)

#### 4. Ver bosques de un guardián

```http
GET /guardian/{email}
```

**Parámetros:**

- `email` (path): Email del guardián

**Respuesta:**

```json
{
  "guardian_email": "maria@email.com",
  "guardian_name": "María López",
  "adopted_forests": [...],
  "total_forests": 2,
  "total_points": 20,
  "guardian_level": "Sembrador"
}
```

---

### 🔥 INCENDIOS - NASA FIRMS (3 endpoints)

#### 5. Incendios en Perú

```http
GET /fires/peru?days=2
```

**Parámetros:**

- `days` (query): Días hacia atrás (1-10), default: 1

**Respuesta:**

```json
[
  {
    "latitude": -8.3,
    "longitude": -75.6,
    "brightness": 325.4,
    "confidence": "high",
    "acquired_date": "2025-10-03",
    "acquired_time": "1430"
  }
]
```

#### 6. Incendios cerca de bosque

```http
GET /fires/forest/{id}?radius_km=20&days=2
```

**Parámetros:**

- `id` (path): ID del bosque
- `radius_km` (query): Radio búsqueda (default: 50)
- `days` (query): Días hacia atrás (default: 1)

#### 7. Analizar punto en mapa ⭐ CRÍTICO

```http
GET /fires/analyze?lat=-8.3&lon=-75.6&radius_km=50&days=2
```

**Parámetros:**

- `lat` (query): Latitud (-90 a 90)
- `lon` (query): Longitud (-180 a 180)
- `radius_km` (query): Radio búsqueda (1-100)
- `days` (query): Días hacia atrás (1-10)

**Respuesta:**

```json
{
  "risk_assessment": {
    "level": "CRÍTICO",
    "color": "#ef4444",
    "description": "¡PELIGRO! Incendio a solo 3.07km",
    "fires_detected": 2,
    "closest_fire_km": 3.07
  },
  "fires": [
    {
      "latitude": -8.29,
      "longitude": -75.58,
      "distance_km": 3.07,
      "brightness": 325.4,
      "confidence": "high"
    }
  ],
  "recommendations": [
    "🚨 Evacuar zona inmediatamente",
    "📞 Contactar bomberos locales"
  ]
}
```

**Niveles de riesgo y colores UI:**

- `CRÍTICO`: `#ef4444` (rojo) - Incendio < 10km
- `ALTO`: `#f97316` (naranja) - Incendio 10-20km
- `MODERADO`: `#fbbf24` (amarillo) - Incendio 20-50km
- `BAJO`: `#10b981` (verde) - Sin incendios < 50km

**🔥 Coordenadas de prueba con incendios REALES:**

```javascript
// Zona crítica (incendio detectado)
lat: -8.3, lon: -75.6

// Otras zonas con actividad
lat: -12.87, lon: -70.44  // Madre de Dios
lat: -7.86, lon: -71.73   // Ucayali
lat: -6.18, lon: -76.09   // San Martín
```

---

### 🛰️ SALUD FORESTAL - NASA MODIS (4 endpoints)

#### 8. Salud actual del bosque

```http
GET /forest/{id}/health
```

**Respuesta:**

```json
{
  "forest_id": "1",
  "forest_name": "Bosque de Neblina Pacaya-Samiria",
  "location": {
    "latitude": -4.5,
    "longitude": -74.2
  },
  "ndvi_value": 0.829,
  "health_percentage": 95,
  "status": "Saludable",
  "color": "#10b981",
  "source": "MODIS/061/MOD13Q1 (NASA)",
  "is_real_data": true,
  "last_update": "2025-10-03T18:00:00"
}
```

**Estados y colores:**

- `Saludable` (≥70%): `#10b981` (verde)
- `En riesgo` (50-69%): `#f59e0b` (amarillo)
- `Deteriorado` (30-49%): `#f97316` (naranja)
- `Crítico` (<30%): `#ef4444` (rojo)

#### 9. Histórico NDVI de bosque

```http
GET /forest/{id}/history?months=12
```

**Parámetros:**

- `months` (query): Meses hacia atrás (1-24), default: 12

**Respuesta:**

```json
{
  "forest_id": "1",
  "forest_name": "Bosque de Neblina Pacaya-Samiria",
  "months_requested": 12,
  "data_points": 23,
  "history": [
    {
      "date": "2024-10-01",
      "ndvi": 0.799,
      "health": 100
    }
  ]
}
```

#### 10. Analizar punto personalizado ⭐

```http
GET /analyze/point?lat=-8.3&lon=-75.6
```

**Parámetros:**

- `lat` (query): Latitud
- `lon` (query): Longitud

**Uso:** Usuario hace click en mapa → Analizar salud de ese punto

#### 11. Histórico de punto personalizado

```http
GET /analyze/point/history?lat=-8.3&lon=-75.6&months=6
```

**🌿 Coordenada ejemplo - Deforestación REAL detectada:**

```javascript
lat: -8.29356, lon: -74.79893
// NDVI cayó de 0.8 → 0.3 (Ago-Sept 2025)
// Pérdida de 60% vegetación
```

---

### 🤖 PREDICCIONES ML (3 endpoints)

#### 12. Predicción de salud forestal

```http
GET /forest/{id}/prediction?days_ahead=90
```

**Parámetros:**

- `days_ahead` (query): Días a predecir (1-365), default: 90

**Respuesta:**

```json
{
  "forest_id": "1",
  "days_ahead": 90,
  "predictions": [
    {
      "date": "2025-11-01",
      "predicted_ndvi": 0.654,
      "predicted_health": 65,
      "lower_bound": 0.62,
      "upper_bound": 0.69
    }
  ],
  "trend": "declining",
  "risk_assessment": {
    "level": "ALTO",
    "message": "El bosque perderá 6 puntos en 90 días",
    "change_percentage": -6.5
  },
  "current_ndvi": 0.829,
  "predicted_ndvi": 0.654
}
```

**⚠️ LIMITACIÓN IMPORTANTE:**

- Prophet tiene solo 6 meses de datos (11 puntos)
- Necesita 50-100 puntos para precisión
- **Frontend debe mostrar SOLO la "tendencia"**
- NO mostrar predicciones exactas ni fechas

**Valores de tendencia:**

- `improving`: Mejorando
- `declining`: En declive
- `slightly_declining`: Ligero declive
- `stable`: Estable

#### 13. Predicción de punto personalizado

```http
GET /analyze/point/prediction?lat=-8.3&lon=-75.6&days_ahead=90
```

#### 14. Simulador de impacto ⭐ FUNCIONA PERFECTO

```http
POST /simulate-impact
```

**Body:**

```json
{
  "fire_area_ha": 50,
  "scenarios": [1, 2, 7]
}
```

**Respuesta:**

```json
{
  "initial_fire_area_ha": 50.0,
  "scenarios": [
    {
      "days_ahead": 7,
      "fire": {
        "total_area_ha": 155.0,
        "growth_rate": 15,
        "area_burned": 105.0
      },
      "air_quality": {
        "aqi": 465,
        "category": "Peligroso"
      },
      "emissions": {
        "co2_tonnes": 12400,
        "cars_equivalent": 2695
      },
      "population": {
        "affected": 3875,
        "severity": "Grave"
      },
      "water": {
        "families_without_water": 775,
        "rivers_at_risk": ["Río Marañón", "Río Ucayali"]
      },
      "biodiversity": {
        "species_affected": 124,
        "critical_species": ["Jaguar", "Oso de anteojos"]
      }
    }
  ],
  "recommendations": [
    "🚨 Evacuación inmediata de comunidades cercanas",
    "🏥 Activar centros de salud de emergencia",
    "💧 Distribuir agua potable de emergencia"
  ],
  "worst_case": {
    "days": 7,
    "total_area": 155.0,
    "population_affected": 3875
  }
}
```

---

### 🎮 GAMIFICACIÓN (4 endpoints)

#### 15. Leaderboard

```http
GET /leaderboard?limit=10
```

**Parámetros:**

- `limit` (query): Número de guardianes (default: 10)

**Respuesta:**

```json
{
  "leaderboard": [
    {
      "rank": 1,
      "guardian_name": "María López",
      "guardian_email": "maria@email.com",
      "total_points": 100,
      "guardian_level": "Protector",
      "level_emoji": "🌳",
      "forests_count": 3
    }
  ],
  "total_guardians": 25
}
```

**Sistema de niveles:**

- 🌱 Sembrador: 0-50 puntos
- 🌳 Protector: 51-150 puntos
- 🦅 Guardián: 151-300 puntos
- 🏆 Líder Ancestral: 301+ puntos

#### 16. Estadísticas globales

```http
GET /stats
```

**Respuesta:**

```json
{
  "total_adoptions": 47,
  "total_guardians": 25,
  "total_alerts_sent": 12,
  "level_distribution": {
    "Sembrador": 15,
    "Protector": 8,
    "Guardián": 2,
    "Líder Ancestral": 0
  },
  "levels_info": {...}
}
```

#### 17. Actualizar puntos guardián

```http
PUT /guardian/{email}/points?points_to_add=25
```

**Parámetros:**

- `email` (path): Email del guardián
- `points_to_add` (query): Puntos a agregar

#### 18. Progreso del guardián

```http
GET /guardian/{email}/progress
```

**Respuesta:**

```json
{
  "guardian_email": "maria@email.com",
  "guardian_name": "María López",
  "current_level": {
    "name": "Sembrador",
    "emoji": "🌱",
    "points": 45
  },
  "next_level": {
    "name": "Protector",
    "points_needed": 6,
    "progress_percentage": 90
  },
  "forests_adopted": 2
}
```

---

### 📧 NOTIFICACIONES (2 endpoints)

#### 19. Test email

```http
POST /test-email
```

**Body:**

```json
{
  "email": "asolism17_1@unc.edu.pe",
  "guardian_name": "Test"
}
```

**⚠️ Solo funciona con:** `asolism17_1@unc.edu.pe`

#### 20. Test alerta incendio

```http
POST /test-fire-alert
```

---

### ⚙️ SISTEMA (2 endpoints)

#### 21. Root

```http
GET /
```

#### 22. Health check

```http
GET /health
```

---

## 🎨 Ejemplos de Integración

### React - Analizar punto del mapa

```javascript
const handleMapClick = async (lat, lon) => {
  const response = await fetch(
    `https://web-production-7dae.up.railway.app/api/v1/fires/analyze?lat=${lat}&lon=${lon}&radius_km=20&days=2`
  );
  const data = await response.json();

  // Usar color del riesgo en UI
  setRiskColor(data.risk_assessment.color);
  setRiskLevel(data.risk_assessment.level);

  // Mostrar incendios en mapa
  setFireMarkers(
    data.fires.map((fire) => ({
      position: [fire.latitude, fire.longitude],
      distance: fire.distance_km,
    }))
  );
};
```

### React - Obtener salud NDVI

```javascript
const getForestHealth = async (forestId) => {
  const response = await fetch(
    `https://web-production-7dae.up.railway.app/api/v1/forest/${forestId}/health`
  );
  const data = await response.json();

  return {
    ndvi: data.ndvi_value,
    health: data.health_percentage,
    status: data.status,
    color: data.color,
    isRealData: data.is_real_data,
  };
};
```

### React - Simulador de impacto

```javascript
const simulateImpact = async (areaHa) => {
  const response = await fetch(
    `https://web-production-7dae.up.railway.app/api/v1/simulate-impact`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        fire_area_ha: areaHa,
        scenarios: [1, 2, 7],
      }),
    }
  );

  const data = await response.json();
  return data.scenarios;
};
```

---

## ⚠️ Limitaciones Conocidas

### 1. Predicciones ML (Prophet)

**Problema:** Solo 6 meses de datos MODIS = predicciones poco realistas

**Solución:**

- Mostrar SOLO el campo `trend` (improving/declining/stable)
- NO mostrar `predicted_ndvi` ni fechas exactas
- Agregar disclaimer: "Proyección basada en datos limitados"

### 2. Emails

**Problema:** Resend plan gratuito solo envía a email del dueño

**Solución:**

- Usar solo `asolism17_1@unc.edu.pe` para demos
- Para producción: Verificar dominio en Resend

### 3. Cron Job

**Problema:** No ejecuta automáticamente cada 2h en Railway

**Estado:** Endpoint manual disponible

- `POST /cron/check-fires` (requiere configuración externa)

---

## 🚀 Datos de Prueba

### Bosques con diferentes estados

```javascript
// Bosque saludable
forestId: "1"; // NDVI: 0.829, 95% salud

// Bosque en riesgo
forestId: "4"; // NDVI: 0.45, 54% salud
```

### Coordenadas con incendios

```javascript
// CRÍTICO - Incendio a 3km
lat: -8.3, lon: -75.6

// Deforestación real
lat: -8.29356, lon: -74.79893
```

### Emails para testing

```javascript
// ✅ Funciona
email: "asolism17_1@unc.edu.pe";

// ❌ No funciona (plan gratuito)
email: "otro@gmail.com";
```

---

## 📊 Códigos de Estado HTTP

- `200`: Éxito
- `404`: Recurso no encontrado (bosque, guardián)
- `400`: Parámetros inválidos
- `500`: Error del servidor

---

## 🔧 CORS

CORS habilitado para todos los orígenes en desarrollo.

Para producción, configurar origins específicos.

---

## 📱 Estado del Backend

**Última actualización:** Viernes 4 Oct 2025, 21:00

✅ **Funcionando:**

- 22 endpoints operativos
- Datos NASA reales (MODIS + VIIRS)
- Sistema de gamificación completo
- Simulador de impacto preciso
- Deploy automático desde GitHub

⚠️ **Limitaciones:**

- Prophet con datos limitados
- Emails solo a email institucional
- Cron job manual

---

## 📞 Contacto

**Backend Developer:** Annie  
**Equipo:** WYSIATI  
**Proyecto:** WYSYCS (What You See, You Can Save)  
**NASA Space Apps Challenge 2025** - Cajamarca, Perú
