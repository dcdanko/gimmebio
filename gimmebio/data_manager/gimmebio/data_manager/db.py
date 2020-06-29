
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base
from .constants import DB_FILENAME


def findFileInDirRecursively(dirname, filename):
    maybepath = os.path.join(dirname, filename)
    if os.path.isfile(maybepath):
        return maybepath
    else:
        subs = [os.path.join(dirname, f)
                for f in os.listdir(dirname)
                if os.path.isdir(os.path.join(dirname, f))]
        for sub in subs:
            try:
                out = findFileInDirRecursively(sub, filename)
                if out is not None:
                    return out
            except AssertionError:
                pass
    assert False, f'Could not find {filename} in {dirname} or parent dirs'


def find_db(cwd='.'):
    return findFileInDirRecursively('.', DB_FILENAME)


def get_session(database=None):
    db_path = database if database else find_db()
    db_path = f'sqlite:///{db_path}'
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session
