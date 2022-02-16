import os
import shutil
import tempfile

from gopublish.extensions import db

from . import GopublishTestCase


class TestApiView(GopublishTestCase):
    template_repo = "/gopublish/test-data/test-repo/"
    testing_repo = "/repos/myrepo"
    public_file = "/repos/myrepo/my_file_to_publish.txt"
    published_file = "/repos/myrepo/public/my_file_to_publish_v1.txt"

    def setup_method(self):
        if os.path.exists(self.testing_repo):
            shutil.rmtree(self.testing_repo)
        shutil.copytree(self.template_repo, self.testing_repo)

    def teardown_method(self):
        if os.path.exists(self.testing_repo):
            shutil.rmtree(self.testing_repo)
        db.session.remove()
        db.drop_all()

    def test_view_incorrect_id(self, app, client):
        """
        Get file with incorrect id
        """

        fake_id = "XXX"
        url = "/api/view/" + fake_id
        response = client.get(url)

        assert response.status_code == 404
        assert response.json == {}

    def test_view_missing_file(self, app, client):
        """
        Get file with correct id, but file not created
        """

        fake_id = "f2ecc13f-3038-4f78-8c84-ab881a0b567d"
        url = "/api/view/" + fake_id
        response = client.get(url)

        assert response.status_code == 404
        assert response.json is None

    def test_view_existing_file(self, app, client):
        file_id = self.create_mock_published_file("available")
        published_file = os.path.join("/repos/myrepo/public/", file_id)
        size = os.path.getsize(published_file)
        hash = self.md5(published_file)

        url = "/api/view/" + file_id
        response = client.get(url)

        assert response.status_code == 200
        data = response.json['file']
        data.pop('publishing_date', None)

        assert data == {
            "contact": None,
            "owner": "root",
            "status": "available",
            "file_name": "my_file_to_publish.txt",
            "path": published_file,
            "version": 1,
            "size": size,
            "hash": hash,
            "siblings": [],
            "tags": []
        }

    def test_view_existing_file_with_siblings(self, app, client):
        file_ids = self.create_mock_published_dual_files("available")
        published_file = os.path.join("/repos/myrepo/public/", file_ids[0])
        size = os.path.getsize(published_file)
        hash = self.md5(published_file)

        url = "/api/view/" + file_ids[0]
        response = client.get(url)

        assert response.status_code == 200
        data = response.json['file']
        data.pop('publishing_date', None)
        assert "siblings" in data and len(data['siblings']) == 1
        data['siblings'][0].pop('publishing_date', None)

        assert data == {
            "contact": None,
            "owner": "root",
            "status": "available",
            "file_name": "my_file_to_publish.txt",
            "path": published_file,
            "version": 1,
            "size": size,
            "hash": hash,
            "siblings": [
                {
                    "uri": file_ids[1],
                    "version": 2,
                    "status": "available"
                }
            ],
            "tags": []
        }

        url = "/api/view/" + file_ids[1]
        response = client.get(url)

        assert response.status_code == 200
        data = response.json['file']
        data.pop('publishing_date', None)
        assert "siblings" in data and len(data['siblings']) == 1
        data['siblings'][0].pop('publishing_date', None)

        assert data == {
            "contact": None,
            "owner": "root",
            "status": "available",
            "file_name": "my_file_to_publish.txt",
            "path": os.path.join("/repos/myrepo/public/", file_ids[1]),
            "version": 2,
            "size": size,
            "hash": hash,
            "siblings": [
                {
                    "uri": file_ids[0],
                    "version": 1,
                    "status": "available"
                }
            ],
            "tags": []
        }

    def test_download_existing_file(self, app, client):
        file_id = self.create_mock_published_file("available")
        published_file = os.path.join("/repos/myrepo/public/", file_id)
        url = "/api/download/" + file_id
        response = client.get(url)

        assert response.status_code == 200

        with tempfile.TemporaryDirectory() as local_path:
            local_file = local_path + '/myfile'
            with open(local_file, "wb") as f:
                f.write(response.data)

            assert self.md5(local_file) == self.md5(published_file)

    def test_download_unpublished_file(self, app, client):
        file_id = self.create_mock_published_file("unpublished")

        url = "/api/download/" + file_id
        response = client.get(url)

        assert response.status_code == 404

    def test_list(self, app, client):
        file_id = self.create_mock_published_file("available")
        published_file = os.path.join("/repos/myrepo/public/", file_id)
        size = os.path.getsize(published_file)

        url = "/api/list"
        response = client.get(url)

        assert response.status_code == 200

        data = response.json['files']

        data[0].pop('publishing_date', None)

        assert len(data) == 1
        assert data[0] == {
            'uri': file_id,
            'file_name': "my_file_to_publish.txt",
            'size': size,
            'version': 1,
            'downloads': 0,
            'status': "available",
            "tags": []
        }
