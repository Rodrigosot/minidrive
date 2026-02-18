from app.core.database import engine, Base
from app.models.user import User
from app.models.file import File
from app.models.activitylog import ActivityLog
from app.models.fileshare import FileShare
from app.models.folder import Folder
from app.models.plan import Plan
from app.models.role import Role
from app.models.user_plan import UserPlan
from app.models.user_plan_history import UserPlanHistory

Base.metadata.create_all(bind=engine)
