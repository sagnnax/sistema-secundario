from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import ExpedienteCreate, ExpedienteUpdate
from models.models import Expediente as models
from models.models import Paciente as paciente_model

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_expediente(db: Session, expediente: ExpedienteCreate):
    db_expediente = models(**expediente.model_dump())
    db.add(db_expediente)
    db.commit()
    db.refresh(db_expediente)
    return db_expediente

def get_expediente_by_id(db: Session, id_expediente: int):
    return db.query(models).filter(models.id_expediente == id_expediente).first()

def get_expediente_by_id_paciente(db: Session, id_paciente: int):
    return db.query(models).filter(models.id_paciente == id_paciente).first()

def get_expedientes(db: Session, skip=0, limit: int = 100):
    return db.query(models).offset(skip).limit(limit).all()

def update_expediente(db: Session, expediente: models, expediente_update: ExpedienteUpdate):
    for key, value in expediente_update.dict().items():
        setattr(expediente, key, value)
    db.commit()
    db.refresh(expediente)
    return expediente

def delete_expediente(db: Session, expediente: models):
    db.delete(expediente)
    db.commit()
