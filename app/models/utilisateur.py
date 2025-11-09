from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime,DATE, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from . import Base


class RoleUtilisateur(Enum):
    client = "client"
    agence = "agence"
    administrateur = "administrateur"

class Utilisateur(Base):
    __tablename__="utilisateur"
    id = Column(Integer, primary_key=True, index=True)
    nom_complet = Column(String(255), nullable=False)
    telephone = Column(String(50))
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleUtilisateur, name="role_utilisateur_enum"), default=RoleUtilisateur.client)
    date_creation = Column(DateTime, default=datetime.utcnow)
    reset_token = Column(String(155), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    est_actif = Column(Boolean, default=True)


    reservation = relationship('Reservation', back_populates='utilisateur')
    avis = relationship('Avis', back_populates='utilisateur')
    

    @validates('email')
    def valider_champ(self, key, email):
        if key == 'email':
            assert "@" in email, "adresse email invalide"
        return email      


    @validates('telephone')
    def valider_champ(self, key, telephone):
        if key == 'telephone':
            assert telephone.lstrip("+").isdigit(), "numero de telephone incorrect"
        return telephone                                    