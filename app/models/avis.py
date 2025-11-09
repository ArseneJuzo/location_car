from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from . import Base

class Avis(Base):
    __tablename__ = 'avis'

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey('utilisateur.id'))
    vehicule_id = Column(Integer, ForeignKey('vehicule.id'))
    note = Column(Integer, nullable=False)
    commentaire = Column(Text)
    date_creation = Column(DateTime, default=datetime.utcnow)

    # Relations
    utilisateur = relationship('Utilisateur', back_populates='avis')
    vehicule = relationship('Vehicule', back_populates='avis')

    # Règles métier
    @validates('note')
    def valider_note(self, key, note):
        assert 1 <= note <= 5, "La note doit être comprise entre 1 et 5."
        return note