# Inventario - App de Inventario para Mudanza

## Project Overview
Inventory app for tracking items in moving boxes. Users can create boxes, add items with photos, and classify by shipping priority.

## Tech Stack
- **Backend**: Python + FastAPI
- **Database**: SQLite via SQLAlchemy
- **Frontend**: Jinja2 templates + htmx + Tailwind CSS (CDN)
- **Photos**: Pillow for resize, HTML5 camera API
- **Auth**: PIN-based with signed session cookies

## Running
```bash
pip install -r requirements.txt
python seed.py        # Create DB + initial users
python run.py         # Start server on port 8000
```

## Project Structure
- `app/main.py` - FastAPI app, startup, middleware
- `app/config.py` - Settings
- `app/database.py` - DB setup
- `app/models.py` - SQLAlchemy models (User, Box, Item)
- `app/auth.py` - PIN auth + session management
- `app/routes_*.py` - Route modules
- `app/photos.py` - Photo processing utilities
- `app/templates/` - Jinja2 templates
- `app/static/` - CSS + JS

## Key Conventions
- Language: UI is in Spanish
- Mobile-first design
- Priority colors: green=prioritario, blue=no_prioritario, yellow=quizas, orange=no_vale_la_pena, red=tirar_regalar_vender
- Photos resized to max 1200px (full) and 300px (thumb)
