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
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return param

async def verify_token(
        access_token = Depends(bearer_extractor),
        x_realm: str = Depends(realm_extractor)) -> User:
    """Verify token and extract user information"""

    url = f"https://lokiam.de/realms/{x_realm}/protocol/openid-connect/certs"
    jwks_client = PyJWKClient(url)

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        payload = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["RS256"],
            audience="loki-back",
            options={"verify_exp": True},
        )

        username = payload["sub"]
        client = payload["azp"]
        email = payload["email"]
        try:
            roles = payload["resource_access"][client]["roles"]
        except KeyError:
            roles = []

        if username is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Username not specified")

        return User(username, email, roles)
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
def verify_lha_user(user: User = Depends(verify_token)):
    """Verify that the user is a LHA user"""
    if "lha-user" not in user.role:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="User is not a LHA user")
    return user

# This is how they do authorization with OAuth2 in the past
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
        
