# # coding: utf-8

from typing import List, Union
from fastapi import APIRouter
from fastapi import Depends, Security  # noqa: F401
from fastapi.openapi.models import OAuthFlowImplicit, OAuthFlows  # noqa: F401
from fastapi.security import (  # noqa: F401
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    OAuth2,
    OAuth2AuthorizationCodeBearer,
    OAuth2PasswordBearer,
    SecurityScopes,
)
from fastapi.security.api_key import APIKeyCookie, APIKeyHeader, APIKeyQuery  # noqa: F401

from app.models.extra_models import TokenModel , User,UserInDB,Token,TokenData
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from jose import JWTError, jwt
# router = APIRouter()
from services.auth import VerifyToken
from core.config import REQUIRESAUTH
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