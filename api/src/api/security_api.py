# # coding: utf-8

from fastapi import Header
from fastapi import Depends  # noqa: F401
from fastapi.security import (  # noqa: F401
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jwt import PyJWKClient
import jwt  # noqa: F401

from app.models.extra_models import TokenModel

from fastapi import Depends, HTTPException
from fastapi.security.utils import get_authorization_scheme_param

from services.auth import VerifyToken, User
from core.config import REQUIRESAUTH
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN


class NotAuthorizedException(HTTPException):
    """Exception for unauthorized access (e.g. when user does not have required role)"""
    def __init__(self):
        super().__init__(status_code=HTTP_403_FORBIDDEN, detail="Not authorized")

async def realm_extractor(x_realm: str = Header("X-Realm")):
    """Extract realm information from request header"""
    if x_realm == "":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, 
            detail="X-Realm header not specified"
            )
    return x_realm

async def bearer_extractor(authorization: str = Header("Authorization")):
    """Extract bearer token from request header"""
    scheme, param = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer":
        raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Token is not Bearer",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return param

async def verify_token(
        access_token = Depends(bearer_extractor),
        x_realm: str = Depends(realm_extractor)) -> User:
    """Verify token and extract user information"""

    # every lha has its own realm and users are associated with a specific realm (stored in X-Realm header)
    # the signing key is different across realms, to decode we need to specify the certificate endpoint for PyJWKClient
    # and PyJWKClient will fetch the signing key for us
    url = f"https://lokiam.de/realms/{x_realm}/protocol/openid-connect/certs"
    jwks_client = PyJWKClient(url)

    try:
        # decode bearer token
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        payload = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["RS256"],
            audience="loki-back",
            options={"verify_exp": True},
        )

        # construct user object
        username = payload["sub"]
        client = payload["azp"]
        email = payload["email"]

        try:
            # extract client roles
            roles = payload["resource_access"][client]["roles"]
        except KeyError:
            roles = []
        
        # username is required
        if username is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Username not specified")
    
        return User(username, email, roles)
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")

def verify_lha_user(user: User = Depends(verify_token)):
    """Verify if user has lha-user role"""
    if "lha-user" not in user.role:
        raise NotAuthorizedException()
    return user

# deprecated: this is a temporary setup
# now we use verify_token to verify the bearer token (JWT)
bearer_auth = HTTPBearer()
async def get_token_bearerAuth(credentials: HTTPAuthorizationCredentials = Depends(bearer_auth)) -> TokenModel:
    """
    Check and retrieve authentication information from custom bearer token.

    :param credentials Credentials provided by Authorization header
    :type credentials: HTTPAuthorizationCredentials
    :return: Decoded token information or None if token is invalid
    :rtype: TokenModel | None
    """
    if  REQUIRESAUTH:
        # print(type(credentials))
        # print(credentials)
        if not credentials:
            raise HTTPException(status_code=401, detail="Not authorized or invalid credentials")
        result = VerifyToken(credentials.credentials).verify()
        # print(result)
        if result.get("status"):
            raise HTTPException(status_code=401, detail="Not authorized or invalid credentials")
        
