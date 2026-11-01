import os
import hashlib
import uuid
import re
from typing import Tuple, Optional, Dict, Any, Union
from fastapi import HTTPException, UploadFile
from backend.app.core.config import settings

ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".png", ".jpg", ".jpeg"
}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "text/csv",
    "text/plain",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "application/octet-stream"
}

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


class SavedFileResult(dict):
    """Result object supporting both dict access and tuple unpacking."""
    def __iter__(self):
        yield self["absolute_path"]
        yield self["file_name"]
        yield self["file_size_bytes"]
        yield self["content_hash"]


class StorageService:
    def __init__(self, base_dir: str = settings.STORAGE_DIR):
        self.base_dir = os.path.abspath(base_dir)
        self.subdirs = {
            "resumes": os.path.join(self.base_dir, "resumes"),
            "application_documents": os.path.join(self.base_dir, "application_documents"),
            "institutional_documents": os.path.join(self.base_dir, "institutional_documents"),
            "profile_assets": os.path.join(self.base_dir, "profile_assets"),
            "temporary": os.path.join(self.base_dir, "temporary"),
        }
        for path in self.subdirs.values():
            os.makedirs(path, exist_ok=True)

    def validate_file(self, filename: str, content: bytes, content_type: str = ""):
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="File exceeds maximum allowed size of 25MB.")
        
        _, ext = os.path.splitext(filename.lower())
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

    def sanitize_filename(self, filename: str) -> str:
        base_name = os.path.basename(filename)
        clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', base_name)
        return clean

    def calculate_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    async def save_file(
        self,
        folder_category: Optional[str] = None,
        filename: Optional[str] = None,
        content: Optional[bytes] = None,
        upload_file: Optional[UploadFile] = None,
        subfolder: Optional[str] = None,
    ) -> SavedFileResult:
        """
        Saves file content safely to local storage.
        Supports both direct byte input and FastAPI UploadFile.
        """
        category = subfolder or folder_category or "temporary"
        target_dir = self.subdirs.get(category, self.subdirs["temporary"])

        if upload_file is not None:
            raw_content = await upload_file.read()
            raw_filename = upload_file.filename or "upload.bin"
            content_type = upload_file.content_type or "application/octet-stream"
        else:
            raw_content = content or b""
            raw_filename = filename or "upload.bin"
            content_type = "application/octet-stream"

        self.validate_file(raw_filename, raw_content, content_type)

        clean_name = self.sanitize_filename(raw_filename)
        _, ext = os.path.splitext(clean_name)
        unique_prefix = str(uuid.uuid4())[:8]
        stored_filename = f"{unique_prefix}_{clean_name}"
        destination = os.path.join(target_dir, stored_filename)

        real_dest = os.path.abspath(destination)
        if not real_dest.startswith(target_dir):
            raise HTTPException(status_code=400, detail="Invalid file destination path traversal detected.")

        with open(destination, "wb") as f:
            f.write(raw_content)

        file_hash = self.calculate_hash(raw_content)
        file_size = len(raw_content)

        return SavedFileResult({
            "absolute_path": destination,
            "file_name": clean_name,
            "storage_rel_path": destination,
            "file_size_bytes": file_size,
            "content_hash": file_hash,
            "mime_type": content_type,
            "file_extension": ext
        })

    def get_file_path(self, relative_or_absolute_path: str) -> str:
        real_path = os.path.abspath(relative_or_absolute_path)
        if not real_path.startswith(self.base_dir):
            raise HTTPException(status_code=403, detail="Access denied: file outside storage boundary.")
        if not os.path.exists(real_path):
            raise HTTPException(status_code=404, detail="Requested file not found in storage.")
        return real_path


storage_service = StorageService()
