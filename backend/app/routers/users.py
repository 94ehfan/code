from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import get_db
from app.models import NotificationPreference, User
from app.schemas import Token, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(
        username=user_in.username,
        display_name=user_in.display_name,
        phone_number=user_in.phone_number,
        password_hash=hash_password(user_in.password),
        notification_preference=user_in.notification_preference,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id)
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    phone_number: str | None = None,
    notification_preference: NotificationPreference | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if phone_number is not None:
        current_user.phone_number = phone_number
    if notification_preference is not None:
        current_user.notification_preference = notification_preference
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return db.query(User).all()
