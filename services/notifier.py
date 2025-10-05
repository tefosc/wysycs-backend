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
                        <h1>🌳 Congratulations {guardian_name}!</h1>
                    </div>
                    <div class="content">
                        <p>You have successfully adopted:</p>
                        <p class="forest-name">{forest_name}</p>

                        <p>As a Guardian of this forest, you will now receive:</p>
                        <ul>
                            <li>🔥 Real-time alerts for nearby fires</li>
                            <li>📊 Forest health reports (NDVI)</li>
                            <li>🏆 Points for each day protecting the forest</li>
                        </ul>

                        <p><strong>Your mission:</strong> Protect and monitor this Amazonian forest.</p>

                        <p style="margin-top: 30px; color: #6b7280;">
                            What You See, You Can Save 💚
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            params = {
                "from": "WYSYCS <alertas@wysycs.health>",
                "to": [guardian_email],
                "subject": f"🌳 You adopted {forest_name}!",
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
                        <h1>🔥 FIRE ALERT!</h1>
                    </div>
                    <div class="content">
                        <p><strong>Your forest {forest_name} is in danger.</strong></p>

                        <div class="alert-box">
                            <p>Fire detected at:</p>
                            <p class="distance">{distance_km:.1f} km</p>
                            <p style="color: #6b7280;">NASA Data - Satellite Detection</p>
                        </div>

                        <p><strong>Recommended actions:</strong></p>
                        <ul>
                            <li>🚨 Alert local authorities</li>
                            <li>👥 Check with the community</li>
                            <li>📞 Contact firefighters if necessary</li>
                        </ul>

                        <p style="margin-top: 30px; color: #dc2626;">
                            <strong>Act fast. Every minute counts.</strong>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            params = {
                "from": "WYSYCS <alertas@wysycs.health>",
                "to": [guardian_email],
                "subject": f"🔥 ALERT: Fire near {forest_name}",
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