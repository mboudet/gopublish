import os
import shutil
from time import sleep

from gopublish.db_models import PublishedFile
from gopublish.extensions import db

from . import GopublishTestCase


class TestApiPublish(GopublishTestCase):

    template_repo = "/gopublish/test-data/test-repo/"
    testing_repos = ["/repos/myrepo", "/repos/myrepo_copy"]
    public_file = "/repos/myrepo/my_file_to_publish.txt"
    published_file = "/repos/myrepo/public/my_file_to_publish_v1.txt"
    file_ids = []

    def setup_method(self):
        for repo in self.testing_repos:
            if os.path.exists(repo):
                shutil.rmtree(repo)
            shutil.copytree(self.template_repo, repo)

    def teardown_method(self):
        for repo in self.testing_repos:
            if os.path.exists(repo):
                shutil.rmtree(repo)
        for file_id in self.file_ids:
            for file in PublishedFile.query.filter(PublishedFile.id == file_id):
                db.session.delete(file)
            db.session.commit()
        self.file_ids = []

    def test_publish_missing_token_header(self, client):
        """
        Publish without the header
        """
        data = {
            'files': '/foo/bar'
        }
        response = client.post('/api/publish', json=data, headers={'Test': 'some hash'})
        assert response.status_code == 401
        assert response.json == {'error': 'Missing "X-Auth-Token" header'}

    def test_publish_malformed_token_header(self, client):
        """
        Publish without the correct header
        """
        data = {
            'files': '/foo/bar'
        }
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'mytoken'})
        assert response.status_code == 401
        assert response.json == {'error': 'Invalid "X-Auth-Token" header: must start with "Bearer "'}

    def test_publish_incorrect_token(self, client):
        """
        Publish without the correct token
        """
        data = {
            'files': '/foo/bar'
        }
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhIjoiYiJ9.1bSs1XuNia4apOO73KoixwVRM9YNgU4gdYWeZnAkALY'})

        assert response.status_code == 401
        assert response.json == {'error': 'Invalid token'}

    def test_publish_expired_token(self, app, client):
        """
        Publish with an expired token
        """

        data = {
            'files': '/foo/bar'
        }
        token = self.create_mock_token(app, expire_now=True)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.json == {'error': 'Expired token'}
        assert response.status_code == 401

    def test_publish_missing_body(self, app, client):
        """
        Publish without body
        """
        token = self.create_mock_token(app)
        response = client.post('/api/publish', headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 400
        assert response.json == {'error': 'Missing body'}

    def test_publish_missing_path(self, app, client):
        """
        Publish without a proper path
        """
        data = {
            'files': "/foo/bar"
        }
        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 400
        assert response.json == {'error': 'Missing path'}

    def test_publish_missing_file(self, app, client):
        """
        Publish a missing file
        """
        data = {
            'path': "/foo/bar"
        }
        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 400
        assert response.json == {'error': 'File not found at path /foo/bar'}

    def test_publish_folder(self, app, client):
        """
        Publish a folder
        """
        path_to_folder = "/repos/myrepo/myfolder"
        os.mkdir(path_to_folder)

        data = {
            'path': path_to_folder
        }
        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 400
        assert response.json == {'error': 'Path must not be a folder or a symlink'}

    def test_publish_symlink(self, app, client):
        """
        Publish a symlink
        """
        symlink_path = "/repos/myrepo/mylink"
        os.symlink(self.public_file, symlink_path)

        data = {
            'path': symlink_path
        }
        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 400
        assert response.json == {'error': 'Path must not be a folder or a symlink'}

    def test_publish_wrong_email(self, app, client):
        """
        Publish with wrong email address
        """
        data = {
            'path': self.public_file,
            'email': 'x'
        }
        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 400
        assert response.json == {"error": "The email address is not valid. It must have exactly one @-sign."}

    def test_publish_wrong_contact(self, app, client):
        """
        Publish with wrong email address
        """
        data = {
            'path': self.public_file,
            'contact': 'x'
        }
        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 400
        assert response.json == {"error": "The email address is not valid. It must have exactly one @-sign."}

    def test_publish_link_success(self, app, client):
        """
        Try to publish a file in normal conditions
        """
        public_file = "/repos/myrepo/my_file_to_publish.txt"

        data = {
            'path': public_file
        }
        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 200
        data = response.json
        assert data['message'] == "File registering. It should be ready soon"
        assert 'file_id' in data

        file_id = data['file_id']
        self.file_ids = [file_id]

        published_file = os.path.join("/repos/myrepo/public/", file_id)

        wait = 0
        while wait < 60:
            sleep(2)

            if os.path.exists(published_file):
                break
            wait += 1

        assert os.path.exists(published_file)
        assert os.path.islink(public_file)
        assert os.readlink(public_file) == published_file

    def test_publish_copy_success(self, app, client):
        """
        Try to publish a file in normal conditions
        """
        public_file = "/repos/myrepo_copy/my_file_to_publish.txt"

        data = {
            'path': public_file,
        }
        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 200
        data = response.json
        assert data['message'] == "File registering. It should be ready soon"
        assert 'file_id' in data
        assert data['version'] == 1

        file_id = data['file_id']
        self.file_ids = [file_id]

        published_file = os.path.join("/repos/myrepo_copy/public/", file_id)

        wait = 0
        while wait < 60:
            sleep(2)

            if os.path.exists(published_file):
                break
            wait += 1

        assert os.path.exists(published_file)
        assert os.path.exists(public_file)
        assert not os.path.islink(public_file)
        assert self.md5(published_file) == self.md5(public_file)

    def test_update_malformed_id(self, app, client):
        public_file = "/repos/myrepo_copy/my_file_to_publish.txt"

        data = {
            'path': public_file,
            'linked_to': "fakeid"
        }

        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 400
        assert response.json['error'] == "linked_to fakeid is not a valid id"

    def test_update_wrong_id(self, app, client):
        public_file = "/repos/myrepo_copy/my_file_to_publish.txt"

        data = {
            'path': public_file,
            'linked_to': "f2ecc13f-3038-4f78-8c84-ab881a0b567d"
        }

        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 404
        assert response.json['error'] == "linked_to fakeid file does not exists"

    def test_update_wrong_repo(self, app, client):
        file_id = self.create_mock_published_file(client, "available")
        self.file_ids = [file_id]

        public_file = "/repos/myrepo_copy/my_file_to_publish.txt"
        data = {
            'path': public_file,
            'linked_to': file_id
        }

        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 404
        assert response.json['error'] == "linked_to %s file is not in the same repository" % file_id

    def test_update(self, app, client):
        file_id = self.create_mock_published_file(client, "available")
        self.file_ids = [file_id]

        public_file = "/repos/myrepo/my_file_to_publish.txt"
        data = {
            'path': public_file,
            'linked_to': file_id
        }

        token = self.create_mock_token(app)
        response = client.post('/api/publish', json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 200
        data = response.json
        assert data['message'] == "File registering. It should be ready soon"
        assert 'file_id' in data

        assert data['version'] == 2

        new_file_id = data['file_id']
        self.file_ids.append(new_file_id)

        published_file = os.path.join("/repos/myrepo_copy/public/", new_file_id)

        wait = 0
        while wait < 60:
            sleep(2)

            if os.path.exists(published_file):
                break
            wait += 1

        assert os.path.exists(published_file)
        assert os.path.exists(public_file)
        assert not os.path.islink(public_file)
        assert self.md5(published_file) == self.md5(public_file)
