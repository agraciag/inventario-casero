from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import create_tables
from app.routes_auth import router as auth_router
from app.routes_boxes import router as boxes_router
from app.routes_items import router as items_router
from app.routes_organize import router as organize_router
from app.routes_reports import router as reports_router

app = FastAPI(title="Inventario", docs_url=None, redoc_url=None)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routes
app.include_router(auth_router)
app.include_router(boxes_router)
app.include_router(items_router)
app.include_router(organize_router)
app.include_router(reports_router)


@app.on_event("startup")
def startup():
    create_tables()
