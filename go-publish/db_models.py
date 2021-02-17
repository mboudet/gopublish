from datetime import datetime

from .extensions import db

class PublishedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    encoded_path = db.Column(db.Text(), index=True, nullable=False)
    hash = db.Column(db.String(255), index=True, nullable=False)
    version = db.Column(db.Integer, index=True, nullable=False)
    path = db.Column(db.Text(), index=True, nullable=False)

    def __repr__(self):
        return '<PublishedFile {}>'.format(self.id)
