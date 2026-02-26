from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session, aliased
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.folder import Folder
from app.models.file import File
import uuid
from app.schemas.folder import FolderCreate, FolderRename
from app.services.folder_service import delete_folder_recursive, recovery_folder, soft_delete_folder_recursive

Parent = aliased(Folder)

router = APIRouter(prefix="/folder", tags=["Folders"])

@router.get("/")
def read_root_folder(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    root_folder = db.query(Folder).filter(Folder.user_id == current_user.id, Folder.parent_id == None).first()

    files = db.query(File).filter(File.folder_id == root_folder.id, File.deleted_at.is_(None)).all()
    folders = db.query(Folder).filter(Folder.parent_id == root_folder.id).all()


    return {"message": "Root folder for the authenticated user", "folder": root_folder, "files": files, "folders": folders}

@router.get("/{folder_id}")
def read_folder(folder_id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.user_id == current_user.id).first()

    if not folder:
        return {"message": "Folder not found"}


    folders = db.query(Folder).filter(Folder.parent_id == folder_id).all()
    files = db.query(File).filter(File.folder_id == folder_id, File.deleted_at.is_(None)).all()
    return {"message": "Folder details", "folder_data": folder, "files": files, "folders": folders}

 
@router.get("/trash")
def get_deleted(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    
    
    folders = ( 
        db.query(Folder)
        .outerjoin(Parent, Folder.parent_id==Parent.id).
        filter(
            Folder.user_id == current_user.id,
            Folder.deleted_at.is_not(None),
            Parent.deleted_at.is_(None)).all() 
)

    
    files = (
    db.query(File)
    .join(Folder, File.folder_id == Folder.id)
    .filter(
        File.user_id == current_user.id,
        File.deleted_at.isnot(None),
        Folder.deleted_at.is_(None)
    )
    .all()
)
    return {
        "files": files,
        "folders": folders
    }

@router.post("/{folder_id}/restore")
def restore_folder(folder_id: uuid.UUID,db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.user_id == current_user.id).first()

    if not folder:
        raise HTTPException(
            status_code=404, 
            detail="folder not found"
            )
    
    if folder.deleted_at is None:
          raise HTTPException(
            status_code=400,
            detail="folder is not deleted"
        )
    
    recovery_folder(folder, db)
    db.commit()

    return {"message": " Folder restored successfoly"}

# Borrar carpeta y su contenido
# Agregar soft-hard delete
@router.delete("/")
def delete_folder(folder_id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.user_id == current_user.id).first()

    if not folder:
        return {"message": "Folder not found"}


    if folder.name == "root" and folder.parent_id == None:
        return {"message": "Cannot delete root folder"}


    if folder.deleted_at is None: 
        soft_delete_folder_recursive(folder, db)
        msg = "Folder moved to trash"

    else:
        delete_folder_recursive(folder, db)
        msg = "Folder and its contents deleted permanently"


    db.commit()
    return {"message": msg}

# Mover carpeta a otra carpeta
@router.put("/move")
def move_folder(folder_id:uuid.UUID, new_parent_id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.user_id == current_user.id).first()

    if folder.name == "root":
        raise HTTPException(status_code=404, detail="folder root no puede ser movido")

    if not folder:
        return {"message": "Folder not found"}

    new_parent = db.query(Folder).filter(Folder.id == new_parent_id, Folder.user_id == current_user.id).first()

    if not new_parent:
        return {"message": "New parent folder not found"}

    folder.parent_id = new_parent_id
    db.commit()

    return {"message": "Folder moved successfully"}

# crear carpeta
@router.post("/{parent_folder_id}/create")
def create_folder(
    parent_folder_id: uuid.UUID,
    folder: FolderCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    parent_folder = db.query(Folder).filter(
        Folder.id == parent_folder_id, 
        Folder.user_id == current_user.id
    ).first()

    if not parent_folder:
        return {"message": "Parent folder not found"}
    
    new_folder = Folder(
        name=folder.name,  # ahora viene del body
        user_id=current_user.id,
        parent_id=parent_folder_id
    )

    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)

    return {"message": "Folder created successfully", "folder": new_folder}

# renombrar carpeta
@router.put("/rename")
def rename_folder(folder: FolderRename, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing_folder = db.query(Folder).filter(Folder.id == folder.id, Folder.user_id == current_user.id).first()

    if not existing_folder:
        return {"message": "Folder not found"}
    
    if existing_folder.name == "root" and existing_folder.parent_id == None: 
        return {"message" : "Folder root cant rename"} 
    
    existing_folder.name = folder.name
    db.commit()
    return {"message": "Folder renamed successfully", "folder": existing_folder}


