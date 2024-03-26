from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import PacienteCreate, PacienteUpdate
from models.models import Paciente as models

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
  
def create_paciente(db: Session, paciente: PacienteCreate):
        db_paciente = models(**paciente.model_dump())
        db.add(db_paciente)
        db.commit()
        db.refresh(db_paciente)
        return (db_paciente)


def get_paciente_by_id(db: Session, id_paciente: int):
    return db.query(models).filter(models.id_paciente == id_paciente).first()


def get_pacientes(db: Session, skip = 0, limit: int = 100):
    return db.query(models).offset(skip).limit(limit).all()


def update_paciente(db: Session, paciente: models, paciente_update:PacienteUpdate):
    for key, value in paciente_update.dict().items():
        setattr(paciente, key, value)
    db.commit()
    db.refresh(paciente)
    return paciente


def delete_paciente(db: Session, paciente: models):
    db.delete(paciente)
    db.commit()
    return paciente
