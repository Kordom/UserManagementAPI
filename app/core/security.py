from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    Args:
        password: Raw user password.
    Returns:
        Securely hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password
    Args:
        password: Raw user password
        hashed_password: Stored hashed password from database.
    Returns:
        bool if password matches

    """
    return pwd_context.verify(password, hashed_password)
