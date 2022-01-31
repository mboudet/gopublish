import hashlib
import os
import shutil
from datetime import datetime, timedelta

from gopublish.db_models import PublishedFile, Tag
from gopublish.extensions import db

import jwt


class GopublishTestCase():

    def create_mock_published_file(self, status, tags=[]):
        file_name = "my_file_to_publish.txt"
        public_file = "/repos/myrepo/my_file_to_publish.txt"
        size = os.path.getsize(public_file)
        hash = self.md5(public_file)
        # Copy file in public repo
        size = os.path.getsize(public_file)

        pf = PublishedFile(file_name=file_name, repo_path="/repos/myrepo", version=1, size=size, hash=hash, status=status, owner="root")

        tag_list = []
        if tags:
            for tag in tags:
                tag_entity = Tag(tag=tag)
                tag_list.append(tag_entity)
                db.session.add(tag_entity)
            db.session.commit()
            pf.tags = tag_list

        db.session.add(pf)
        db.session.commit()
        shutil.copy(public_file, os.path.join('/repos/myrepo/public/', str(pf.id)))
        return str(pf.id)

    def create_mock_published_dual_files(self, status):
        file_name = "my_file_to_publish.txt"
        public_file = "/repos/myrepo/my_file_to_publish.txt"
        size = os.path.getsize(public_file)
        hash = self.md5(public_file)
        # Copy file in public repo
        size = os.path.getsize(public_file)
        pf = PublishedFile(file_name=file_name, repo_path="/repos/myrepo", version=1, size=size, hash=hash, status=status, owner="root")
        db.session.add(pf)
        db.session.commit()
        shutil.copy(public_file, os.path.join('/repos/myrepo/public/', str(pf.id)))
        pf2 = PublishedFile(file_name=file_name, repo_path="/repos/myrepo", version=2, size=size, hash=hash, status=status, owner="root", version_of=pf)
        db.session.add(pf)
        db.session.commit()
        shutil.copy(public_file, os.path.join('/repos/myrepo/public/', str(pf2.id)))

        return [str(pf.id), str(pf2.id)]

    def create_mock_token(self, app, expire_now=False, user="root"):
        if expire_now:
            expire_at = datetime.utcnow() - timedelta(hours=12)
        else:
            expire_at = datetime.utcnow() + timedelta(hours=12)

        token = jwt.encode({"username": user, "exp": expire_at}, app.config['SECRET_KEY'], algorithm="HS256")
        return token

    def create_mock_tag(self, tag):
        tag = Tag(tag=tag)
        db.session.add(tag)
        db.session.commit()
        return tag.id

    def md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
