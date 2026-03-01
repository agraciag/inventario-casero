import io
import uuid

import qrcode
import qrcode.image.svg
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_session_user_id
from app.database import get_db
from app.models import Box, Item, User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_current_user(request: Request, db: Session) -> User | None:
    user_id = get_session_user_id(request)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id).first()


@router.get("/boxes")
def boxes_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    boxes = db.query(Box).order_by(Box.number).all()
    # Get item counts per box
    counts = dict(
        db.query(Item.box_id, func.count(Item.id))
        .group_by(Item.box_id)
        .all()
    )
    # Get first thumb per box
    thumbs = {}
    for box in boxes:
        first_item = (
            db.query(Item)
            .filter(Item.box_id == box.id, Item.thumb_path.isnot(None))
            .first()
        )
        if first_item:
            thumbs[box.id] = first_item.thumb_path

    return templates.TemplateResponse("boxes.html", {
        "request": request,
        "user": user,
        "boxes": boxes,
        "counts": counts,
        "thumbs": thumbs,
    })


@router.get("/boxes/new")
def new_box_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    next_number = (db.query(func.max(Box.number)).scalar() or 0) + 1
    return templates.TemplateResponse("box_form.html", {
        "request": request,
        "user": user,
        "box": None,
        "next_number": next_number,
    })


@router.post("/boxes/new")
def create_box(
    request: Request,
    label: str = Form(...),
    number: int = Form(...),
    location: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    box = Box(
        number=number,
        label=label,
        location=location,
        qr_code=str(uuid.uuid4()),
        created_by=user.id,
    )
    db.add(box)
    db.commit()
    return RedirectResponse(f"/boxes/{box.id}", status_code=303)


@router.get("/boxes/{box_id}")
def box_detail(box_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        return RedirectResponse("/", status_code=303)

    items = db.query(Item).filter(Item.box_id == box_id).order_by(Item.created_at.desc()).all()
    return templates.TemplateResponse("box_detail.html", {
        "request": request,
        "user": user,
        "box": box,
        "items": items,
    })


@router.get("/boxes/{box_id}/edit")
def edit_box_form(box_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("box_form.html", {
        "request": request,
        "user": user,
        "box": box,
        "next_number": box.number,
    })


@router.post("/boxes/{box_id}/edit")
def edit_box(
    box_id: int,
    request: Request,
    label: str = Form(...),
    number: int = Form(...),
    location: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        return RedirectResponse("/", status_code=303)

    box.label = label
    box.number = number
    box.location = location
    db.commit()
    return RedirectResponse(f"/boxes/{box.id}", status_code=303)


@router.post("/boxes/{box_id}/delete")
def delete_box(box_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or not user.is_admin:
        return RedirectResponse("/", status_code=303)

    box = db.query(Box).filter(Box.id == box_id).first()
    if box:
        db.delete(box)
        db.commit()
    return RedirectResponse("/", status_code=303)


@router.get("/boxes/{box_id}/qr")
def box_qr(box_id: int, request: Request, db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        return RedirectResponse("/", status_code=303)

    # Build URL for this box
    base_url = str(request.base_url).rstrip("/")
    box_url = f"{base_url}/boxes/{box.id}"

    img = qrcode.make(box_url, image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO()
    img.save(buf)
    return Response(content=buf.getvalue(), media_type="image/svg+xml")


@router.get("/boxes/{box_id}/qr-print")
def box_qr_print(box_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("qr_print.html", {
        "request": request,
        "user": user,
        "box": box,
    })
