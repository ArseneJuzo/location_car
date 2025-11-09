from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from . import Base


class Agence(Base):
    __tablename__ = 'agence'

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(150), nullable=False)
    adresse = Column(String(255), nullable=False)
    ville = Column(String(100))
    pays = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    telephone = Column(String(50))
    email = Column(String(150))

    # Relations
    vehicule = relationship('Vehicule', back_populates='agence')
