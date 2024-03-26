from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from config.database import Base

class Paciente(Base):
    __tablename__ = "pacientes"
    
    id_paciente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, index=True)
    edad = Column(Integer)
    telefono = Column(String)
    genero = Column(String)
    ocupacion = Column(String)
    
    expedientes = relationship("Expediente", back_populates="pacientes",  cascade="all, delete-orphan")
    
    
class Expediente(Base):
    __tablename__ = "expedientes"
    
    id_expediente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_modificacion = Column(Date)
    datos = Column(String)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"))
    
    pacientes = relationship("Paciente", back_populates="expedientes")