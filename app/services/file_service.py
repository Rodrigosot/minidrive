from datetime import datetime
import hashlib
from io import BytesIO
from app.core.b2_client import s3
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.file import File
import uuid
from app.core.config import settings


def upload_file_to_b2(
    folder_id: uuid.UUID,
    file: UploadFile,
    db: Session,
    user_id: str
):
    b2_key = str(uuid.uuid4())

    content = file.file.read()

    size = len(content)
    file_hash = hashlib.sha256(content).hexdigest()

    s3.upload_fileobj(BytesIO(content), settings.B2_KEYNAME, b2_key, ExtraArgs={'ContentType': file.content_type})

    new_file = File(
        id=uuid.uuid4(),
        user_id=user_id,
        folder_id=folder_id,
        name=file.filename,
        path=b2_key,
        size=size,
        mime_type=file.content_type,
        hash=file_hash, 
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return new_file


def delete_file_from_b2(path):
    return s3.delete_object(Bucket=settings.B2_KEYNAME, Key=path)

def download_file_from_b2(path):
    return s3.generate_presigned_url('get_object', Params={'Bucket': settings.B2_KEYNAME, 'Key': path}, ExpiresIn=3600)
    