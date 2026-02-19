from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.file import File
from app.services.file_service import delete_file_from_b2, download_file_from_b2, upload_file_to_b2

router = APIRouter(prefix="/folder", tags=["folder"])
# Subir archivo
@router.post("/{folder_id}/upload")
def upload_file(folder_id: str, file: UploadFile, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    
    file_upload = upload_file_to_b2(folder_id=folder_id, file=file, db=db, user_id=current_user.id)
    return {"message": "Archivo subido exitosamente", "file": file_upload}


# Descargar archivo
@router.get("/{file_id}/download")
def download_file(file_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    print(file_id)
    file = db.query(File).filter(File.id == file_id, File.user_id == current_user.id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    print(file.path)
    download_url = download_file_from_b2(file.path)
    return {"download_url": download_url}


# Borrar archivo
@router.delete("/")
def delete_file(file_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    file = db.query(File).filter(File.id == file_id, File.user_id == current_user.id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    db.delete(file)
    db.commit()

    delete_file_from_b2(file.path)  
    return {"message": "Archivo eliminado exitosamente"}

# Mover archivo a otra carpeta
# Renombrar archivo
# Compartir archivo con otro usuario
# Obtener detalles de un archivo
