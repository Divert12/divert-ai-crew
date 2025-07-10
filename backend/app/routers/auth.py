from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, TokenWithUser
from app.crud.user import create_user, get_user_by_username, get_user_by_email
from app.core.security import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur
    
    Args:
        user: Données de l'utilisateur à créer
        db: Session de base de données
        
    Returns:
        Utilisateur créé
        
    Raises:
        HTTPException: Si l'utilisateur existe déjà
    """
    # Vérifier si l'utilisateur existe déjà
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Créer l'utilisateur
    db_user = create_user(db, user)
    return db_user

@router.post("/login", response_model=TokenWithUser)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Connexion d'un utilisateur
    """
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }