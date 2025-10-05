from prophet import Prophet
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import warnings

warnings.filterwarnings('ignore')

class PredictorService:
    
    @staticmethod
    def predict_forest_health(historical_data: List[Dict], days_ahead: int = 90) -> Dict:
        """
        Predecir salud futura del bosque usando Prophet
        
        Args:
            historical_data: Lista de dict con 'date' y 'ndvi'
            days_ahead: Días hacia adelante para predecir
        
        Returns:
            Predicciones con tendencia y recomendaciones
        """
        try:
            # Preparar datos para Prophet
            df = pd.DataFrame(historical_data)
            df['ds'] = pd.to_datetime(df['date'])
            df['y'] = df['ndvi']
            df = df[['ds', 'y']]
            
            # Entrenar modelo Prophet
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
            model.fit(df)
            
            # Crear fechas futuras
            future = model.make_future_dataframe(periods=days_ahead, freq='D')
            forecast = model.predict(future)
            
            # Extraer predicciones futuras
            future_predictions = forecast[forecast['ds'] > df['ds'].max()].copy()
            
            # Convertir NDVI a porcentaje de salud
            def ndvi_to_health(ndvi):
                return int(min(100, max(0, ndvi * 150)))
            
            predictions = []
            for _, row in future_predictions.iterrows():
                # Limitar NDVI entre -1 y 1 (rango válido)
                predicted_ndvi = max(-1, min(1, row['yhat']))
                
                predictions.append({
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'predicted_ndvi': round(predicted_ndvi, 3),
                    'predicted_health': ndvi_to_health(predicted_ndvi),
                    'lower_bound': round(max(-1, min(1, row['yhat_lower'])), 3),
                    'upper_bound': round(max(-1, min(1, row['yhat_upper'])), 3)
                })
            
            # Analizar tendencia
            current_ndvi = df['y'].iloc[-1]
            predicted_ndvi = min(1, max(-1, predictions[-1]['predicted_ndvi']))
            change = predicted_ndvi - current_ndvi
            change_percentage = (change / current_ndvi) * 100
            
            if change_percentage < -10:
                trend = "declining"
                risk_level = "HIGH"
                message = f"⚠️ Forest will lose {abs(int(change_percentage))}% of health in {days_ahead} days"
            elif change_percentage < -5:
                trend = "slightly_declining"
                risk_level = "MODERATE"
                message = f"⚠️ Slight decrease of {abs(int(change_percentage))}% expected"
            elif change_percentage > 5:
                trend = "improving"
                risk_level = "LOW"
                message = f"✅ Forest will improve {int(change_percentage)}% in {days_ahead} days"
            else:
                trend = "stable"
                risk_level = "LOW"
                message = f"✅ Forest will remain stable"
            
            return {
                'predictions': predictions[:30],  # Máximo 30 días
                'trend': trend,
                'risk_assessment': {
                    'level': risk_level,
                    'message': message,
                    'change_percentage': round(change_percentage, 1)
                },
                'current_ndvi': round(current_ndvi, 3),
                'predicted_ndvi': round(predicted_ndvi, 3)
            }
            
        except Exception as e:
            print(f"Error en predicción: {e}")
            return PredictorService._get_fallback_prediction(days_ahead)
    
    @staticmethod
    def _get_fallback_prediction(days_ahead: int) -> Dict:
        """Predicción de respaldo si Prophet falla"""
        return {
            'predictions': [],
            'trend': 'stable',
            'risk_assessment': {
                'level': 'UNKNOWN',
                'message': 'Not enough historical data for prediction',
                'change_percentage': 0
            },
            'current_ndvi': 0,
            'predicted_ndvi': 0
        }
    
    @staticmethod
    def simulate_fire_impact(fire_area_ha: float, scenarios: List[int] = [1, 2, 7]) -> Dict:
        """
        Simular impacto de incendio en diferentes escenarios temporales
        
        Args:
            fire_area_ha: Área actual del incendio en hectáreas
            scenarios: Lista de días para simular
        
        Returns:
            Simulaciones de impacto ambiental y social
        """
        results = []
        
        for days in scenarios:
            # Crecimiento del fuego (hectáreas/día)
            growth_rate = 15
            total_area = fire_area_ha + (growth_rate * days)
            
            # Calidad del aire (AQI)
            base_aqi = total_area * 3
            aqi = min(500, int(base_aqi))
            
            if aqi > 300:
                aqi_category = "Hazardous"
            elif aqi > 200:
                aqi_category = "Very Unhealthy"
            elif aqi > 150:
                aqi_category = "Unhealthy"
            else:
                aqi_category = "Unhealthy for Sensitive Groups"
            
            # Emisiones CO2
            co2_tonnes = total_area * 80
            cars_equivalent = int(co2_tonnes / 4.6)
            
            # Población afectada
            affected_population = int(total_area * 25)
            
            if affected_population > 5000:
                severity = "Critical"
            elif affected_population > 2000:
                severity = "Severe"
            else:
                severity = "Moderate"
            
            # Recursos hídricos
            families_without_water = int(affected_population / 5)
            
            # Biodiversidad
            species_affected = int(total_area * 0.8)
            
            results.append({
                'days_ahead': days,
                'fire': {
                    'total_area_ha': round(total_area, 1),
                    'growth_rate': growth_rate,
                    'area_burned': round(total_area - fire_area_ha, 1)
                },
                'air_quality': {
                    'aqi': aqi,
                    'category': aqi_category
                },
                'emissions': {
                    'co2_tonnes': int(co2_tonnes),
                    'cars_equivalent': cars_equivalent
                },
                'population': {
                    'affected': affected_population,
                    'severity': severity
                },
                'water': {
                    'families_without_water': families_without_water,
                    'rivers_at_risk': ["Río Marañón", "Río Ucayali"] if total_area > 100 else []
                },
                'biodiversity': {
                    'species_affected': species_affected,
                    'critical_species': ["Jaguar", "Oso de anteojos", "Guacamayo rojo"] if total_area > 150 else []
                }
            })
        
        # Recomendaciones basadas en el peor escenario
        worst_scenario = results[-1]
        recommendations = []
        
        if worst_scenario['air_quality']['aqi'] > 200:
            recommendations.append("🚨 Immediate evacuation of nearby communities")

        if worst_scenario['population']['affected'] > 2000:
            recommendations.append("🏥 Activate emergency health centers")

        if worst_scenario['fire']['total_area_ha'] > 200:
            recommendations.append("🚁 Request aerial support for firefighting")

        if worst_scenario['water']['families_without_water'] > 500:
            recommendations.append("💧 Distribute emergency drinking water")

        recommendations.append("📢 Inform environmental authorities (SERNANP/MINAM)")
        
        return {
            'scenarios': results,
            'recommendations': recommendations,
            'worst_case': {
                'days': scenarios[-1],
                'total_area': worst_scenario['fire']['total_area_ha'],
                'population_affected': worst_scenario['population']['affected']
            }
        }


# Instancia global
predictor_service = PredictorService()