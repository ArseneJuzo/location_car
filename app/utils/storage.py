import os
import uuid

from fastapi import HTTPException, UploadFile, status

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
VEHICULES_DIR = os.path.join(UPLOAD_DIR, "vehicules")

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 Mo

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


def save_vehicule_image(file: UploadFile, previous_url: str | None = None) -> str:
    """Enregistre l'image sur disque et retourne son URL relative (/static/...).

    Le nom de fichier est généré côté serveur (uuid) : jamais dérivé du nom
    fourni par le client, pour éviter tout risque de traversée de chemin.
    """
    extension = ALLOWED_CONTENT_TYPES.get(file.content_type)
    if not extension:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="format d'image non supporté (jpeg, png ou webp uniquement)",
        )

    content = file.file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="image trop volumineuse (5 Mo maximum)",
        )

    os.makedirs(VEHICULES_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{extension}"
    filepath = os.path.join(VEHICULES_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    _delete_local_image(previous_url)
    return f"/static/vehicules/{filename}"


def _delete_local_image(url: str | None) -> None:
    if not url or not url.startswith("/static/vehicules/"):
        return
    filepath = os.path.join(UPLOAD_DIR, url.removeprefix("/static/"))
    try:
        if os.path.commonpath([filepath, VEHICULES_DIR]) == VEHICULES_DIR and os.path.isfile(filepath):
            os.remove(filepath)
    except (OSError, ValueError):
        pass
