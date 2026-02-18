from sqlalchemy.orm import Session
from app.models.folder import Folder
from app.models.file import File

def delete_folder_recursive(folder: Folder, db: Session):
    db.query(File).filter(File.folder_id == folder.id).delete()
    
    subfolders = db.query(Folder).filter(Folder.parent_id == folder.id).all()
    for sub in subfolders:
        delete_folder_recursive(sub, db)
    
    db.delete(folder)
