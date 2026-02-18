from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.folder import Folder
from app.models.file import File
import uuid


router = APIRouter(prefix="/folder", tags=["Folders"])

@router.get("/")
def read_root_folder(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    root_folder = db.query(Folder).filter(Folder.user_id == current_user.id, Folder.parent_id == None).first()

    files = db.query(File).filter(File.folder_id == root_folder.id).all()


    return {"message": "Root folder for the authenticated user", "folder": root_folder, "files": files}

@router.get("/{folder_id}")
def read_folder(folder_id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.user_id == current_user.id).first()

    if not folder:
        return {"message": "Folder not found"}


    folders = db.query(Folder).filter(Folder.parent_id == folder_id).all()
    

    files = db.query(File).filter(File.folder_id == folder_id).all()
    return {"message": "Folder details", "folder_info": folder, "files": files, "folders": folders}

# Borrar carpeta y su contenido
# Mover carpeta a otra carpeta
# crear carpeta



# renombrar carpeta


