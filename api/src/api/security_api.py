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

class AuthenticationException(HTTPException):
    """Exception for unauthorized access (e.g. when user does not have required role)"""
    def __init__(self, msg: str = "Authentication error"):
        super().__init__(status_code=HTTP_401_UNAUTHORIZED, detail=msg)

class BearerTokenException(HTTPException):
    """Exception for invalid Bearer token"""
    def __init__(self):
        super().__init__(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid Bearer token", headers={"WWW-Authenticate": "Bearer"})

async def get_realm(x_realm: str) -> str:
    """
    Validate the realm. Returns the realm or raises HTTPException (401)\n
    Note: This is a standard function that CANNOT be used by FastAPI's dependency injection as described here:
    https://fastapi.tiangolo.com/tutorial/dependencies/\n
    Use realm_extractor for extracting realm from X-Realm header via dependency injection\n
    """
    if x_realm == "":
        raise AuthenticationException("X-Realm header not specified")
    return x_realm

async def get_bearer(authorization: str) -> str:
    """
    Validate the bearer token in Authorization header. Returns the Bearer token or raises HTTPException (401)\n
    Note: This is a standard function that CANNOT be used by FastAPI's dependency injection as described here:
    https://fastapi.tiangolo.com/tutorial/dependencies/\n
    Use bearer_extractor for validating and extracting the token via dependency injection\n
    """
    scheme, param = get_authorization_scheme_param(authorization)
    if scheme == "":
        raise BearerTokenException()
    if scheme.lower() != "bearer":
        raise BearerTokenException()
    return param

async def get_user(
        access_token: str,
        x_realm: str) -> UserDetail:
    """Verify and extract user information.\n
    Returns a UserDetail object if successful, raises HTTPException (401) if token or X-Realm header is not given or invalid\n
    Note: This is a standard function that CANNOT be used by FastAPI's dependency injection as described here:
    https://fastapi.tiangolo.com/tutorial/dependencies/\n
    Use user_detail_extractor for validating and extracting the token via dependency injection\n
    """

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
            raise AuthenticationException("User Id not specified")
    
        return UserDetail(userId, email, roles)
    except jwt.exceptions.InvalidTokenError:
        raise AuthenticationException("Invalid token")


async def realm_extractor(x_realm: str = Header("X-Realm")):
    """
    Dependency injection way to extract realm information from X-Realm header\n
    Use it in your endpoints like this:\n
    def foo(x_realm: str = Depends(realm_extractor))
    """
    return get_realm(x_realm)

async def bearer_extractor(authorization: str = Header("Authorization")):
    """
    Dependency injection way to extract and validate bearer token from Authorization header\n
    Use it in your endpoints like this:\n
    def foo(authorization: str = Depends(bearer_extractor))
    """
    return get_bearer(authorization)

async def user_detail_extractor(
        access_token: str = Depends(bearer_extractor),
        x_realm: str = Depends(realm_extractor)) -> UserDetail:
    """
    Dependency injection way to get user detail\n
    Returns a UserDetail object if successful, raises HTTPException (401) if token or X-Realm header is not given or invalid\n
    Use it in your endpoints like this:\n
    def foo(user: UserDetail = Depends(user_detail_extractor))
    """
    return get_user(access_token, x_realm)
    


def user_role_filter(role: str, user: UserDetail = Depends(user_detail_extractor)):
    """
    Dependency injection way to verify if user has specified role
    Returns a UserDetail object if successful,\n
    raises HTTPException (401) if token or X-Realm header is not given or invalid,\n
    raises HTTPException (403) if user does not have the specified role\n
    Note: You CANNOT use this directly as a dependency.\n
    You need to create a partial function for each role you want to verify\n
    Check the example below for lha-user role\n
    """
    if role not in user.role:
        raise NotAuthorizedException()
    return user

"""
Dependency injection way to verify if an user has lha-user role
Similar dependencies can be created for other roles
e.g. verify_lha_admin = partial(verify_user_with_role, "lha-admin")
then in endpoints: def foo(user: UserDetail = Depends(verify_lha_admin))
"""
lha_user_filter = partial(user_role_filter, "lha-user")