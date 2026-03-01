"""Create initial database and seed users."""
from app.database import create_tables, SessionLocal
from app.models import User
from app.auth import hash_pin


def seed():
    create_tables()
    db = SessionLocal()

    # Check if users already exist
    if db.query(User).count() > 0:
        print("Users already exist, skipping seed.")
        db.close()
        return

    users = [
        User(name="Alex", pin=hash_pin("2546"), avatar_emoji="🧔", is_admin=True),
        User(name="Yeni", pin=hash_pin("1305"), avatar_emoji="👩", is_admin=True),
        User(name="Eugenio", pin=hash_pin("0000"), avatar_emoji="👦", is_admin=False),
    ]

    db.add_all(users)
    db.commit()
    db.close()
    print("Seed complete! Users created: Alex (admin), Mamá (admin), Mateo")
    print("Default PIN for all: 1234 (Mateo: 0000)")


if __name__ == "__main__":
    seed()
