from datetime import datetime, timedelta
import hashlib
import os
import shutil

from gopublish.db_models import PublishedFile, Token
from gopublish.extensions import db


class GopublishTestCase():

    def create_mock_published_file(self, client, status):
        file_name = "my_file_to_publish.txt"
        public_file = "/repos/myrepo/my_file_to_publish.txt"
        published_file = "/repos/myrepo/public/my_file_to_publish_v1.txt"
        size = os.path.getsize(public_file)
        hash = self.md5(public_file)
        # Copy file in public repo
        shutil.copy(public_file, published_file)
        size = os.path.getsize(public_file)
        pf = PublishedFile(file_name=file_name, stored_file_name="my_file_to_publish_v1.txt", repo_path="/repos/myrepo", version=1, size=size, hash=hash, status=status, owner="root")
        db.session.add(pf)
        db.session.commit()
        return str(pf.id)

    def create_mock_token(self, expire_now=False):
        if expire_now:
            expire_at = datetime.utcnow()
        else:
            expire_at = datetime.utcnow() + timedelta(hours=12)

        token = Token(username="root", expire_at=expire_at)
        db.session.add(token)
        db.session.commit()
        return str(token.id)

    def md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
