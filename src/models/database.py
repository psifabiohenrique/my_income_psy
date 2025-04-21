import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base  # Import the Base

# Modified DATABASE_URL to handle bundled environment
if getattr(sys, 'frozen', False):
    # we are running in a bundle
    basedir = os.path.dirname(sys.executable)
else:
    # we are running in a normal Python environment
    basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_URL = f"sqlite:///{os.path.join(basedir, 'psicologia.db')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def criar_banco():
if not os.path.exists(os.path.join(basedir, 'psicologia.db')):
    Base.metadata.create_all(bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
