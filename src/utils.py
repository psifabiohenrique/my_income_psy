from contextlib import contextmanager
from .models.database import get_session

@contextmanager
def session_scope():
    """Provides a transactional scope around a series of operations."""
    session = next(get_session())
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
