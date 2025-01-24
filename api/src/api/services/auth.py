import jwt
from core.config import DOMAIN, API_AUDIENCE, ALGORITHMS, ISSUER

class User():
    """A simple user model for authentication & authorization"""
    def __init__(self, username: str, email: str = "", role: list[str] = []):
        self.username = username
        self.email = email
        self.role = role

    def __str__(self):
        return """User(username="{}", email="{}", roles=[{}])""".format(
            self.username, self.email, ", ".join(self.role)
        )

# deprecated: Used by get_token_bearerAuth which is a temporary setup
# now we use verify_token method in security_api.py
class VerifyToken():
    """Does all the token verification using PyJWT"""

    def __init__(self, token):
        self.token = token
        self.config = {
          "DOMAIN": DOMAIN,
          "API_AUDIENCE": API_AUDIENCE,
          "ALGORITHMS": ALGORITHMS,
          "ISSUER": ISSUER
        }
        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f'https://{self.config["DOMAIN"]}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.config["ALGORITHMS"],
                audience=self.config["API_AUDIENCE"],
                issuer=self.config["ISSUER"],
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return payload