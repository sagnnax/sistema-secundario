from fastapi import APIRouter, Depends, HTTPException
import requests
from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import Paciente, PacienteCreate, PacienteUpdate
from crud.paciente_crud import create_paciente, get_pacientes, get_paciente_by_id, update_paciente, delete_paciente
from datetime import datetime



router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
FHIR_SERVER_URL = "http://localhost:8080/fhir/Patient"

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
    
@router.get("/patient/")
def get_patient_by_full_name(name: str):
    response = requests.get(f"{FHIR_SERVER_URL}?given={name}")
    if response.status_code == 200:
        data = response.json()
        if data['total'] > 0:
            patient = data['entry'][0]['resource']
            birth_date = patient.get('birthDate', None)
            age = None
            if birth_date:
                birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
                today = datetime.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            gender = patient.get('gender', "")
            if gender == "male":
                gender = "M"
            elif gender == "female":
                gender = "F"
                  
            return {
                "name": patient['name'][0]['given'][0],
                "occupation": patient.get('extension', [{}])[0].get('valueString', ""),
                "gender": gender,
                "age": age,
                "phone": patient.get('telecom', [{}])[0].get('value', "")
            }
            
    return {"error": "Patient not found"}