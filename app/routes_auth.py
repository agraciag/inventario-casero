from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import clear_session_cookie, set_session_cookie, verify_pin
from app.database import get_db
from app.models import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
def login_page(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("login.html", {"request": request, "users": users, "error": None})


@router.post("/login")
def login(request: Request, user_id: int = Form(...), pin: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not verify_pin(pin, user.pin):
        users = db.query(User).all()
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "users": users, "error": "PIN incorrecto"},
            status_code=401,
        )
    response = RedirectResponse("/", status_code=303)
    return set_session_cookie(response, user.id)


@router.post("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    return clear_session_cookie(response)
