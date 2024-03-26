from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import Paciente, PacienteCreate, PacienteUpdate
from crud.paciente_crud import create_paciente, get_pacientes, get_paciente_by_id, update_paciente, delete_paciente


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/pacientes/", response_model=Paciente)
def agregar_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    db_paciente = create_paciente(db=db, paciente=paciente)
    return db_paciente


@router.get("/pacientes/", response_model=list[Paciente])
def obtener_pacientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pacientes = get_pacientes(db, skip=skip, limit=limit)
    return pacientes


@router.get("/pacientes/{id_paciente}", response_model=Paciente)
def obtener_paciente_por_id(id_paciente: int, db: Session = Depends(get_db)):
    db_paciente = get_paciente_by_id(db, id_paciente=id_paciente)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="El ID del paciente no existe")
    return db_paciente


@router.put("/pacientes/{id_paciente}", response_model=Paciente)
def actualizar_paciente(
    id_paciente: int, paciente_update: PacienteUpdate, db: Session = Depends(get_db)
):
    db_paciente = get_paciente_by_id(db, id_paciente=id_paciente)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="El ID del paciente no existe")
    db_paciente = update_paciente(db, db_paciente, paciente_update)
    return db_paciente


@router.delete("/pacientes/{id_paciente}", response_model=Paciente)
def eliminar_paciente(id_paciente: int, db: Session = Depends(get_db)):
    db_paciente = get_paciente_by_id(db, id_paciente=id_paciente)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="El ID del paciente no existe")
    else:
        db_paciente = delete_paciente(db, db_paciente)
        return db_paciente

