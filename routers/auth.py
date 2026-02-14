"""
Authentication routes: login, register, logout.
"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from config import BASE_DIR
from sqlalchemy.orm import Session

from database import get_db
from models import User
import bcrypt as _bcrypt

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return _bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current user from session."""
    user_id = request.session.get("user_id")
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    return None


def require_login(request: Request, db: Session = Depends(get_db)):
    """Require user to be logged in."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Please login first")
    return user


def require_admin(request: Request, db: Session = Depends(get_db)):
    """Require user to be admin."""
    user = require_login(request, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/login")
async def login_page(request: Request):
    user = get_current_user(request, next(get_db()))
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {
        "request": request, "error": None
    })


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Sai tên đăng nhập hoặc mật khẩu"
        })
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=302)


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request, "error": None
    })


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db)
):
    # Validate
    if password != password_confirm:
        return templates.TemplateResponse("register.html", {
            "request": request, "error": "Mật khẩu không khớp"
        })

    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("register.html", {
            "request": request, "error": "Tên đăng nhập đã tồn tại"
        })

    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("register.html", {
            "request": request, "error": "Email đã tồn tại"
        })

    # Create user
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)
