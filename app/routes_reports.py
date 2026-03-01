from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_session_user_id
from app.database import get_db
from app.models import PRIORITY_CHOICES, Box, Item, User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/reports")
def reports(request: Request, db: Session = Depends(get_db)):
    user_id = get_session_user_id(request)
    if user_id is None:
        return RedirectResponse("/login", status_code=303)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse("/login", status_code=303)

    total_boxes = db.query(func.count(Box.id)).scalar() or 0
    total_items = db.query(func.count(Item.id)).scalar() or 0

    # Items by priority
    priority_stats = []
    for value, label, color in PRIORITY_CHOICES:
        count = db.query(func.count(Item.id)).filter(Item.priority == value).scalar() or 0
        weight = db.query(func.sum(Item.weight_kg)).filter(Item.priority == value).scalar() or 0
        value_sum = db.query(func.sum(Item.estimated_value)).filter(Item.priority == value).scalar() or 0
        priority_stats.append({
            "key": value,
            "label": label,
            "color": color,
            "count": count,
            "weight": round(weight, 1),
            "value": round(value_sum),
        })

    # Totals for prioritarios
    priority_weight = db.query(func.sum(Item.weight_kg)).filter(Item.priority == "prioritario").scalar() or 0
    priority_value = db.query(func.sum(Item.estimated_value)).filter(Item.priority == "prioritario").scalar() or 0

    return templates.TemplateResponse("reports.html", {
        "request": request,
        "user": user,
        "total_boxes": total_boxes,
        "total_items": total_items,
        "priority_stats": priority_stats,
        "priority_weight": round(priority_weight, 1),
        "priority_value": round(priority_value),
    })
