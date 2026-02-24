import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.file import File
from app.models.user import User
from app.schemas.file import FileRename, ShareFileSchema
from app.models.fileshare import FileShare
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

    ## Solo puede descargar el archivo el owner, modificar para shares
    ## Crear funcion get_accesible_file, para evitar reutilizar codigo xd
    print(file_id)
    file = db.query(File).filter(File.id == file_id, File.user_id == current_user.id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    print(file.path)
    download_url = download_file_from_b2(file.path)
    return {"download_url": download_url}
    

# Borrar archivo
@router.delete("/{file_id}")
def delete_file(file_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    file = db.query(File).filter(File.id == file_id, File.user_id == current_user.id).first()

    if not file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    db.delete(file)
    db.commit()

    delete_file_from_b2(file.path)  
    return {"message": "Archivo eliminado exitosamente"}

# Mover archivo a otra carpeta
@router.put("/{file_id}/move")
def move_file(file_id: uuid.UUID, new_folder_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Implementar logica mover archivo

    file = db.query(File).filter(File.id == file_id, File.user_id==current_user.id).first()

    if not file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    file.folder_id = new_folder_id

    db.commit()

    return {"message": "file moved successfully"}

# Renombrar archivo
@router.put("/{file_id}/rename")
def rename_file(file_id: uuid.UUID, fileResponse: FileRename, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    #logica renombrar archivo

    file = db.query(File).filter(File.id == file_id, File.user_id==current_user.id).first()  
    if not file:
        raise HTTPException(status_code=404, detail="file not found")


    ## Crear fileResponse 
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
def get_file(file_id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    file = db.query(File).filter(File.id== file_id).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="file not found")
    

    new_file = new_file = File(
        folder_id = file.folder_id,
        name = file.name,
        size = file.size,
        mime_type = file.mime_type,
    )

    if file.user_id == current_user.id:
        return {"file": new_file}
    
    share = db.query(FileShare).filter(
        FileShare.file_id == file_id,
        FileShare.shared_with_user_id == current_user.id
    ).first()

    if not share:
        raise HTTPException(
            status_code=403,
            detail="Acces denied"
        )
    
    if share.expires_at and share.expires_at < datetime.utcnow(): 
        raise HTTPException(
            status_code=403,
            detail="Share expired"
        )

    return {"file": new_file}
    


# Compartir archivo con otro usuario
@router.post("/{file_id}/share")
def share_file(file_id : uuid.UUID,share_data: ShareFileSchema, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    

    #Implementar logica para compartir un archivo
    if share_data.forever:
        expires_at = None
    else:
        if not any([share_data.expires_in_minutes, share_data.expires_in_days, share_data.expires_in_hours]):
            share_data.expires_in_days = 30


        expires_at = datetime.utcnow() + timedelta(
        days= share_data.expires_in_days or 0,
        hours= share_data.expires_in_hours or 0,
        minutes= share_data.expires_in_minutes or 0,
        )

    user_to_share = db.query(User).filter(User.email == share_data.email).first()

    if not user_to_share:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.id == user_to_share.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot share a file with yourself"
        )

    file = db.query(File).filter(File.id == file_id, File.
    user_id == current_user.id, File.is_deleted == False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")


    existing_share = db.query(FileShare).filter(FileShare.file_id == file_id, FileShare.shared_with_user_id == user_to_share.id  ).first()

    if existing_share:
        existing_share.expires_at = expires_at
        existing_share.shared_at = datetime.utcnow()
        db.commit()

        return {
        "message": "File shared, succesfully",
        "share_id": str(existing_share.id),
        "expires_at": expires_at
    }
    



    file_share = FileShare(
        id= uuid.uuid4(),
        file_id= file_id,
        shared_with_user_id= user_to_share.id,
        created_at= datetime.utcnow(),
        expires_at=expires_at,
        shared_at= datetime.utcnow(),
    )

    db.add(file_share)
    db.commit()
    db.refresh(file_share)

    return {
        "message": "File shared, succesfully",
        "share_id": str(file_share.id),
        "expires_at": expires_at
    }

