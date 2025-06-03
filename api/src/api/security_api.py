# # coding: utf-8

from fastapi import Header
from fastapi import Depends  # noqa: F401
from jwt import PyJWKClient
import jwt  # noqa: F401

from fastapi import Depends, HTTPException
from fastapi.security.utils import get_authorization_scheme_param

from app.models.user_detail import UserDetail
from core.config import IDP_ROOT_URL
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from functools import partial


class NotAuthorizedException(HTTPException):
    """Exception for unauthorized access (e.g. when user does not have required role)"""
    def __init__(self):
        super().__init__(status_code=HTTP_403_FORBIDDEN, detail="Not authorized")

async def validate_realm(x_realm: str) -> str:
    """Validate the realm. Returns the realm or raises HTTPException (401)"""
    if x_realm == "":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, 
            detail="X-Realm header not specified"
            )
    return x_realm

async def validate_bearer(authorization: str) -> str:
    """Validate the authorization scheme. Returns the Bearer token or raises HTTPException (401)"""
    scheme, param = get_authorization_scheme_param(authorization)
    if scheme == "":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Authorization header not specified",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if scheme.lower() != "bearer":
        raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Token is not Bearer",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return param

async def realm_extractor(x_realm: str = Header("X-Realm")):
    """Extract realm information from request header and validate it"""
    return validate_realm(x_realm)

async def bearer_extractor(authorization: str = Header("Authorization")):
    """Extract bearer token from request header and validate it"""
    return validate_bearer(authorization)

async def verify_token(
        access_token: str = Depends(bearer_extractor),
        x_realm: str = Depends(realm_extractor)) -> UserDetail:
    return _verify_token(access_token, x_realm)
    

async def _verify_token(
        access_token: str,
        x_realm: str) -> UserDetail:
    """Verify token and extract user information"""

    # every lha has its own realm and users are associated with a specific realm (stored in X-Realm header)
    # the signing key is different across realms, to decode we need to specify the certificate endpoint for PyJWKClient
    # and PyJWKClient will fetch the signing key for us
    url = f"{IDP_ROOT_URL}/realms/{x_realm}/protocol/openid-connect/certs"
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
        userId = payload["sub"]
        client = payload["azp"]
        email = payload["email"]

        try:
            # extract client roles
            roles = payload["resource_access"][client]["roles"]
        except KeyError:
            roles = []
        
        # userId is required
        if userId is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User Id not specified")
    
        return UserDetail(userId, email, roles)
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")

def verify_user_with_role(role: str, user: UserDetail = Depends(verify_token)):
    """Verify if user has specified role"""
    if role not in user.role:
        raise NotAuthorizedException()
    return user

# Verify if user has lha-user role
# Similar dependencies can be created for other roles
# e.g. verify_lha_admin = partial(verify_user_with_role, "lha-admin")
#      in endpoints: def foo(user: UserDetail = Depends(verify_lha_admin))
verify_lha_user = partial(verify_user_with_role, "lha-user")