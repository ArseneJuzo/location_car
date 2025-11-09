from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from . import Base


class Paiement(Base):
    __tablename__ = 'paiement'

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey('reservation.id'))
    montant = Column(Float, nullable=False)
    statut = Column(String(50), default="en_attente")
    methode = Column(String(50))
    date_paiement = Column(DateTime, default=datetime.utcnow)

    # Relations
    reservation = relationship('Reservation', back_populates='paiement')

    # Règles métier
    @validates('montant')
    def valider_montant(self, key, montant):
        assert montant > 0, "Le montant du paiement doit être supérieur à zéro."
        return montant
