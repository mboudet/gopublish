import os
import shutil

from gopublish.db_models import PublishedFile
from gopublish.extensions import db

from . import GopublishTestCase


class TestApiView(GopublishTestCase):
    template_repo = "/gopublish/test-data/test-repo/"
    testing_repo = "/repos/myrepo"
    public_file = "/repos/myrepo/my_file_to_publish.txt"
    published_file = "/repos/myrepo/public/my_file_to_publish_v1.txt"
    file_id = ""

    def setup_method(self):
        if os.path.exists(self.testing_repo):
            shutil.rmtree(self.testing_repo)
        shutil.copytree(self.template_repo, self.testing_repo)

    def teardown_method(self):
        if os.path.exists(self.testing_repo):
            shutil.rmtree(self.testing_repo)
        if self.file_id:
            for file in PublishedFile.query.filter(PublishedFile.id == self.file_id):
                db.session.delete(file)
            db.session.commit()
            self.file_id = ""

    def test_unpublish_wrong_owner(self, app, client):
        self.file_id = self.create_mock_published_file(client, "available")
        url = "/api/unpublish/" + self.file_id

        token = self.create_mock_token(app, user="jdoe")
        response = client.delete(url, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 401
        assert response.json == {}

    def test_unpublish(self, app, client):
        self.file_id = self.create_mock_published_file(client, "available")
        url = "/api/unpublish/" + self.file_id

        token = self.create_mock_token(app)
        response = client.delete(url, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 200
        assert response.json == {'message': 'File unpublished'}

    def test_unpublish_admin(self, app, client):
        self.file_id = self.create_mock_published_file(client, "available")
        url = "/api/unpublish/" + self.file_id

        token = self.create_mock_token(app, user="adminuser")
        response = client.delete(url, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 200
        assert response.json == {'message': 'File unpublished'}
