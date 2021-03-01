import os
import shutil
from time import sleep


class TestApiPublish():

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

    def test_publish_missing_body(self, client):
        """
        Publish without body
        """
        response = client.post('/api/publish')

        assert response.status_code == 400
        assert response.json == {'error': 'Missing body'}

    def test_publish_missing_user(self, client):
        """
        Publish without a user
        """
        data = {
            'files': '/foo/bar'
        }
        response = client.post('/api/publish', json=data)
        assert response.status_code == 401
        assert response.json == {'error': 'Missing username in body'}

    def test_publish_missing_path(self, client):
        """
        Publish without a proper path
        """
        data = {
            'username': 'root',
            'files': "/foo/bar"
        }
        response = client.post('/api/publish', json=data)

        assert response.status_code == 400
        assert response.json == {'error': 'Missing path'}

    def test_publish_missing_file(self, client):
        """
        Publish a missing file
        """
        data = {
            'username': 'root',
            'path': "/foo/bar"
        }
        response = client.post('/api/publish', json=data)

        assert response.status_code == 400
        assert response.json == {'error': 'File not found at path /foo/bar'}

    def test_publish_incorrect_version(self, client):
        """
        Publish without a proper version
        """
        data = {
            'username': 'root',
            'path': self.public_file,
            'version': "x"
        }
        response = client.post('/api/publish', json=data)

        assert response.status_code == 400
        assert response.json == {'error': "Value x is not an integer > 0"}

    def test_publish_duplicate_version(self, client):
        """
        Publish a duplicate (file and version)
        """
        data = {
            'username': 'root',
            'path': self.public_file,
            'version': "2"
        }
        response = client.post('/api/publish', json=data)

        assert response.status_code == 400
        assert response.json == {'error': "Error checking file : File is already published in that version"}

    def test_publish_wrong_email(self, client):
        """
        Publish with wrong email address
        """
        data = {
            'username': 'root',
            'path': self.public_file,
            'email': 'x'
        }
        response = client.post('/api/publish', json=data)

        assert response.status_code == 400
        assert response.json == {"error": "The email address is not valid. It must have exactly one @-sign."}

    def test_publish_wrong_contact(self, client):
        """
        Publish with wrong email address
        """
        data = {
            'username': 'root',
            'path': self.public_file,
            'contact': 'x'
        }
        response = client.post('/api/publish', json=data)

    assert response.status_code == 400
    assert response.json == {"error": "The email address is not valid. It must have exactly one @-sign."}

    def test_publish_success(self, app, client):
        """
        Try to publish a file in normal conditions
        """

        data = {
            'username': 'root',
            'path': self.public_file,
        }
        response = client.post('/api/publish', json=data)

        assert response.status_code == 200
        data = response.json
        assert data['message'] == "File registering. It should be ready soon"
        assert 'file_id' in data

        wait = 0
        while wait < 30:
            sleep(2)

            if os.path.exists(self.published_file):
                break
            wait += 1

        assert os.path.exists(self.published_file)
