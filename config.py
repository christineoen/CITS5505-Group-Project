import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DATABASE = os.path.join(os.path.dirname(__file__), "instance", "database.db")
    DEBUG = True
