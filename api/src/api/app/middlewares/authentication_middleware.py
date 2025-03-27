from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from security_api import _verify_token, validate_bearer, validate_realm

class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        protected_methods = ['POST', 'PUT', 'DELETE']
        if request.method in protected_methods:
            try:
                bearer = await validate_bearer(request.headers.get("Authorization"))
                realm = await validate_realm(request.headers.get("X-Realm"))
                user = await _verify_token(bearer, realm)
                request.state.user = user
            except HTTPException as e:
                return JSONResponse(e.detail, e.status_code)
            
        response = await call_next(request)
        return response