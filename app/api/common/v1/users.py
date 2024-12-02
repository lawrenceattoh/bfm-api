from enum import Enum
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.processes import manage_users as mu

router = APIRouter(prefix='/v1/users', tags=['users'])


class AccessLevel(Enum):
    ADMIN = 'ADMIN'
    VIEWER = 'VIEWER'
    EDITOR = 'EDITOR'


class User(BaseModel):
    uid: str | None = None
    email: str | None = None
    access_level: AccessLevel


class Users(BaseModel):
    users: List[User]


class Email(BaseModel):
    email: str


@router.get('/', response_model=Users)
async def get_users():
    return {'users': mu.get_users()}


@router.patch('/')
async def patch_users(users: Users):
    updated_users = []
    for user in users.users:
        try:
            mu.update_user_permissions(user.email, user.access_level)
            updated_users.append(user)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    return {'updated_users': updated_users}


@router.delete('/')
async def delete_user(user: Email):
    try:
        result = mu.delete_user(user.email)
        return {'status': 'deleted', 'message': result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/')
async def create_user(user: User):
    mu.create_user(user.email, user.access_level)
    return True
