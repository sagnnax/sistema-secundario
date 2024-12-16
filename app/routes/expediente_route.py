from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import Expediente, ExpedienteCreate, ExpedienteUpdate
from crud.expediente_crud import create_expediente, get_expedientes, get_expediente_by_id, update_expediente, delete_expediente, get_expediente_by_id_paciente
from crud.paciente_crud import get_paciente_by_id
from typing import Any, Dict
import requests

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
FHIR_SERVER_URL = "http://localhost:8080/fhir"

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

def fetch_resource(resource_type: str, patient_id: str) -> Dict[str, Any]:
    url = f"{FHIR_SERVER_URL}/{resource_type}?patient={patient_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "entry" not in data:
            data["entry"] = [] 
        return data
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Error en la solicitud de {resource_type}")

def get_patient_id_by_name(name: str) -> str:
    url = f"{FHIR_SERVER_URL}/Patient?given={name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['total'] > 0:
            return data['entry'][0]['resource']['id']
        else:
            raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=response.status_code, detail="Error al buscar el paciente")
    
@router.get("/get_expediente_fhir/{name}")
async def get_patient_resources_by_name(name: str):
    try:
        patient_id = get_patient_id_by_name(name)
        
        observation = fetch_resource("Observation", patient_id)
        condition = fetch_resource("Condition", patient_id)
        procedure = fetch_resource("Procedure", patient_id)
        medication_statement = fetch_resource("MedicationStatement", patient_id)
        
        formatted_data = {
            "Patient name": name,
            "Observation": [
                {
                    "id":f'{entry["resource"]["id"]}' ,
                    "value": entry["resource"].get("valueString", ""),
                }
                for entry in observation.get("entry",[])
                ],
            "Condition": [
                {
                    "id": entry["resource"]["id"],
                    "description": entry["resource"].get("code", {}).get("text", "")
                }
                for entry in condition.get("entry", [])
            ],
            "Procedure": [
                {
                    "id": entry["resource"]["id"],
                    "description": entry["resource"].get("code", {}).get("text", ""),
                }
                for entry in procedure.get("entry", [])
            ],
            "MedicationStatement": [
                {
                    "id": entry["resource"]["id"],
                    "dosage": entry["resource"].get("dosage", [{}])[0].get("text", "")
                }
                for entry in medication_statement.get("entry", [])
            ]
        }
        
        return {
            "PatientID": patient_id,
            "Observations": formatted_data["Observation"],
            "Conditions": formatted_data["Condition"],
            "Procedures": formatted_data["Procedure"],
            "MedicationStatements": formatted_data["MedicationStatement"],
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

