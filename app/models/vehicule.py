from enum import Enum
from sqlalchemy import Column, Integer, Float, String, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from . import Base

class StatutVehicule(Enum):
    disponible = "disponible"
    en_location = "en_location"
    maintenance = "maintenance"

class Vehicule(Base):
    __tablename__ = "vehicule"

    id = Column(Integer, primary_key=True)
    marque = Column(String(255), nullable=False)
    modele = Column(String(255), nullable=False)
    immatriculation = Column(String(255), unique=True, nullable=False)
    prix_journalier = Column(Float, nullable=False)
    carburant = Column(String(50))
    nombres_places = Column(Integer)
    boite_vitesse = Column(String(50))
    statut = Column(SQLEnum(StatutVehicule, name="statut_vehicule_enum"), default=StatutVehicule.disponible)
    image_url = Column(String(255))

    agence_id = Column(Integer, ForeignKey('agence.id'))
    agence = relationship('Agence', back_populates='vehicule')
    reservation = relationship('Reservation', back_populates='vehicule')
    avis = relationship('Avis', back_populates='vehicule')
