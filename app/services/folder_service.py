from datetime import datetime, timezone

from sqlalchemy.orm import Session
from app.models.fileshare import FileShare
from app.models.folder import Folder
from app.models.file import File
from app.services.file_service import delete_file_from_b2
    
def delete_folder_recursive(folder: Folder, db: Session):
    files = db.query(File).filter(File.folder_id == folder.id).all()

    for file in files:
        delete_file_from_b2(file.path)  # Eliminar el archivo de B2
        db.query(FileShare).filter(FileShare.file_id == file.id).delete()
        db.delete(file)

    subfolders = db.query(Folder).filter(Folder.parent_id == folder.id).all()
    for sub in subfolders:
        delete_folder_recursive(sub, db)
    
    
    db.delete(folder)

def soft_delete_folder_recursive(folder: Folder, db: Session):
    files = db.query(File).filter(File.folder_id == folder.id).all()

    for file in files:
        file.deleted_at = datetime.now(timezone.utc)

    subfolders = db.query(Folder).filter(Folder.parent_id == folder.id).all()

    for sub in subfolders:
        soft_delete_folder_recursive(sub, db)

    folder.deleted_at = datetime.now(timezone.utc)

def recovery_folder(folder: Folder, db: Session):
    files = db.query(File).filter(File.folder_id == folder.id).all()

    for file in files:
        file.deleted_at = None

    subfolders = db.query(Folder).filter(Folder.parent_id == folder.id).all()

    for sub in subfolders: 
        recovery_folder(sub, db)

    folder.deleted_at = None