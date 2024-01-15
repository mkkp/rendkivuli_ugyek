from flask import redirect
from authlib.integrations.flask_client import OAuth

from app.env import AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN


class MockOauth2Client:
    def __init__(self, client_id):
        self.client_id = client_id

    @property
    def auth0(self):
        return self

    def register(self, name, client_id, **kwargs):
        self.client_id = client_id

    def authorize_redirect(self, redirect_uri):
        # XXX: Not using redirect_url, since it is forced to be https
        # and we want to test on simple http too on localhost.
        return redirect("/callback")

    def authorize_access_token(self):
        return {
            "userinfo": {
                "email": "ketfarku@kutyi.kuty",
                "aud": self.client_id,
                "name": "Teszt Elek",
            }
        }


def setup_oauth(app):
    if AUTH0_CLIENT_ID == "MOCK":
        oauth = MockOauth2Client(AUTH0_CLIENT_ID)
    else:
        oauth = OAuth(app)

        oauth.register(
            "auth0",
            client_id=AUTH0_CLIENT_ID,
            client_secret=AUTH0_CLIENT_SECRET,
            client_kwargs={
                "scope": "openid profile email",
            },
            server_metadata_url=f"https://{AUTH0_DOMAIN}/.well-known/openid-configuration",
        )
    return oauth
