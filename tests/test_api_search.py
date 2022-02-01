import os
import shutil

from gopublish.extensions import db

from . import GopublishTestCase


class TestApiSearch(GopublishTestCase):
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

    def test_search_wrong_term(self, client):
        self.create_mock_published_file("available")

        url = "/api/search?file=blablabloblo"
        response = client.get(url)

        assert response.status_code == 200

        data = response.json['files']

        assert len(data) == 0

    def test_search_term(self, client):
        file_id = self.create_mock_published_file("available")
        published_file = os.path.join("/repos/myrepo/public/", file_id)
        size = os.path.getsize(published_file)

        url = "/api/search?file=my_file_to_publish"
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

    def test_search_wrong_tags(self, client):
        self.create_mock_published_file("available", tags=["tag1"])

        url = "/api/search?tags=blabla"
        response = client.get(url)

        assert response.status_code == 200

        data = response.json['files']
        assert data == {}

    def test_search_tags(self, client):
        self.create_mock_published_file("available", tags=["tag2"])
        file_id = self.create_mock_published_file("available", tags=["tag1"])
        published_file = os.path.join("/repos/myrepo/public/", file_id)
        size = os.path.getsize(published_file)

        url = "/api/search?tags=tag1"
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
            "tags": ["tag1"]
        }
