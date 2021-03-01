import os
import shutil
from time import sleep

from gopublish.db_models import PublishedFile
from gopublish.extensions import db

class TestApiView():
    template_repo = "/gopublish/test-data/test-repo/"
    testing_repo = "/myrepo"
    public_file = "/myrepo/my_file_to_publish.txt"
    published_file = "/myrepo/public/my_file_to_publish_v1.txt"

    def setup_method(self):
        if os.path.exists(testing_repo):
            shutil.rmtree(testing_repo)
        shutil.copytree(self.template_repo, testing_repo)

    def teardown_method(self):
        if os.path.exists(testing_repo):
            shutil.rmtree(testing_repo)
        if self.file_id:
            for file in PublishedFile.query.filter(PublishedFile.file_id == self.file_id):
                db.session.delete(file)
            db.session.commit()

    def test_view_incorrect_id(self, client):
        """
        Get file with incorrect id
        """

        fake_id = "XXX"
        url = "/api/view/" + fake_id
        response = client.get(url)

        assert response.status_code == 404
        assert response.json == {}

    def test_view_missing_file(self, client):
        """
        Get file with correct id, but file not created
        """

        fake_id = "f2ecc13f-3038-4f78-8c84-ab881a0b567d"
        url = "/api/view/" + fake_id
        response = client.get(url)

        assert response.status_code == 404
        assert response.json == {}

    def test_view_existing_file(self, client)
        self.file_id = create_mock_published_file(self, client, "available")
        published_file = "/myrepo/public/my_file_to_publish_v1.txt"
        size = os.path.getsize(published_file)
        hash = md5(published_file)

        url = "/api/view/" + self.file_id
        response = client.get(url)

        assert response.status_code == 200
        data = response.json
        data.pop('publishing_date', None)

        assert data == {
            "contact": "",
            "owner": "root",
            "status": "available",
            "file_name": "my_file_to_publish.txt",
            "version": 1,
            "size": size,
            "hash": hash,
        }

    def create_mock_published_file(self, client, status):
            file_name = "my_file_to_publish.txt"
            public_file = "/myrepo/my_file_to_publish.txt"
            published_file = "/myrepo/public/my_file_to_publish_v1.txt"
            size = os.path.getsize(public_file)
            hash = md5(public_file)
            # Copy file in public repo
            shutil.copy(public_file, published_file)
            size = os.path.getsize(file_path)
            pf = PublishedFile(file_path=published_file, file_name=file_name, old_file_path=public_file, repo_path="/myrepo", version=1, size=size, hash=hash, status=status, owner="root")
            db.session.add(pf)
            db.session.commit()
            return pf.id

    def md5(fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
