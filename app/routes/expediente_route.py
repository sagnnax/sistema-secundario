from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import Expediente, ExpedienteCreate, ExpedienteUpdate
from crud.expediente_crud import create_expediente, get_expedientes, get_expediente_by_id, update_expediente, delete_expediente, get_expediente_by_id_paciente
from crud.paciente_crud import get_paciente_by_id

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/expedientes/", response_model=Expediente)
def agregar_expediente(expediente: ExpedienteCreate, db: Session = Depends(get_db)):
    db_paciente = get_paciente_by_id(db, id_paciente=expediente.id_paciente)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="El ID del paciente no existe")
    db_expediente = create_expediente(db=db, expediente=expediente)
    return db_expediente

@router.get("/expedientes/", response_model=list[Expediente])
def obtener_expedientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    expedientes = get_expedientes(db, skip=skip, limit=limit)
    return expedientes

@router.get("/expedientes/{id_expediente}", response_model=Expediente)
def obtener_expediente_por_id(id_expediente: int, db: Session = Depends(get_db)):
    db_expediente = get_expediente_by_id(db, id_expediente=id_expediente)
    if db_expediente is None:
        raise HTTPException(status_code=404, detail="El ID del expediente no existe")
    return db_expediente

@router.get("/expedientes/paciente/{id_paciente}", response_model=Expediente)
def obtener_expediente_por_id_paciente(id_paciente: int, db: Session = Depends(get_db)):
    db_expediente = get_expediente_by_id_paciente(db, id_paciente=id_paciente)
    if db_expediente is None:
        raise HTTPException(status_code=404, detail="No se encontró ningún expediente para el ID del paciente")
    return db_expediente

@router.put("/expedientes/{id_expediente}", response_model=Expediente)
def actualizar_expediente(
    id_expediente: int, expediente_update: ExpedienteUpdate, db: Session = Depends(get_db)
):
    db_expediente = get_expediente_by_id(db, id_expediente=id_expediente)
    if db_expediente is None:
        raise HTTPException(status_code=404, detail="El ID del expediente no existe")
    if expediente_update.id_paciente:
        db_paciente = get_paciente_by_id(db, id_paciente=expediente_update.id_paciente)
        if db_paciente is None:
            raise HTTPException(status_code=404, detail="El ID del paciente no existe")
 
    db_expediente = update_expediente(db, db_expediente, expediente_update)
    return db_expediente

@router.delete("/expedientes/{id_expediente}", response_model=Expediente)
def eliminar_expediente(id_expediente: int, db: Session = Depends(get_db)):
    db_expediente = get_expediente_by_id(db, id_expediente=id_expediente)
    if db_expediente is None:
        raise HTTPException(status_code=404, detail="El ID del expediente no existe")
    delete_expediente(db, db_expediente)
    return db_expediente
