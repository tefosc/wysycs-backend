from fastapi import APIRouter, HTTPException
from services.database import DatabaseService, supabase
from typing import Optional


router = APIRouter(prefix="/api/v1", tags=["Gamification"])

# Sistema de niveles
LEVELS = {
    "Seedling": {"min_points": 0, "max_points": 50, "emoji": "🌱"},
    "Protector": {"min_points": 51, "max_points": 150, "emoji": "🌳"},
    "Guardian": {"min_points": 151, "max_points": 300, "emoji": "🦅"},
    "Ancestral Leader": {"min_points": 301, "max_points": 999999, "emoji": "🏆"}
}

def calculate_level(points: int) -> str:
    """Calcular nivel basado en puntos"""
    for level, config in LEVELS.items():
        if config["min_points"] <= points <= config["max_points"]:
            return level
    return "Seedling"

def calculate_points_for_adoption() -> int:
    """Puntos por adoptar un bosque"""
    return 10

def calculate_points_for_alert_action() -> int:
    """Puntos por actuar ante una alerta"""
    return 25

@router.get("/leaderboard")
def get_leaderboard(limit: int = 10):
    """
    Obtener top guardianes del bosque
    
    Args:
        limit: Número de guardianes a mostrar (default 10)
    
    Returns:
        Top guardianes con puntos, nivel y bosques adoptados
    """
    try:
        # Obtener todas las adopciones
        result = supabase.table('adopted_forests') \
            .select('guardian_email, guardian_name, points, guardian_level') \
            .eq('is_active', True) \
            .execute()
        
        if not result.data:
            return {
                "leaderboard": [],
                "total_guardians": 0
            }
        
        # Agrupar por guardián y sumar puntos
        guardians = {}
        for adoption in result.data:
            email = adoption['guardian_email']
            if email not in guardians:
                guardians[email] = {
                    'guardian_name': adoption['guardian_name'],
                    'guardian_email': email,
                    'total_points': 0,
                    'guardian_level': adoption.get('guardian_level', 'Seedling'),
                    'forests_count': 0
                }
            # SUMAR los puntos de cada adopción
            guardians[email]['total_points'] += adoption.get('points', 0)
            guardians[email]['forests_count'] += 1
        
        # Convertir a lista y ordenar por puntos
        leaderboard = sorted(
            guardians.values(),
            key=lambda x: x['total_points'],
            reverse=True
        )[:limit]
        
        # Agregar ranking y emoji
        # Agregar ranking, recalcular nivel y emoji
        for idx, guardian in enumerate(leaderboard, 1):
            guardian['rank'] = idx
            # ✅ RECALCULAR nivel basado en puntos totales
            guardian['guardian_level'] = calculate_level(guardian['total_points'])
            level_config = LEVELS.get(guardian['guardian_level'], LEVELS['Seedling'])
            guardian['level_emoji'] = level_config['emoji']
                
        return {
            "leaderboard": leaderboard,
            "total_guardians": len(guardians)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_global_stats():
    """
    Estadísticas globales del sistema
    
    Returns:
        Estadísticas de adopciones, guardianes, alertas, etc.
    """
    try:
        # Total adopciones
        adoptions = supabase.table('adopted_forests') \
            .select('*', count='exact') \
            .eq('is_active', True) \
            .execute()
        
        # Total guardianes únicos
        guardians = supabase.table('adopted_forests') \
            .select('guardian_email') \
            .eq('is_active', True) \
            .execute()
        
        unique_guardians = len(set([g['guardian_email'] for g in guardians.data])) if guardians.data else 0
        
        # Total alertas enviadas
        alerts = supabase.table('alerts_sent') \
            .select('*', count='exact') \
            .execute()
        
        # Distribución por nivel
        level_distribution = {
            "Seedling": 0,
            "Protector": 0,
            "Guardian": 0,
            "Ancestral Leader": 0
        }
        
        if guardians.data:
            for guardian in guardians.data:
                result = supabase.table('adopted_forests') \
                    .select('guardian_level') \
                    .eq('guardian_email', guardian['guardian_email']) \
                    .limit(1) \
                    .execute()
                
                if result.data:
                    level = result.data[0].get('guardian_level', 'Seedling')
                    if level in level_distribution:
                        level_distribution[level] += 1
        
        return {
            "total_adoptions": len(adoptions.data) if adoptions.data else 0,
            "total_guardians": unique_guardians,
            "total_alerts_sent": len(alerts.data) if alerts.data else 0,
            "level_distribution": level_distribution,
            "levels_info": LEVELS
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/guardian/{email}/points")
def update_guardian_points(email: str, points_to_add: int):
    """
    Actualizar puntos de un guardián
    
    Args:
        email: Email del guardián
        points_to_add: Puntos a agregar
    
    Returns:
        Información actualizada del guardián
    """
    try:
        # Obtener adopciones del guardián
        result = supabase.table('adopted_forests') \
            .select('*') \
            .eq('guardian_email', email) \
            .eq('is_active', True) \
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Guardián no encontrado")
        
        # Calcular nuevos puntos
        current_points = result.data[0].get('points', 0)
        new_points = current_points + points_to_add
        
        # Calcular nuevo nivel
        new_level = calculate_level(new_points)
        
        # Actualizar todas las adopciones del guardián
        update_result = supabase.table('adopted_forests') \
            .update({
                'points': new_points,
                'guardian_level': new_level
            }) \
            .eq('guardian_email', email) \
            .execute()
        
        level_config = LEVELS.get(new_level, LEVELS['Seedling'])
        
        return {
            "guardian_email": email,
            "points_added": points_to_add,
            "total_points": new_points,
            "previous_level": result.data[0].get('guardian_level', 'Seedling'),
            "current_level": new_level,
            "level_emoji": level_config['emoji'],
            "message": f"New level reached: {level_config['emoji']} {new_level}!" if new_level != result.data[0].get('guardian_level') else "Points updated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/guardian/{email}/progress")
def get_guardian_progress(email: str):
    """
    Obtener progreso del guardián hacia el siguiente nivel
    
    Args:
        email: Email del guardián
    
    Returns:
        Información de progreso y siguiente nivel
    """
    try:
        # Obtener TODAS las adopciones del guardián
        result = supabase.table('adopted_forests') \
            .select('*') \
            .eq('guardian_email', email) \
            .eq('is_active', True) \
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Guardián no encontrado")
        
        # ✅ SUMAR puntos de todas las adopciones
        total_points = sum([adoption.get('points', 0) for adoption in result.data])
        
        # ✅ RECALCULAR nivel basado en puntos totales
        current_level = calculate_level(total_points)
        
        # Encontrar siguiente nivel
        levels_list = list(LEVELS.items())
        current_index = next(i for i, (level, _) in enumerate(levels_list) if level == current_level)
        
        if current_index < len(levels_list) - 1:
            next_level_name, next_level_config = levels_list[current_index + 1]
            points_needed = next_level_config['min_points'] - total_points
            progress_percentage = int((total_points / next_level_config['min_points']) * 100)
        else:
            next_level_name = "Maximum level reached"
            points_needed = 0
            progress_percentage = 100
        
        current_config = LEVELS[current_level]
        
        return {
            "guardian_email": email,
            "guardian_name": result.data[0]['guardian_name'],
            "current_level": {
                "name": current_level,
                "emoji": current_config['emoji'],
                "points": total_points  # ✅ Puntos totales, no de una adopción
            },
            "next_level": {
                "name": next_level_name,
                "points_needed": max(0, points_needed),  # No negativos
                "progress_percentage": min(100, progress_percentage)  # Max 100%
            },
            "forests_adopted": len(result.data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))