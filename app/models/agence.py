from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from . import Base


class Agence(Base):
    __tablename__ = 'agence'

    id = Column(Integer, primary_key=True, index=True)
    nom_agence = Column(String(150), nullable=False)
    adresse = Column(String(255), nullable=False)
    ville = Column(String(100))
    pays = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    telephone = Column(String(50))
    email = Column(String(150))
    nombre_vehicule_disponibles = Column(Integer, default=0)
    nombre_vehicule_total = Column(Integer, default=0)
    nombre_reservation = Column(Integer, default=0)
    date_creation = Column(DateTime, default=datetime.utcnow)
    notes = Column(Float, default=0)
    total_avis = Column(Integer, default=0)
    responsable_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=True)

    # Relations
    vehicule = relationship('Vehicule', back_populates='agence')
    responsable = relationship('Utilisateur', back_populates='agences_gerees')

    @validates('email')
    def valider_email(self, key, email):
        if email is not None:
            assert "@" in email, "adresse email invalide"
        return email

    @validates('telephone')
    def valider_telephone(self, key, telephone):
        if telephone is not None:
            assert telephone.lstrip("+").isdigit(), "numero de telephone incorrect"
        return telephone
