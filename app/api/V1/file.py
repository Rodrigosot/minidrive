import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.file import File
from app.schemas.file import FileRename
from app.services.file_service import delete_file_from_b2, download_file_from_b2, upload_file_to_b2

router = APIRouter(prefix="/file", tags=["file"])
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
@router.put("/move")
def move_file(file_id: uuid.UUID, new_folder_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Implementar logica mover archivo

    file = db.query(File).filter(File.id == file_id, File.user_id==current_user.id).first()

    if not file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    file.folder_id = new_folder_id

    db.commit()

    return {"message": "file moved successfully"}

# Renombrar archivo
@router.put("/rename")
def rename_file(request:Request ,fileResponse: FileRename, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    #logica renombrar archivo

    file = db.query(File).filter(File.id == fileResponse.id, File.user_id==current_user.id).first()  
    if not file:
        raise HTTPException(status_code=404, detail="file not found")

    new_file = File(
        folder_id = file.folder_id,
        name = file.name,
        size = file.size,
        mime_type = file.mime_type,
    )

    file.name = fileResponse.name 
    db.commit()

    return {"message": "File renamed successfully", "file": new_file, "file2xd": file}


# Obtener detalles de un archivo
@router.get("/{file_id}")
def get_file(file_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    file= db.query(File).filter(File.id== file_id, File.user_id == current_user.id).first()
    

    if not file:
        raise HTTPException(status_code=404, detail="file not found")
    
    new_file = new_file = File(
        folder_id = file.folder_id,
        name = file.name,
        size = file.size,
        mime_type = file.mime_type,
    )

    return {"file": file}
    ""


# Compartir archivo con otro usuario



