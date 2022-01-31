import os
import shutil

from gopublish.extensions import db

from . import GopublishTestCase


class TestApiTag(GopublishTestCase):
    template_repo = "/gopublish/test-data/test-repo/"
    testing_repo = "/repos/myrepo"
    public_file = "/repos/myrepo/my_file_to_publish.txt"
    published_file = "/repos/myrepo/public/my_file_to_publish_v1.txt"
    file_ids = []
    tag_ids = []

    def setup_method(self):
        if os.path.exists(self.testing_repo):
            shutil.rmtree(self.testing_repo)
        shutil.copytree(self.template_repo, self.testing_repo)

    def teardown_method(self):
        if os.path.exists(self.testing_repo):
            shutil.rmtree(self.testing_repo)
        db.session.remove()
        db.drop_all()

    def test_list_tags(self, client):
        """
        List tags
        """

        self.create_mock_tag("my_tag")

        url = "/api/tag/list"
        response = client.get(url)

        assert response.status_code == 200
        assert response.json == {"tags": ["my_tag"]}

    def test_add_tag_wrong_owner(self, app, client):
        file_id = self.create_mock_published_file("available")
        token = self.create_mock_token(app, user="jdoe")

        data = {
            'tags': 'my_tag'
        }

        url = "/api/tag/add/" + file_id
        response = client.put(url, json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 401
        assert response.json == {}

    def test_add_tag(self, app, client):
        file_id = self.create_mock_published_file("available")
        token = self.create_mock_token(app)

        data = {
            'tags': ['my_tag']
        }

        url = "/api/tag/add/" + file_id
        response = client.put(url, json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 200
        assert response.json.get('file')
        assert response.json['file']['tags'] == ['my_tag']

    def test_untag(self, app, client):
        file_id = self.create_mock_published_file("available", tags=['my_tag'])
        token = self.create_mock_token(app)

        data = {
            'tags': ['my_tag']
        }

        url = "/api/tag/remove/" + file_id
        response = client.put(url, json=data, headers={'X-Auth-Token': 'Bearer ' + token})

        assert response.status_code == 200
        assert response.json.get('file')
        assert response.json['file']['tags'] == []
