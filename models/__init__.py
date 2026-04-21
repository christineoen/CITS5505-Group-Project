from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .babysitter_profile import BabysitterProfile
from .parent_profile import ParentProfile
