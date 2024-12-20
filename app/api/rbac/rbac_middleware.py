from fastapi import Request, HTTPException
from firebase_admin import auth
from starlette.middleware.base import BaseHTTPMiddleware

role_map = {
    'GET': ['VIEWER', 'EDITOR', 'ADMIN'],
    'PATCH': ['EDITOR', 'ADMIN'],
    'POST': ['EDITOR', 'ADMIN'],
    'DELETE': ['EDITOR', 'ADMIN']
}


class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print('inside dispatch')
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
        else:
            print('YES THERE IS A USER')
            print(request.headers.get('Authorization'))

        token = auth_header.split(" ", 1)[1]

        try:
            decoded_token = auth.verify_id_token(token)
            user_id = decoded_token["uid"]
            fb_user = auth.get_user(user_id)
            print("Firebase user retrieved:", fb_user.uid)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        required_roles = role_map.get(request.method, [])

        if '/users/' in request.url.path and request.method in {'PATCH', 'DELETE'}:
            if fb_user.custom_claims.get('access_level', 'VIEWER') != 'ADMIN':
                raise HTTPException(status_code=403, detail="Insufficient permissions")
        else:
            user_role = fb_user.custom_claims.get('access_level', 'VIEWER')
            if user_role not in required_roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")

        response = await call_next(request)
        return response
