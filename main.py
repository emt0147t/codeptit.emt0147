"""
CodePTITclone - Main Application
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
app = FastAPI(title="CodePTITclone", version="1.0.0")

# Middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Static files & templates – use absolute paths for Linux deployment
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Include routers
app.include_router(auth.router)
app.include_router(problems.router)
app.include_router(submissions.router)


@app.get("/debug-db")
def debug_db():
    """Diagnose DB connection issues - temporary."""
    import traceback
    from config import DATABASE_URL as cfg_url
    result = {"config_url_start": cfg_url[:30] + "..." if cfg_url else "None"}
    try:
        from database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        result["status"] = "OK"
        result["host"] = str(engine.url.host)
        result["port"] = engine.url.port
        result["database"] = str(engine.url.database)
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()[-500:]
    return result


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    import os
    logger.info(f"Starting CodePTITclone (Render/Docker)")
    
    logger.info(f"Initializing DB...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"FAILED TO INITIALIZE DB ON STARTUP: {e}")
        # We don't exit here, let the first request try again or fail gracefully
        pass


import time

home_stats_cache = {"timestamp": 0, "data": {}}

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page with stats and recent problems."""
    from routers.auth import get_current_user
    user = get_current_user(request, db)

    current_time = time.time()
    if current_time - home_stats_cache["timestamp"] > 60 or not home_stats_cache["data"]:
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
            
        home_stats_cache["data"] = {
            "total_problems": total_problems,
            "total_submissions": total_submissions,
            "total_users": total_users,
            "categories": categories_with_counts
        }
        home_stats_cache["timestamp"] = current_time

    data = home_stats_cache["data"]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "total_problems": data["total_problems"],
        "total_submissions": data["total_submissions"],
        "total_users": data["total_users"],
        "categories": data["categories"],
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)