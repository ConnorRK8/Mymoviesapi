import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

sqLite_file_name = "../database.sqlite"

#Estamos leyendo el directorio actual que es database.py
base_dir = os.path.dirname(os.path.abspath(__file__))

#creamos la url de la base de datos uniendo las 2 variabales anteriores
database_url = f"sqlite:///{os.path.join(base_dir, sqLite_file_name)}"

engine = create_engine(database_url, echo=True)

Session = sessionmaker (bind=engine)

Base = declarative_base()