from datetime import UTC, timedelta, datetime
from os import access
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from database import SessionLocal
import models
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt


router = APIRouter()
router.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='users/templates')


def get_db():
    """Función para obtener una sesión de la base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependencia para obtener una sesión de la base de datos
db_dependency = Annotated[Session, Depends(get_db)]


class Token(BaseModel):
    """Modelo para el token"""
    access_token: str
    token_type: str


@router.get('/users/signup', tags=['users'])
async def get_users(request: Request):
    """Obtener todos los usuarios"""
    return templates.TemplateResponse('userSignUpForm.html', {'request': request})


@router.post('/users/signup', tags=['admin'])
async def create(request: Request, db: db_dependency, email: str = Form(...), password: str = Form(...), password_confirmation: str = Form(...), first_name: str = Form(...), last_name: str = Form(...)):
    """Crear un usuario"""
    if password != password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')

    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')

    db_user = models.User(email=email, password=password,
                          first_name=first_name, last_name=last_name)
    db.add(db_user)
    db.commit()

    return RedirectResponse(url='/users/signin', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/users/signin', tags=['users'])
async def get_users(request: Request):
    """Obtener todos los usuarios"""
    return templates.TemplateResponse('userSignInForm.html', {'request': request})


@router.post('/users/signin', response_model=Token, tags=['users'])
def login_for_access_token(request: Request, db: db_dependency, email: str = Form(...), password: str = Form(...)):
    db_user = db.query(models.User).filter(models.User.email == email).first()

    if not db_user:
        return templates.TemplateResponse('userSignInForm.html', {'request': request})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect email or password')

    if db_user.password != password:
        return templates.TemplateResponse('userSignInForm.html', {'request': request})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect email or password')

    access_token_expires = timedelta(minutes=30) + datetime.now(UTC)
    access_token = jwt.encode(
        {'sub': db_user.email, 'exp': access_token_expires},
        'Nec dubitamus multa iter quae et nos invenerat.',
        algorithm='HS256'
    )
    response = RedirectResponse(
        url='/home', status_code=status.HTTP_303_SEE_OTHER)

    response.set_cookie(key='access_token', value=f"Bearer {
                        access_token}", httponly=True)

    return response
