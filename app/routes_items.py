from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_session_user_id
from app.database import get_db
from app.models import PRIORITY_CHOICES, Box, Item, User
from app.photos import delete_photo, save_photo

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_current_user(request: Request, db: Session) -> User | None:
    user_id = get_session_user_id(request)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id).first()


@router.get("/")
@router.get("/items")
def loose_items_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    items = db.query(Item).filter(Item.box_id.is_(None)).order_by(Item.created_at.desc()).all()
    return templates.TemplateResponse("items.html", {
        "request": request,
        "user": user,
        "items": items,
        "priorities": PRIORITY_CHOICES,
    })


@router.get("/items/new")
def new_loose_item_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse("item_form.html", {
        "request": request,
        "user": user,
        "box": None,
        "item": None,
        "priorities": PRIORITY_CHOICES,
    })


@router.post("/items/new")
async def create_loose_item(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    priority: str = Form("no_prioritario"),
    weight_kg: str = Form(""),
    estimated_value: str = Form(""),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    photo_path = None
    thumb_path = None
    if photo and photo.filename:
        data = await photo.read()
        if data:
            photo_path, thumb_path = save_photo(data, photo.filename)

    item = Item(
        box_id=None,
        name=name,
        description=description,
        photo_path=photo_path,
        thumb_path=thumb_path,
        priority=priority,
        weight_kg=float(weight_kg) if weight_kg else None,
        estimated_value=float(estimated_value) if estimated_value else None,
        created_by=user.id,
    )
    db.add(item)
    db.commit()
    return RedirectResponse("/items", status_code=303)


@router.get("/boxes/{box_id}/items/new")
def new_item_form(box_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("item_form.html", {
        "request": request,
        "user": user,
        "box": box,
        "item": None,
        "priorities": PRIORITY_CHOICES,
    })


@router.post("/boxes/{box_id}/items/new")
async def create_item(
    box_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    priority: str = Form("no_prioritario"),
    weight_kg: str = Form(""),
    estimated_value: str = Form(""),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    photo_path = None
    thumb_path = None
    if photo and photo.filename:
        data = await photo.read()
        if data:
            photo_path, thumb_path = save_photo(data, photo.filename)

    item = Item(
        box_id=box_id,
        name=name,
        description=description,
        photo_path=photo_path,
        thumb_path=thumb_path,
        priority=priority,
        weight_kg=float(weight_kg) if weight_kg else None,
        estimated_value=float(estimated_value) if estimated_value else None,
        created_by=user.id,
    )
    db.add(item)
    db.commit()
    return RedirectResponse(f"/boxes/{box_id}", status_code=303)


@router.get("/items/{item_id}")
def item_detail(item_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return RedirectResponse("/", status_code=303)

    boxes = db.query(Box).order_by(Box.number).all()
    return templates.TemplateResponse("item_detail.html", {
        "request": request,
        "user": user,
        "item": item,
        "boxes": boxes,
        "priorities": PRIORITY_CHOICES,
    })


@router.get("/items/{item_id}/edit")
def edit_item_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("item_form.html", {
        "request": request,
        "user": user,
        "box": item.box,
        "item": item,
        "priorities": PRIORITY_CHOICES,
    })


@router.post("/items/{item_id}/edit")
async def edit_item(
    item_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    priority: str = Form("no_prioritario"),
    weight_kg: str = Form(""),
    estimated_value: str = Form(""),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return RedirectResponse("/", status_code=303)

    item.name = name
    item.description = description
    item.priority = priority
    item.weight_kg = float(weight_kg) if weight_kg else None
    item.estimated_value = float(estimated_value) if estimated_value else None

    if photo and photo.filename:
        data = await photo.read()
        if data:
            delete_photo(item.photo_path, item.thumb_path)
            item.photo_path, item.thumb_path = save_photo(data, photo.filename)

    db.commit()
    return RedirectResponse(f"/items/{item.id}", status_code=303)


@router.post("/items/{item_id}/move")
def move_item(
    item_id: int,
    request: Request,
    box_id: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return RedirectResponse("/", status_code=303)

    old_box_id = item.box_id
    new_box_id = int(box_id) if box_id else None
    item.box_id = new_box_id
    db.commit()

    # If htmx request, return OOB partial fragments for source + target containers
    if request.headers.get("HX-Request"):
        from app.routes_organize import render_container_partial

        html = render_container_partial(db, new_box_id, oob=True)
        if old_box_id != new_box_id:
            html += render_container_partial(db, old_box_id, oob=True)
        return HTMLResponse(html)

    return RedirectResponse(f"/items/{item.id}", status_code=303)


@router.post("/items/{item_id}/delete")
def delete_item(item_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return RedirectResponse("/", status_code=303)

    box_id = item.box_id
    delete_photo(item.photo_path, item.thumb_path)
    db.delete(item)
    db.commit()
    if box_id:
        return RedirectResponse(f"/boxes/{box_id}", status_code=303)
    return RedirectResponse("/items", status_code=303)
