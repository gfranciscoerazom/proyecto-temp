from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime


class User(Base):
    """Modelo para la creación de un usuario"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        """Convertir el modelo a un diccionario"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns if column.name != 'password'}
