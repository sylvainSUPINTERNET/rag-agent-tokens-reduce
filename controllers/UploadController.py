
import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/upload", tags=["upload"])

# Config Azure
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER")

# Types autorisés
ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
}

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 Mo


def get_blob_service_client() -> Optional[BlobServiceClient]:
    """Initialise le client Azure Blob."""
    if not AZURE_CONNECTION_STRING:
        return None
    try:
        return BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    except Exception:
        return None


def validate_file(file: UploadFile) -> None:
    """Valide le type et la taille du fichier."""
    # Vérification du type MIME
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de fichier non autorisé: {file.content_type}. Types acceptés: PDF, PNG, JPEG, WebP"
        )
    
    # Vérification de la taille (via headers)
    content_length = file.headers.get("content-length")
    if content_length and int(content_length) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fichier trop volumineux. Taille max: {MAX_FILE_SIZE // (1024*1024)} Mo"
        )


async def upload_to_azure(file: UploadFile) -> str:
    """Upload le fichier vers Azure Blob Storage."""
    blob_service = get_blob_service_client()
    if not blob_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage non configuré"
        )
    
    # Génère un nom unique pour éviter les collisions
    ext = ALLOWED_MIME_TYPES[file.content_type]  # type: ignore
    unique_name = f"{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4()}{ext}"
    
    container_client = blob_service.get_container_client(AZURE_CONTAINER_NAME)  # type: ignore
    blob_client = container_client.get_blob_client(unique_name)
    
    # Upload direct (FastAPI buffering déjà le fichier en temp)
    content = await file.read()
    
    blob_client.upload_blob(
        content,
        overwrite=True,
        content_settings=ContentSettings(content_type=file.content_type)
    )
    
    return blob_client.url


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload un fichier (PDF, PNG, JPEG, WebP) vers Azure Blob Storage.
    
    - Taille max: 100 Mo
    - Types: PDF, PNG, JPEG, WebP
    - FastAPI buffering automatique en temp (pas de chunking manuel)
    """
    # Validation
    validate_file(file)
    
    # Upload vers Azure
    url = await upload_to_azure(file)
    
    return {
        "status": "success",
        "filename": file.filename,
        "content_type": file.content_type,
        "url": url
    }


@router.get("/")
async def index():
    """Health check du controller."""
    return {
        "status": "ok",
        "message": "UploadController actif",
        "allowed_types": list(ALLOWED_MIME_TYPES.keys()),
        "max_size_mb": MAX_FILE_SIZE // (1024 * 1024)
    }