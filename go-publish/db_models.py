from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .extensions import db

class PublishedFile(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    # Maybe store it as text? Or encoded?
    file_path = db.Column(db.String(255), index=True, nullable=False)
    repo_path = db.Column(db.String(255), index=True, nullable=False)
    version = db.Column(db.Integer, index=True, nullable=False)
    hash = db.Column(db.String(255), index=True, nullable=False)
    # Maybe store it as a string? We don't need to run queries on size
    size = db.Column(db.BigInteger, index=True, nullable=False)
    is_pulling = db.Column(db.Boolean, index=True, nullable=False, default=False)

    def __repr__(self):
        return '<PublishedFile {}>'.format(self.id)
