"""
Peuple la base avec des données réalistes pour le contexte camerounais
(agences, véhicules, clients à Douala, Yaoundé, Bafoussam, Garoua).

Usage (depuis la racine du projet, venv activé) :
    python -m scripts.seed_data
"""
from datetime import date, timedelta

from app.db.session import session_local
from app.core.security import get_password_hash
from app.models.utilisateur import Utilisateur, RoleUtilisateur
from app.models.agence import Agence
from app.models.vehicule import Vehicule, StatutVehicule, CategorieLocation
from app.models.reservation import Reservation, StatutReservation
from app.models.paiement import Paiement
from app.models.avis import Avis

MOT_DE_PASSE_PAR_DEFAUT = "Cameroun@2024"


def get_or_create_user(db, *, email, nom_complet, telephone, role):
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if user:
        return user, False
    user = Utilisateur(
        nom_complet=nom_complet,
        telephone=telephone,
        email=email,
        hashed_password=get_password_hash(MOT_DE_PASSE_PAR_DEFAUT),
        role=role,
    )
    db.add(user)
    db.flush()
    return user, True


def get_or_create_agence(db, *, nom_agence, adresse, ville, pays, telephone, email, responsable_id,
                          latitude=None, longitude=None):
    agence = db.query(Agence).filter(Agence.nom_agence == nom_agence).first()
    if agence:
        return agence, False
    agence = Agence(
        nom_agence=nom_agence,
        adresse=adresse,
        ville=ville,
        pays=pays,
        telephone=telephone,
        email=email,
        responsable_id=responsable_id,
        latitude=latitude,
        longitude=longitude,
    )
    db.add(agence)
    db.flush()
    return agence, True


def get_or_create_vehicule(db, *, immatriculation, agence_id, **kwargs):
    vehicule = db.query(Vehicule).filter(Vehicule.immatriculation == immatriculation).first()
    if vehicule:
        return vehicule, False
    vehicule = Vehicule(immatriculation=immatriculation, agence_id=agence_id, **kwargs)
    db.add(vehicule)
    db.flush()
    agence = db.query(Agence).filter(Agence.id == agence_id).first()
    agence.nombre_vehicule_total = (agence.nombre_vehicule_total or 0) + 1
    agence.nombre_vehicule_disponibles = (agence.nombre_vehicule_disponibles or 0) + 1
    return vehicule, True


