from datetime import datetime, timezone
from fastapi import Request
from sqlalchemy.orm import Session
from app.models.fileshare import FileShare
from app.models.folder import Folder
from app.models.file import File
from app.models.user import User
from app.services.activitylog_service import ActivityLogService, ActivityAction, TargetType
from app.services.file_service import delete_file_from_b2
    
def delete_folder_recursive(folder: Folder, db: Session, current_user: User, request: Request):
    files = db.query(File).filter(File.folder_id == folder.id).all()

    for file in files:
        delete_file_from_b2(file.path)  # Eliminar el archivo de B2
        db.query(FileShare).filter(FileShare.file_id == file.id).delete()
        db.delete(file)
        ActivityLogService.log(
        db=db,
        user_id=current_user.id,
        action=ActivityAction.PERMANENT_DELETE_FILE,
        target_type=TargetType.FILE,
        target_id=file.id, 
        details=(
            f"delete file {file.id}"
        ),
        ip_address=request.client.host
    )

    subfolders = db.query(Folder).filter(Folder.parent_id == folder.id).all()
    for sub in subfolders:
        delete_folder_recursive(sub, db, current_user, request)
    
    
    ActivityLogService.log(
        db=db,
        user_id=current_user.id,
        action=ActivityAction.PERMANENT_DELETE_FOLDER,
        target_type=TargetType.FOLDER,
        target_id=folder.id, 
        details=(
            f"delete folder folder='{folder.name}' ({folder.id})"
        ),
        ip_address=request.client.host
    )
    db.delete(folder)

def soft_delete_folder_recursive(folder: Folder, db: Session, current_user: User,request: Request):
    files = db.query(File).filter(File.folder_id == folder.id).all()

    for file in files:
        file.deleted_at = datetime.now(timezone.utc)
        ActivityLogService.log(db=db, user_id=current_user.id, action=ActivityAction.SOFT_DELETE_FILE, target_type=TargetType.FILE, target_id=file.id, details=
        f"Soft delete file due to recursive folder deletion | "
        f"file='{file.name}' ({file.id}) | "
        f"parent_folder='{folder.name}' ({folder.id})", ip_address=request.client.host)

    subfolders = db.query(Folder).filter(Folder.parent_id == folder.id).all()

    for sub in subfolders:
        soft_delete_folder_recursive(sub, db, current_user, request)

    folder.deleted_at = datetime.now(timezone.utc)

    ActivityLogService.log(
        db=db,
        user_id=current_user.id,
        action=ActivityAction.SOFT_DELETE_FOLDER,
        target_type=TargetType.FOLDER,
        target_id=folder.id, 
        details=(
            f"Soft delete folder recursively | "
            f"folder='{folder.name}' ({folder.id})"
        ),
        ip_address=request.client.host
    )

def recovery_folder(request: Request,folder: Folder, db: Session, current_user: User):
    files = db.query(File).filter(File.folder_id == folder.id, File.deleted_at.isnot(None)).all()

    for file in files:
        ActivityLogService.log(
        db=db,
        user_id=current_user.id,
        action=ActivityAction.RESTORE_FILE,
        target_type=TargetType.FILE,
        target_id=file.id, 
        details=(
            f"file recovery succesfuly {file.id}"
        ),
        ip_address=request.client.host)
        file.deleted_at = None

    subfolders = db.query(Folder).filter(Folder.parent_id == folder.id, Folder.deleted_at.isnot(None)).all()

    for sub in subfolders: 
        recovery_folder(request ,sub, db, current_user)

    folder.deleted_at = None
    
    ActivityLogService.log(
        db=db,
        user_id=current_user.id,
        action=ActivityAction.RESTORE_FOLDER,
        target_type=TargetType.FOLDER,
        target_id=folder.id, 
        details=(
            f"folder recovery recursively | "
            f"folder='{folder.name}' ({folder.id})"
        ),
        ip_address=request.client.host)