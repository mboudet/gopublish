import os
import shutil

from gopublish.extensions import db

from . import GopublishTestCase


class TestApiView(GopublishTestCase):
    template_repo = "/gopublish/test-data/test-repo/"
    testing_repo = "/repos/myrepo"
    public_file = "/repos/myrepo/my_file_to_publish.txt"
    published_file = "/repos/myrepo/public/my_file_to_publish_v1.txt"

    def setup_method(self, app):
        with app.app_context():
            db.create_all()
        if os.path.exists(self.testing_repo):
            shutil.rmtree(self.testing_repo)
        shutil.copytree(self.template_repo, self.testing_repo)

    def teardown_method(self):
        if os.path.exists(self.testing_repo):
            shutil.rmtree(self.testing_repo)
        db.session.remove()
        db.drop_all()

    def test_delete_not_admin(self, app, client):
        file_id = self.create_mock_published_file("available")
        url = "/api/delete/" + file_id

        token = self.create_mock_token(app)
        response = client.delete(url, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 401
        assert response.json == {'error': True, 'errorMessage': 'Admin required'}

    def test_delete(self, app, client):
        file_id = self.create_mock_published_file("available")
        url = "/api/delete/" + file_id

        token = self.create_mock_token(app, user="adminuser")
        response = client.delete(url, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 200
        assert response.json == {'message': 'File deleted'}
