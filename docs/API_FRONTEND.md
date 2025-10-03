# WYSYCS Backend API - Documentación para Frontend

## 🌐 URL Base de Producción

```
https://web-production-7dae.up.railway.app
```

## 📚 Documentación Interactiva

```
https://web-production-7dae.up.railway.app/docs
```

---

## 📡 Endpoints Disponibles

### 1. Listar todos los bosques

**GET** `/forests`

**Respuesta:**

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
    "fun_facts": [...]
  }
]
```

---

### 2. Obtener bosque específico

**GET** `/forests/{id}`

**Parámetros:**

- `id`: ID del bosque (1-10)

---

### 3. Adoptar un bosque

**POST** `/adopt`

**Body:**

```json
{
  "forest_id": "1",
  "guardian_name": "María López",
  "guardian_email": "maria@email.com"
}
```

---

### 4. Ver bosques de un guardián

**GET** `/guardian/{email}`

**Parámetros:**

- `email`: Email del guardián

---

### 5. Incendios en Perú (datos NASA FIRMS)

**GET** `/fires/peru?days=2`

**Parámetros:**

- `days`: Días hacia atrás (1-10)

**Respuesta:**

- Array de incendios detectados

---

### 6. Analizar punto en mapa ⭐ MÁS IMPORTANTE

**GET** `/fires/analyze?lat=-8.3&lon=-75.6&radius_km=50&days=2`

**Parámetros:**

- `lat`: Latitud (-90 a 90)
- `lon`: Longitud (-180 a 180)
- `radius_km`: Radio de búsqueda (1-100)
- `days`: Días hacia atrás (1-10)

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
  "fires": [...],
  "recommendations": [...]
}
```

**Niveles de riesgo y colores para UI:**

- CRÍTICO: `#ef4444` (rojo)
- ALTO: `#f97316` (naranja)
- MODERADO: `#fbbf24` (amarillo)
- BAJO: `#10b981` (verde)

---

### 7. Estadísticas de incendios

**GET** `/fires/stats?days=7`

**Parámetros:**

- `days`: Período de análisis (1-30)

---

## 🎨 Ejemplo de integración en React

```javascript
// Analizar punto del mapa al hacer click
const handleMapClick = async (lat, lon) => {
  const response = await fetch(
    `https://web-production-7dae.up.railway.app/api/v1/fires/analyze?lat=${lat}&lon=${lon}&radius_km=20&days=2`
  );
  const data = await response.json();

  // Usar el color del riesgo en el UI
  setRiskColor(data.risk_assessment.color);
  setRiskLevel(data.risk_assessment.level);
};
```

---

## 📝 Notas importantes

- Todos los endpoints devuelven **JSON**
- CORS está habilitado para todos los orígenes
- Los datos de incendios son **REALES de NASA FIRMS**
- El backend se actualiza automáticamente con cada push a GitHub

---

## 🚀 Estado actual del backend

✅ Endpoints funcionando
✅ Datos reales de NASA
✅ Base de datos Supabase conectada
✅ Deploy automático configurado

⏳ Por implementar (viernes):

- Notificaciones por email
- Predicciones ML
- Bot de Telegram
