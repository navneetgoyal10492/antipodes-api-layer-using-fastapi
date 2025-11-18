# api/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
from pathlib import Path
from typing import List

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()

@router.post("/uploadExcelFiles", summary="Upload Excel files")
async def uploadExcelFiles(files: List[UploadFile] = File(...)):
    file_names = []

    # Looping through all the files and upload one by one
    for f in files:
        # Validate extensions
        if not f.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(status_code=400, detail=f"{f.filename} is not a valid Excel file")

        # Save file locally
        file_path = UPLOAD_DIR / f"{f.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)

        file_names.append(f.filename)

    return {"message": "Files uploaded successfully", "loaded_files": file_names}
