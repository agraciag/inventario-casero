from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _migrate_items_box_id_nullable():
    """Make items.box_id nullable (SQLite doesn't support ALTER COLUMN)."""
    insp = inspect(engine)
    if "items" not in insp.get_table_names():
        return  # Table doesn't exist yet, will be created with correct schema
    cols = {c["name"]: c for c in insp.get_columns("items")}
    if "box_id" not in cols or cols["box_id"]["nullable"]:
        return  # Already nullable or column missing
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE items RENAME TO _items_old"))
        conn.execute(text("""
            CREATE TABLE items (
                id INTEGER PRIMARY KEY,
                box_id INTEGER REFERENCES boxes(id),
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                photo_path TEXT,
                thumb_path TEXT,
                priority TEXT DEFAULT 'no_prioritario',
                weight_kg REAL,
                estimated_value REAL,
                created_by INTEGER NOT NULL REFERENCES users(id),
                created_at DATETIME
            )
        """))
        conn.execute(text("""
            INSERT INTO items SELECT * FROM _items_old
        """))
        conn.execute(text("DROP TABLE _items_old"))


def create_tables():
    _migrate_items_box_id_nullable()
    Base.metadata.create_all(bind=engine)