def seed():
    db = session_local()
    created = {"users": 0, "agences": 0, "vehicules": 0, "reservations": 0, "paiements": 0, "avis": 0}

    try:
        # --- Administrateur ---
        admin, is_new = get_or_create_user(
            db,
            email="admin@locationcar.cm",
            nom_complet="Admin Système",
            telephone="+237699000000",
            role=RoleUtilisateur.administrateur,
        )
        created["users"] += is_new

        # --- Responsables d'agence (rôle "agence") ---
        responsables_data = [
            dict(email="serge.fotso@doualauto.cm", nom_complet="Serge Fotso Nkeng", telephone="+237699001122"),
            dict(email="aicha.oumarou@237rentcar.cm", nom_complet="Aïcha Oumarou Bello", telephone="+237677223344"),
            dict(email="jp.mbarga@westdrive.cm", nom_complet="Jean-Paul Mbarga Owona", telephone="+237655334455"),
            dict(email="fatimatou.abdoulaye@grandnordauto.cm", nom_complet="Fatimatou Abdoulaye", telephone="+237691445566"),
        ]
        responsables = []
        for data in responsables_data:
            user, is_new = get_or_create_user(db, role=RoleUtilisateur.agence, **data)
            created["users"] += is_new
            responsables.append(user)

        # --- Clients ---
        clients_data = [
            dict(email="marie.ateba@gmail.com", nom_complet="Marie-Claire Ateba Mballa", telephone="+237677001122"),
            dict(email="christian.njoya@gmail.com", nom_complet="Christian Njoya Talla", telephone="+237691223344"),
            dict(email="brenda.nguetsop@gmail.com", nom_complet="Brenda Nguetsop Kamdem", telephone="+237655667788"),
            dict(email="emmanuel.onana@gmail.com", nom_complet="Emmanuel Onana Etoundi", telephone="+237699887766"),
            dict(email="aminatou.bello@gmail.com", nom_complet="Aminatou Bello Oumarou", telephone="+237678990011"),
        ]
        clients = []
        for data in clients_data:
            user, is_new = get_or_create_user(db, role=RoleUtilisateur.client, **data)
            created["users"] += is_new
            clients.append(user)

        db.commit()

        # --- Agences ---
        agences_data = [
            dict(
                nom_agence="Doual'Auto Location",
                adresse="Akwa, Boulevard de la Liberté",
                ville="Douala",
                pays="Cameroun",
                telephone="+237699001122",
                email="contact@doualauto.cm",
                responsable_id=responsables[0].id,
                latitude=4.0511,
                longitude=9.7679,
            ),
            dict(
                nom_agence="237 Rent Car",
                adresse="Bastos, Avenue Kennedy",
                ville="Yaoundé",
                pays="Cameroun",
                telephone="+237677223344",
                email="contact@237rentcar.cm",
                responsable_id=responsables[1].id,
                latitude=3.8480,
                longitude=11.5021,
            ),
            dict(
                nom_agence="West Drive Location",
                adresse="Marché A, Route de Bafoussam",
                ville="Bafoussam",
                pays="Cameroun",
                telephone="+237655334455",
                email="contact@westdrive.cm",
                responsable_id=responsables[2].id,
                latitude=5.4737,
                longitude=10.4172,
            ),
            dict(
                nom_agence="Grand Nord Auto",
                adresse="Quartier Plateau",
                ville="Garoua",
                pays="Cameroun",
                telephone="+237691445566",
                email="contact@grandnordauto.cm",
                responsable_id=responsables[3].id,
                latitude=9.3265,
                longitude=13.3958,
            ),
        ]
        agences = []
        for data in agences_data:
            agence, is_new = get_or_create_agence(db, **data)
            created["agences"] += is_new
            agences.append(agence)

        db.commit()

        # --- Véhicules ---
        vehicules_data = [
            # Doual'Auto Location (Douala)
            dict(immatriculation="LT-2245-AB", agence_id=agences[0].id, marque="Toyota", modele="Corolla",
                 prix_journalier=25000, carburant="essence", categorie=CategorieLocation.compacte,
                 nombres_places=5, boite_vitesse="automatique"),
            dict(immatriculation="LT-3391-CK", agence_id=agences[0].id, marque="Toyota", modele="Hilux",
                 prix_journalier=42000, carburant="diesel", categorie=CategorieLocation.suv,
                 nombres_places=5, boite_vitesse="manuelle"),
            dict(immatriculation="LT-4108-DZ", agence_id=agences[0].id, marque="Toyota", modele="Land Cruiser Prado",
                 prix_journalier=60000, carburant="diesel", categorie=CategorieLocation.luxe,
                 nombres_places=7, boite_vitesse="automatique"),
            # 237 Rent Car (Yaoundé)
            dict(immatriculation="CE-1187-BD", agence_id=agences[1].id, marque="Hyundai", modele="Elantra",
                 prix_journalier=27000, carburant="essence", categorie=CategorieLocation.compacte,
                 nombres_places=5, boite_vitesse="automatique"),
            dict(immatriculation="CE-1523-EF", agence_id=agences[1].id, marque="Hyundai", modele="Tucson",
                 prix_journalier=40000, carburant="essence", categorie=CategorieLocation.suv,
                 nombres_places=5, boite_vitesse="automatique"),
            dict(immatriculation="CE-1974-GH", agence_id=agences[1].id, marque="Kia", modele="Picanto",
                 prix_journalier=15000, carburant="essence", categorie=CategorieLocation.economique,
                 nombres_places=4, boite_vitesse="manuelle"),
            # West Drive Location (Bafoussam)
            dict(immatriculation="OU-0453-CT", agence_id=agences[2].id, marque="Kia", modele="Sportage",
                 prix_journalier=38000, carburant="diesel", categorie=CategorieLocation.suv,
                 nombres_places=5, boite_vitesse="automatique"),
            dict(immatriculation="OU-0812-JK", agence_id=agences[2].id, marque="Peugeot", modele="508",
                 prix_journalier=35000, carburant="diesel", categorie=CategorieLocation.compacte,
                 nombres_places=5, boite_vitesse="automatique"),
            # Grand Nord Auto (Garoua)
            dict(immatriculation="NO-0912-GR", agence_id=agences[3].id, marque="Suzuki", modele="Jimny",
                 prix_journalier=30000, carburant="essence", categorie=CategorieLocation.suv,
                 nombres_places=4, boite_vitesse="manuelle"),
            dict(immatriculation="NO-1187-LM", agence_id=agences[3].id, marque="Toyota", modele="RAV4",
                 prix_journalier=45000, carburant="essence", categorie=CategorieLocation.suv,
                 nombres_places=5, boite_vitesse="automatique"),
        ]
        vehicules = []
        for data in vehicules_data:
            vehicule, is_new = get_or_create_vehicule(db, **data)
            created["vehicules"] += is_new
            vehicules.append(vehicule)

        db.commit()

        # --- Réservations + paiement + avis d'exemple ---
        if not db.query(Reservation).filter(Reservation.utilisateur_id == clients[0].id,
                                             Reservation.vehicule_id == vehicules[0].id).first():
            reservation_terminee = Reservation(
                utilisateur_id=clients[0].id,
                vehicule_id=vehicules[0].id,
                date_debut=date.today() - timedelta(days=10),
                date_fin=date.today() - timedelta(days=6),
                montant_total=4 * vehicules[0].prix_journalier,
                statut=StatutReservation.terminée,
            )
            db.add(reservation_terminee)
            db.flush()
            created["reservations"] += 1

            db.add(Paiement(
                reservation_id=reservation_terminee.id,
                montant=reservation_terminee.montant_total,
                statut="valide",
                methode="orange_money",
            ))
            created["paiements"] += 1

            db.add(Avis(
                utilisateur_id=clients[0].id,
                vehicule_id=vehicules[0].id,
                note=5,
                commentaire="Excellent service, voiture propre et agence très réactive à Douala.",
            ))
            created["avis"] += 1

        if not db.query(Reservation).filter(Reservation.utilisateur_id == clients[1].id,
                                             Reservation.vehicule_id == vehicules[4].id).first():
            reservation_en_attente = Reservation(
                utilisateur_id=clients[1].id,
                vehicule_id=vehicules[4].id,
                date_debut=date.today() + timedelta(days=3),
                date_fin=date.today() + timedelta(days=7),
                montant_total=4 * vehicules[4].prix_journalier,
                statut=StatutReservation.en_attente,
            )
            db.add(reservation_en_attente)
            created["reservations"] += 1

        db.commit()

        print("Seed terminé.")
        print(f"  Utilisateurs créés : {created['users']}")
        print(f"  Agences créées     : {created['agences']}")
        print(f"  Véhicules créés    : {created['vehicules']}")
        print(f"  Réservations créées: {created['reservations']}")
        print(f"  Paiements créés    : {created['paiements']}")
        print(f"  Avis créés         : {created['avis']}")
        print(f"\nMot de passe commun à tous les comptes créés : {MOT_DE_PASSE_PAR_DEFAUT}")
        print("Comptes : admin@locationcar.cm (administrateur), serge.fotso@doualauto.cm (agence), "
              "marie.ateba@gmail.com (client), etc.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
