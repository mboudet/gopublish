from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .extensions import db

class PublishedFile(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    task_id = db.Column(db.String(255), index=True)
    # Maybe store it as text? Or encoded?
    file_path = db.Column(db.String(255), index=True, nullable=False)
    old_file_path = db.Column(db.String(255), index=True, nullable=False)
    # To check quickly if managed by baricadr
    repo_path = db.Column(db.String(255), index=True, nullable=False)
    hash = db.Column(db.String(255), index=True)
    status = db.Column(db.String(255), nullable=False, default='creating')
    publishing_date = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    # Maybe store it as a string? We don't need to run queries on size
    size = db.Column(db.BigInteger, index=True, default=0, nullable=False)

    def __repr__(self):
        return '<PublishedFile {}>'.format(self.id)
