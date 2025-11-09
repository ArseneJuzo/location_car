from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .utilisateur import Utilisateur
from .vehicule import Vehicule
from .reservation import Reservation
from .paiement import Paiement
from .avis import Avis
from .agence import Agence
