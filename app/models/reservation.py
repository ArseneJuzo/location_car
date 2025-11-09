from enum import Enum
from sqlalchemy import Column, Integer, Date, Float, ForeignKey, String, Enum as SQLEnum, CheckConstraint
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from app.models.vehicule import StatutVehicule
from . import Base


class StatutReservation(Enum):
    en_attente = "en_attente"
    confirmée = "confirmée"
    annulée = "annulée"
    terminée = "terminée"


class Reservation(Base):
    __tablename__="reservation"
    id = Column(Integer, primary_key=True)
    utilisateur_id = Column(Integer, ForeignKey('utilisateur.id'))
    vehicule_id = Column(Integer, ForeignKey('vehicule.id'))
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    montant_total = Column(Float, nullable=False)
    statut = Column(SQLEnum(StatutReservation, name="statut_reservation_enum"), default=StatutReservation.en_attente)

     # Relations
    utilisateur = relationship('Utilisateur', back_populates='reservation')
    vehicule = relationship('Vehicule', back_populates='reservation')
    paiement = relationship('Paiement', back_populates='reservation', uselist=False)

    # Contraintes et règles métier
    __table_args__ = (
        CheckConstraint('montant_total >= 0', name='montant_positif'),
    )

    @validates('date_fin')
    def valider_dates(self, key, date_fin):
        assert date_fin > self.date_debut, "La date de fin doit être postérieure à la date de début."
        return date_fin

    @validates('vehicule')
    def valider_vehicule(self, key, vehicule):
        assert vehicule.statut == StatutVehicule.disponible, "Le véhicule n'est pas disponible à la réservation."
        return vehicule

