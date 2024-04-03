from fastapi.encoders import jsonable_encoder
from fastapi import Body, Form
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Annotated

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

app = FastAPI()  # Crear la aplicación de FastAPI
app.mount('/static', StaticFiles(directory='static'), name='static')

# Directorio de las plantillas
templates = Jinja2Templates(directory='templates')

# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)


def get_db():
    """Función para obtener una sesión de la base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependencia para obtener una sesión de la base de datos
db_dependency = Annotated[Session, Depends(get_db)]


class User(BaseModel):
    """Modelo para la creación de un usuario"""
    email: str
    password: str
    first_name: str
    last_name: str


@app.get('/api/users/{id}', tags=['api'])
async def get_user(id: int, db: db_dependency):
    """Obtener un usuario por su id"""
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@app.get('/api/users/{email}/', tags=['api'])
async def get_user(email: str, db: db_dependency):
    """Obtener un usuario por su email"""
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@app.get('/api/users/', tags=['api'])
async def get_users(db: db_dependency):
    """Obtener todos los usuarios"""
    users = db.query(models.User).all()
    return users


@app.post('/api/users/', tags=['api'])
async def create_user(user: User, db: db_dependency):
    """Crear un usuario"""
    db_user = models.User(email=user.email, password=user.password,
                          first_name=user.first_name, last_name=user.last_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.put('/api/users/{id}', tags=['api'])
async def update_user(id: int, user: User, db: db_dependency):
    """Actualizar un usuario"""
    db_user = db.query(models.User).filter(
        models.User.id == id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')

    db_user.email = user.email
    db_user.password = user.password
    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete('/api/users/{id}', tags=['api'])
async def delete_user(id: int, db: db_dependency):
    """Eliminar un usuario"""
    db_user = db.query(models.User).filter(
        models.User.id == id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')

    db.delete(db_user)
    db.commit()
    return db_user


@app.get('/home', response_class=HTMLResponse, tags=['admin'])
async def home(request: Request, db: db_dependency):
    """Página principal"""
    context = {
        'request': request,
        'type': 'users',
        'items': [user.to_dict() for user in db.query(models.User).all()]
    }

    return templates.TemplateResponse('home.html', context)


@app.get('/users/delete/{id}', response_class=HTMLResponse, tags=['admin'])
async def delete(request: Request, id: int, db: db_dependency):
    """Eliminar un usuario"""
    db_user = db.query(models.User).filter(
        models.User.id == id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')

    db.delete(db_user)
    db.commit()

    return RedirectResponse(url='/home', status_code=303)


@app.get('/users/edit/{id}', response_class=HTMLResponse, tags=['admin'])
async def edit(request: Request, id: int, db: db_dependency):
    """Editar un usuario"""
    db_user = db.query(models.User).filter(
        models.User.id == id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')

    context = {
        'request': request,
        'user': db_user
    }

    return templates.TemplateResponse('/forms/user.html', context)


@app.post('/users/edit/{id}', response_class=HTMLResponse, tags=['admin'])
async def edit(request: Request, id: int, db: db_dependency, email: str = Form(...), password: str = Form(...), first_name: str = Form(...), last_name: str = Form(...)):
    """Editar un usuario"""
    db_user = db.query(models.User).filter(
        models.User.id == id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')

    db_user.email = email
    db_user.password = password
    db_user.first_name = first_name
    db_user.last_name = last_name
    db.commit()

    return RedirectResponse(url='/home', status_code=303)


@app.get('/users/create/', response_class=HTMLResponse, tags=['admin'])
async def create(request: Request):
    """Crear un usuario"""
    context = {
        'request': request,
        'user': None
    }

    return templates.TemplateResponse('/forms/user.html', context)


@app.post('/users/create/', response_class=HTMLResponse, tags=['admin'])
async def create(request: Request, db: db_dependency, email: str = Form(...), password: str = Form(...), first_name: str = Form(...), last_name: str = Form(...)):
    """Crear un usuario"""
    db_user = models.User(email=email, password=password,
                          first_name=first_name, last_name=last_name)
    db.add(db_user)
    db.commit()

    return RedirectResponse(url='/home', status_code=303)
