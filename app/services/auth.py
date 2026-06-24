from datetime import datetime, timedelta
from typing import Any, Union
import bcrypt  # Use native bcrypt directly!
from jose import jwt
from app.config import settings

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Converts the plain-text string password to bytes, 
        generates a salt, and hashes it using native bcrypt.
        """
        # Encode the raw text password string into UTF-8 bytes
        password_bytes = password.encode("utf-8")
        
        # Generate a secure salt (defaults to 12 rounds)
        salt = bcrypt.gensalt()
        
        # Hash and return the string version of the hash
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        return hashed_bytes.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a text password against a stored text hash safely.
        """
        try:
            password_bytes = plain_password.encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")
            
            # Use native checkpw to compare safely against timing attacks
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False

    @staticmethod
    def create_access_token(subject: Union[str, Any]) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"exp": expire, "sub": str(subject)}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)