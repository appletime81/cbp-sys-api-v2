import configparser

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# read ini file
config = configparser.ConfigParser()

# read section
section = "ubuntu"
config.read("dbinfo.ini")
user = config[section]["user"]
pwd = config[section]["pwd"]
url = config[section]["url"]
port = config[section]["port"]
db_name = config[section]["db_name"]

DB_URL = f"mysql+pymysql://{user}:{pwd}@{url}:{port}/{db_name}"

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)

Base = declarative_base()
