from datetime import date
from pydantic import BaseModel

### Pacientes

class PacienteBase(BaseModel):
    nombre: str | None=None
    edad: int | None=None
    telefono: str | None=None
    genero: str | None=None
    ocupacion: str | None=None
    
class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(PacienteBase):
    pass

class Paciente(PacienteBase):
    id_paciente: int | None=None
    
    class Config:
        from_attributes = True
    

### Expedientes

class ExpedienteBase(BaseModel):
    fecha_modificacion: date | None=None
    datos: str | None=None
    id_paciente: int 
    
class ExpedienteCreate(ExpedienteBase):
    pass

class ExpedienteUpdate(ExpedienteBase):
    pass

class Expediente(ExpedienteBase):
    id_expediente: int | None=None
    
    class Config:
        from_attributes = True