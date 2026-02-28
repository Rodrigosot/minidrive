from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session, aliased
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.fileshare import FileShare
from app.models.folder import Folder
from app.models.file import File
import uuid
from app.schemas.folder import FolderCreate, FolderRename
from app.services.file_service import delete_file_from_b2
from app.services.folder_service import delete_folder_recursive, recovery_folder, soft_delete_folder_recursive

Parent = aliased(Folder)

router = APIRouter(prefix="/folder", tags=["Folders"])

@router.get("/")
def read_root_folder(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    root_folder = db.query(Folder).filter(Folder.user_id == current_user.id, Folder.parent_id == None).first()


    print(root_folder.id)
    files = db.query(File).filter(File.folder_id == root_folder.id, File.deleted_at.is_(None)).all()
    folders = db.query(Folder).filter(Folder.parent_id == root_folder.id).all()


    return {"message": "Root folder for the authenticated user", "folder": root_folder, "files": files, "folders": folders}


@router.get("/shared-with-me")
def get_shared_files(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    files_shared_with_me = db.query(File).join(FileShare, FileShare.file_id == File.id).filter(FileShare.shared_with_user_id == current_user.id, or_(
    FileShare.expires_at == None,
    FileShare.expires_at > datetime.now(timezone.utc)   
), File.deleted_at.is_(None)).all()

    return files_shared_with_me


@router.post("/trash/restore-all")
def restore_all_trash(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    folders = db.query(Folder).filter(Folder.user_id==current_user.id, Folder.deleted_at.isnot(None)).all()
    for folder in folders:
        parent = db.query(Folder).filter(Folder.id==folder.parent_id).first()
        if not parent or parent.deleted_at:
            root = db.query(Folder).filter(Folder.user_id==current_user.id, Folder.name=="root", Folder.parent_id.is_(None)).first()
            folder.parent_id = root.id
        recovery_folder(folder, db)
    
    files = (
        db.query(File)
        .join(Folder, File.folder_id==Folder.id)
        .filter(File.user_id==current_user.id, File.deleted_at.isnot(None), Folder.deleted_at.is_(None))
        .all()
    )
    for f in files:
        f.deleted_at = None
    
    db.commit()
    return {"message": f"Restored {len(folders)} folders and {len(files)} files from trash"}

router.post("/empty-trash")
def empty_trash(db: Session = Depends(get_db), current_user= Depends(get_current_user)):

    files = db.query(File).join(Folder, File.folder_id == Folder.id).filter(
        File.deleted_at.isnot(None),
        Folder.deleted_at.is_(None),  
        File.user_id == current_user.id
    ).all()

    for file in files:
        delete_file_from_b2(file.path)
        db.delete(file)

    folders = db.query(Folder).filter(Folder.deleted_at.isnot(None), Folder.user_id == current_user.id).all()

    for sub in folders:
        delete_folder_recursive(sub, db)
    db.commit()

    return {"message": "Trash emptied successfully"}
    


@router.get("/trash")
def get_deleted(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    folders = db.query(Folder).outerjoin(Parent, Folder.parent_id==Parent.id).filter(
            Folder.user_id == current_user.id,
            Folder.deleted_at.is_not(None),
            Parent.deleted_at.is_(None)).all() 
    
    files = db.query(File).join(Folder, File.folder_id == Folder.id).filter(
        File.user_id == current_user.id,
        File.deleted_at.isnot(None),
        Folder.deleted_at.is_(None)
    ).all()

    return {
        "files": files,
        "folders": folders
    }


@router.get("/{folder_id}")
def read_folder(folder_id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.user_id == current_user.id).first()

    if not folder:
        return {"message": "Folder not found"}


    folders = db.query(Folder).filter(Folder.parent_id == folder_id).all()
    files = db.query(File).filter(File.folder_id == folder_id, File.deleted_at.is_(None)).all()
    return {"message": "Folder details", "folder_data": folder, "files": files, "folders": folders}

@router.get("/{folder_id}/trash")
def read_deleted_folder(folder_id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    folder = db.query(Folder).filter(
        Folder.id == folder_id, 
        Folder.user_id == current_user.id,
        Folder.deleted_at.is_not(None)
    ).first()

    if not folder:
        raise HTTPException(status_code=404, detail="Deleted folder not found")

    # Subcarpetas borradas
    folders = db.query(Folder).filter(
        Folder.parent_id == folder_id,
        Folder.deleted_at.is_not(None)
    ).all()

    # Archivos borrados dentro de esta carpeta
    files = db.query(File).filter(
        File.folder_id == folder_id,
        File.deleted_at.is_not(None)
    ).all()

    return {
        "folder_data": folder,
        "folders": folders,
        "files": files
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
    
    folder_parent = db.query(Folder).filter(Folder.id == folder.parent_id, Folder.user_id == current_user.id).first()


    if not folder_parent or folder_parent.deleted_at is not None:
        root_folder = db.query(Folder).filter(Folder.user_id == current_user.id, Folder.name == "root", Folder.parent_id.is_(None)).first()
        folder.parent_id = root_folder.id
    
    recovery_folder(folder, db)
    db.commit()

    return {"message": "Folder restored successfully"}

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
        parent_id=parent_folder_id,
        updated_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        id=uuid.uuid4()
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


