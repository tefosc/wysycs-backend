from fastapi import APIRouter, HTTPException
from services.database import DatabaseService
from typing import List, Dict

router = APIRouter(prefix="/api/v1", tags=["Forests"])

@router.get("/forests", response_model=List[Dict])
def get_all_forests():
    """Obtener todos los bosques"""
    forests = DatabaseService.get_all_forests()
    if not forests:
        raise HTTPException(status_code=404, detail="No hay bosques")
    return forests

@router.get("/forests/{forest_id}", response_model=Dict)
def get_forest_by_id(forest_id: str):
    """Obtener un bosque específico"""
    forest = DatabaseService.get_forest_by_id(forest_id)
    if not forest:
        raise HTTPException(status_code=404, detail=f"Bosque {forest_id} no encontrado")
    return forest