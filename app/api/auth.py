from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth import User
from app.schemas.auth import UserRegister, TokenResponse, UserLogin
from app.services.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", 
            response_model=TokenResponse, 
            status_code=status.HTTP_201_CREATED,
            summary="Register a new user account",
            response_description="User registered and JWT token issued successfully.")
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
        
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=AuthService.hash_password(user_in.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    token = AuthService.create_access_token(subject=db_user.id)
    
    # Must perfectly map to TokenResponse schema keys
    return {"user": db_user, "token": token}

@router.post("/login", 
            response_model=TokenResponse,
            status_code=status.HTTP_200_OK,
            summary="Authenticate a user and retrieve a token",
            response_description="Credentials verified and new JWT token returned.")
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    # Safely look up by login_in.email from JSON structure
    user = db.query(User).filter(User.email == login_in.email).first()
    print(user)
    print(login_in)
    if not user or not AuthService.verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
        
    token = AuthService.create_access_token(subject=user.id)
    return {"user": user, "token": token}