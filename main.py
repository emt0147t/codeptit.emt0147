"""
Online Judge - Main Application
FastAPI-based online judge system for competitive programming practice.
"""
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from config import SECRET_KEY, CATEGORIES, BASE_DIR
from database import get_db, init_db
from models import Problem, Submission, User
from routers import auth, problems, submissions

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(title="Online Judge", version="1.0.0")

# Middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Static files & templates – use absolute paths for Linux deployment
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Include routers
app.include_router(auth.router)
app.include_router(problems.router)
app.include_router(submissions.router)


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    logger.info(f"Starting Online Judge, BASE_DIR={BASE_DIR}")
    logger.info(f"DB exists: {(BASE_DIR / 'online_judge.db').exists()}")
    init_db()
    logger.info("Database initialized successfully")


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page with stats and recent problems."""
    from routers.auth import get_current_user
    user = get_current_user(request, db)

    total_problems = db.query(Problem).count()
    total_submissions = db.query(Submission).count()
    total_users = db.query(User).count()

    # Category stats
    from sqlalchemy import func
    cat_counts = dict(
        db.query(Problem.category, func.count(Problem.id))
        .group_by(Problem.category).all()
    )
    categories_with_counts = []
    for slug, info in CATEGORIES.items():
        categories_with_counts.append({
            "slug": slug,
            **info,
            "count": cat_counts.get(slug, 0),
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "total_problems": total_problems,
        "total_submissions": total_submissions,
        "total_users": total_users,
        "categories": categories_with_counts,
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)