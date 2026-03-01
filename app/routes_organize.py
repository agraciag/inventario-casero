from collections import Counter

from fastapi import APIRouter, Depends, Request
from markupsafe import Markup
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_session_user_id
from app.database import get_db
from app.models import PRIORITY_CHOICES, Box, Item, User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_current_user(request: Request, db: Session) -> User | None:
    user_id = get_session_user_id(request)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id).first()


def priority_summary(items: list[Item]) -> list[tuple[str, str, str, int]]:
    """Return list of (key, label, color, count) for non-zero priorities."""
    counts = Counter(item.priority for item in items)
    result = []
    for key, label, color in PRIORITY_CHOICES:
        c = counts.get(key, 0)
        if c > 0:
            result.append((key, label, color, c))
    return result


def render_container_partial(
    db: Session, box_id: int | None, oob: bool = True
) -> str:
    """Render a single container (drop zone) + its tags as HTML fragments."""
    if box_id is not None:
        items = (
            db.query(Item)
            .filter(Item.box_id == box_id)
            .order_by(Item.created_at.desc())
            .all()
        )
        box = db.query(Box).filter(Box.id == box_id).first()
    else:
        items = (
            db.query(Item)
            .filter(Item.box_id.is_(None))
            .order_by(Item.created_at.desc())
            .all()
        )
        box = None

    summary = priority_summary(items)
    container_id = f"container-{box_id}" if box_id else "container-loose"
    tags_id = f"tags-{box_id}" if box_id else "tags-loose"
    oob_attr = Markup(' hx-swap-oob="true"') if oob else ""

    container_html = templates.get_template("_organize_container.html").render(
        items=items,
        box=box,
        container_id=container_id,
        oob_attr=oob_attr,
    )
    tags_html = templates.get_template("_organize_tags.html").render(
        summary=summary,
        tags_id=tags_id,
        oob_attr=oob_attr,
    )
    return container_html + tags_html


@router.get("/organize")
def organize_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    loose_items = (
        db.query(Item)
        .filter(Item.box_id.is_(None))
        .order_by(Item.created_at.desc())
        .all()
    )
    boxes = db.query(Box).order_by(Box.number).all()

    # Pre-load items per box
    box_data = []
    for box in boxes:
        items = (
            db.query(Item)
            .filter(Item.box_id == box.id)
            .order_by(Item.created_at.desc())
            .all()
        )
        box_data.append({
            "box": box,
            "box_items": items,
            "summary": priority_summary(items),
        })

    loose_summary = priority_summary(loose_items)

    return templates.TemplateResponse("organize.html", {
        "request": request,
        "user": user,
        "loose_items": loose_items,
        "loose_summary": loose_summary,
        "box_data": box_data,
    })
