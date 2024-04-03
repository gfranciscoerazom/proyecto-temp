from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Url para conectarse a la base de datos
URL_DATABASE = "postgresql://postgres:issue-sulfite-retinal@localhost:5432/proyecto"

# Crear la conexión a la base de datos
engine = create_engine(URL_DATABASE)

# Crear una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una clase base para las clases de la base de datos
Base = declarative_base()
