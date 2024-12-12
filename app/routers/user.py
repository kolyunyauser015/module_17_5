from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get("/user_id")
async def user_by_id(db: Annotated[Session, Depends(get_db)],
                     user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail='User was not found')
    return user


@router.get("/user_id/tasks")
async def user_by_user_id(db: Annotated[Session, Depends(get_db)],
                          user_id: int):
    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    return tasks


@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)],
                      create_users: CreateUser):
    user = db.scalar(select(User).where(User.username == create_users.username))
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Change the username')
    db.execute(insert(User).values(username=create_users.username,
                                   firstname=create_users.firstname,
                                   lastname=create_users.lastname,
                                   age=create_users.age,
                                   slug=slugify(create_users.username)))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'}


@router.put("/update")
async def update_user(db: Annotated[Session, Depends(get_db)],
                      user_id: int,
                      update_users: UpdateUser):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User was not found')
    db.execute(update(User).where(User.id == user_id).values(firstname=update_users.firstname,
                                                             lastname=update_users.lastname,
                                                             age=update_users.age))
    db.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'User update is successful!'}


@router.delete("/delete")
async def delete_user(db: Annotated[Session, Depends(get_db)],
                      user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail='User was not found')
    db.execute(delete(User).where(User.id == user_id))
    db.execute(delete(Task).where(Task.user_id == user_id))
    db.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'User delete is successful!'}
