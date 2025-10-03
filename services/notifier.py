import resend
from config.settings import get_settings
from typing import Optional

settings = get_settings()
resend.api_key = settings.resend_api_key

class NotificationService:
    """Servicio para enviar notificaciones por email"""
    
    @staticmethod
    def send_adoption_email(guardian_name: str, guardian_email: str, forest_name: str) -> bool:
        """Email de confirmación de adopción"""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .forest-name {{ color: #10b981; font-size: 24px; font-weight: bold; }}
                    .cta-button {{ background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🌳 ¡Felicidades {guardian_name}!</h1>
                    </div>
                    <div class="content">
                        <p>Has adoptado exitosamente:</p>
                        <p class="forest-name">{forest_name}</p>
                        
                        <p>Como Guardián de este bosque, ahora recibirás:</p>
                        <ul>
                            <li>🔥 Alertas de incendios cercanos en tiempo real</li>
                            <li>📊 Reportes de salud del bosque (NDVI)</li>
                            <li>🏆 Puntos por cada día protegiendo el bosque</li>
                        </ul>
                        
                        <p><strong>Tu misión:</strong> Proteger y monitorear este bosque amazónico.</p>
                        
                        <p style="margin-top: 30px; color: #6b7280;">
                            What You See, You Can Save 💚
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            params = {
                "from": "WYSYCS <onboarding@resend.dev>",
                "to": [guardian_email],
                "subject": f"🌳 ¡Adoptaste {forest_name}!",
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            print(f"✅ Email enviado a {guardian_email}: {response}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando email: {e}")
            return False
    
    @staticmethod
    def send_fire_alert(guardian_email: str, forest_name: str, distance_km: float) -> bool:
        """Email de alerta de incendio"""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #fef2f2; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .alert-box {{ background: white; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }}
                    .distance {{ font-size: 36px; font-weight: bold; color: #ef4444; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔥 ¡ALERTA DE INCENDIO!</h1>
                    </div>
                    <div class="content">
                        <p><strong>Tu bosque {forest_name} está en peligro.</strong></p>
                        
                        <div class="alert-box">
                            <p>Incendio detectado a:</p>
                            <p class="distance">{distance_km:.1f} km</p>
                            <p style="color: #6b7280;">Datos NASA - Detección satelital</p>
                        </div>
                        
                        <p><strong>Acciones recomendadas:</strong></p>
                        <ul>
                            <li>🚨 Alertar a autoridades locales</li>
                            <li>👥 Verificar con la comunidad</li>
                            <li>📞 Contactar bomberos si es necesario</li>
                        </ul>
                        
                        <p style="margin-top: 30px; color: #dc2626;">
                            <strong>Actúa rápido. Cada minuto cuenta.</strong>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            params = {
                "from": "WYSYCS <alertas@wysycs.dev>",
                "to": [guardian_email],
                "subject": f"🔥 ALERTA: Incendio cerca de {forest_name}",
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            print(f"✅ Alerta enviada a {guardian_email}: {response}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando alerta: {e}")
            return False

# Instancia global
notification_service = NotificationService()