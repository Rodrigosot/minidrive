import uuid
from datetime import datetime
from sqlalchemy.orm.session import Session
from app.models.activitylog import ActivityLog
from enum import Enum

class ActivityAction(str, Enum):
    REGISTER = "REGISTER" #//
    LOGIN = "LOGIN" # //

    CREATE_FOLDER = "CREATE_FOLDER" # //

    UPLOAD_FILE = "UPLOAD_FILE" # //
    SHARE_FILE = "SHARE_FILE" # //

    SOFT_DELETE_FILE = "SOFT_DELETE_FILE" # // 
    SOFT_DELETE_FOLDER = "SOFT_DELETE_FOLDER" # //

    RESTORE_FILE = "RESTORE_FILE"
    RESTORE_FOLDER = "RESTORE_FOLDER"

    PERMANENT_DELETE_FILE = "PERMANENT_DELETE_FILE"
    PERMANENT_DELETE_FOLDER = "PERMANENT_DELETE_FOLDER"

class TargetType(str, Enum):
    FILE = "file"
    FOLDER = "folder"
    USER = "user"

class ActivityLogService:
    @staticmethod
    def log(db: Session, user_id: uuid.UUID, action: ActivityAction , target_type: TargetType | None = None, target_id: uuid.UUID | None = None, details: str | None = None, ip_address: str | None = None):
        
        activityLog = ActivityLog(
            id=uuid.uuid4(),
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details, 
            created_at= datetime.now(),
            ip_address=ip_address
        )

        db.add(activityLog)
        db.commit()