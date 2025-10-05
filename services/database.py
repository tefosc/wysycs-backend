from supabase import create_client, Client
from config.settings import get_settings
from typing import Optional, List, Dict
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

class DatabaseService:
    
    @staticmethod
    def get_all_forests() -> List[Dict]:
        """Obtener todos los bosques"""
        try:
            response = supabase.table('forests').select('*').execute()
            return response.data
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return []
    
    @staticmethod
    def get_forest_by_id(forest_id: str) -> Optional[Dict]:
        """Obtener bosque específico"""
        try:
            response = supabase.table('forests').select('*').eq('id', forest_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return None
    
    @staticmethod
    def adopt_forest(forest_id: str, guardian_name: str, guardian_email: str, 
                     telegram_chat_id: Optional[str] = None) -> Dict:
        """Adoptar bosque"""
        try:
            forest = DatabaseService.get_forest_by_id(forest_id)
            if not forest:
                raise ValueError(f"Forest {forest_id} not found")
            
            data = {
                'forest_id': forest_id,
                'guardian_name': guardian_name,
                'guardian_email': guardian_email,
                'telegram_chat_id': telegram_chat_id
            }
            
            response = supabase.table('adopted_forests').insert(data).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise
    
    @staticmethod
    def get_guardian_forests(email: str) -> List[Dict]:
        """Bosques de un guardián"""
        try:
            response = supabase.table('adopted_forests')\
                .select('*, forests(*)')\
                .eq('guardian_email', email)\
                .eq('is_active', True)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return []