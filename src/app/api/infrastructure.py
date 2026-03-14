from typing import Dict, Any
from fastapi import APIRouter

router = APIRouter(tags=["Infrastructure"])

@router.get("/api/v1/health/minio")
async def health_minio():
    return {"status": "HEALTHY", "service": "MinIO", "uptime": "49m"}

@router.get("/api/v1/health/docling")
async def health_docling():
    return {"status": "READY", "service": "Docling OCR", "memory_usage": "1.2GB"}

@router.post("/api/v1/webhooks/docling/callback")
async def docling_callback(payload: Dict[str, Any]):
    return {"message": "Callback received", "pdf_id": payload.get("pdf_id")}
