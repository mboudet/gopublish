from gopublish.db_models import Token
from gopublish.extensions import db

from . import GopublishTestCase


class TestApiToken(GopublishTestCase):
    token_id = ""

    def teardown_method(self):
        if self.token_id:
            for token in Token.query.filter(Token.id == self.token_id):
                db.session.delete(token)
            db.session.commit()
            self.token_id = ""

    def test_get_token_no_body(self, client):
        """
        Get token without a body
        """
        url = "/api/token/create"

        response = client.post(url)

        assert response.status_code == 400
        assert response.json.get("error") == "Missing body"

    def test_get_token_no_username(self, client):
        """
        Get a token without a username
        """
        body = {"password": "xxx"}
        url = "/api/token/create"

        response = client.post(url, json=body)

        assert response.status_code == 400
        assert response.json.get("error") == "Missing either username or password in body"

    def test_get_token_no_password(self, client):
        """
        Get a token without a password
        """
        body = {"username": "xxx"}
        url = "/api/token/create"

        response = client.post(url, json=body)

        assert response.status_code == 400
        assert response.json.get("error") == "Missing either username or password in body"

    def test_get_token(self, client):
        """
        Get a token
        """
        body = {"username": "xxx", "password": "xxx"}
        url = "/api/token/create"

        response = client.post(url, json=body)

        assert response.status_code == 200
        assert response.json.get("token")

        self.token_id = response.json.get("token")
        assert Token().query.get(self.token_id)

    def test_revoke_malformed_token(self, client):
        """
        Try to revoke malformed token
        """
        token_id = "f2ecc13f-3038-4f78-8c"
        url = "/api/token/delete/" + token_id

        response = client.delete(url)

        assert response.status_code == 400
        assert response.json.get("error") == "Malformed token"

    def test_revoke_wrong_token(self, client):
        """
        Try to revoke wrong token
        """
        token_id = "f2ecc13f-3038-4f78-8c84-ab881a0b567d"
        url = "/api/token/delete/" + token_id

        response = client.delete(url)

        assert response.status_code == 404
        assert response.json.get("error") == "Token not found"

    def test_revoke_token(self, client):
        """
        Try to revoke token
        """
        self.token_id = self.create_mock_token()
        url = "/api/token/delete/" + self.token_id

        response = client.delete(url)

        assert response.status_code == 200
        assert response.json.get("status") == "Token revoked"
        assert not Token().query.get(self.token_id)
