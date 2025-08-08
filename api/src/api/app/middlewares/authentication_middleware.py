from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from security_api import get_user, get_bearer, get_realm

from app.models.user_detail import UserDetail

# authentication middleware that filters requests before they reach the endpoints
# so far it only checks if the user is authenticated for POST, PUT, DELETE methods
class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # authenticate all methods except GET and OPTIONS
        protected_methods = ['POST', 'PUT', 'DELETE']
        if request.method in protected_methods:
            try:
                # try to verify token and extract user information
                bearer = await get_bearer(request.headers.get("Authorization"))
                realm = await get_realm(request.headers.get("X-Realm"))
                user = await get_user(bearer, realm)
                
                # store user information in request state
                # can be then accessed in endpoints e.g. 
                # async def get_user(request: Request):
                #     return request.state.user
                request.state.user = user
                request.state.realm = realm
                # (Optional) role check can be added
                # if ['admin'] not in user.role:
                #     raise HTTPException(
                #         status_code=403,
                #         detail="Not authorized"
                #     )

            except HTTPException as e:
                return JSONResponse(e.detail, e.status_code)
            
        response = await call_next(request)
        return response