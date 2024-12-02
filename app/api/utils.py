from typing import Annotated

from fastapi import Request, Header, HTTPException, Depends, Query
from firebase_admin import auth


async def _pagination_params(
        offset=Query(default=0),
        limit=Query(default=10),
        order=Query(default='asc')

):
    return {
        'offset': offset,
        'limit': limit,
        'order': order
    }


PaginationParams = Annotated[dict, Depends(_pagination_params)]


def get_user(request: Request):
    return request.headers.get("RMS-User", "admin")


async def check_user_firebase_auth(authorization: str = Header(None)):
    if authorization:
        token = authorization.split(" ")[1]
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            raise HTTPException(
                status_code=403, detail=f"Error with authentication: {e}"
            )
    else:
        raise HTTPException(status_code=401, detail=f"Unauthorized")
