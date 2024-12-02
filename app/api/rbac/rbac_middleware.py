from fastapi import Request, HTTPException
from firebase_admin import auth
from starlette.middleware.base import BaseHTTPMiddleware

role_map = {'GET': ['VIEWER', 'EDITOR', 'ADMIN'],
            'PATCH': ['EDITOR', 'ADMIN'],
            'POST': ['EDITOR', 'ADMIN'],
            'DELETE': ['EDITOR', 'ADMIN']}


class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(request.url)
        token = request.headers.get("Authorization")
        if token is None or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

        token = token.split(" ")[1]
        try:
            decoded_token = auth.verify_id_token(token)
            user_id = decoded_token["uid"]
            _fb_user = auth.get_user(user_id)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # user = {k.decode(): v.decode() for k, v in redis_client.hgetall(user_id).items()}
        required_roles = role_map.get(request.method)

        if '/users/' in request.url.path and request.method in {'PATCH', 'DELETE'}:
            if _fb_user.custom_claims.get('access_level') != 'ADMIN':
                raise HTTPException(status_code=403, detail="Insufficient permissions")
        elif _fb_user.custom_claims.get('access_level') in required_roles:
            pass
        else:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        response = await call_next(request)
        return response
