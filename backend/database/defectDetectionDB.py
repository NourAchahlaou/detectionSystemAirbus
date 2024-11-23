from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


URL_DATABASE = "postgresql://postgres:root@localhost:5432/DefectDetectionDB"

#create a connection to the database, it takes a database url 
#and returns an engine object which represent the core interface to the database 
engine = create_engine(URL_DATABASE)

#create a configured session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()