from sqlalchemy.orm import Session
from app.models.folder import Folder
from app.models.file import File
from app.services.file_service import delete_file_from_b2
    
def delete_folder_recursive(folder: Folder, db: Session):
    files = db.query(File).filter(File.folder_id == folder.id).all()

    for file in files:
        delete_file_from_b2(file.path)  # Eliminar el archivo de B2

    db.query(File).filter(File.folder_id == folder.id).delete()
    subfolders = db.query(Folder).filter(Folder.parent_id == folder.id).all()
    for sub in subfolders:
        delete_folder_recursive(sub, db)
    
    db.flush() 
    db.delete(folder)
