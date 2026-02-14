"""
Problem routes: list, detail, create (admin).
"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Problem, TestCase, Submission, SubmissionStatus
from routers.auth import get_current_user, require_admin
from config import PROBLEMS_PER_PAGE, CATEGORIES

router = APIRouter(tags=["problems"])
templates = Jinja2Templates(directory="templates")


@router.get("/problems")
async def problem_list(
    request: Request,
    page: int = 1,
    search: str = "",
    difficulty: str = "",
    category: str = "",
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    query = db.query(Problem)

    if category:
        query = query.filter(Problem.category == category)
    if search:
        query = query.filter(
            (Problem.title.ilike(f"%{search}%")) |
            (Problem.code.ilike(f"%{search}%"))
        )
    if difficulty:
        query = query.filter(Problem.difficulty == difficulty)

    total = query.count()
    problems = query.order_by(Problem.code).offset(
        (page - 1) * PROBLEMS_PER_PAGE
    ).limit(PROBLEMS_PER_PAGE).all()

    total_pages = (total + PROBLEMS_PER_PAGE - 1) // PROBLEMS_PER_PAGE

    # Get solved status for current user
    solved_ids = set()
    if user:
        solved = db.query(Submission.problem_id).filter(
            Submission.user_id == user.id,
            Submission.status == SubmissionStatus.ACCEPTED
        ).distinct().all()
        solved_ids = {s[0] for s in solved}

    # Category info
    category_info = CATEGORIES.get(category) if category else None

    return templates.TemplateResponse("problems.html", {
        "request": request,
        "user": user,
        "problems": problems,
        "page": page,
        "total_pages": total_pages,
        "search": search,
        "difficulty": difficulty,
        "category": category,
        "category_info": category_info,
        "solved_ids": solved_ids,
    })


@router.get("/category/{slug}")
async def category_page(
    request: Request,
    slug: str,
    page: int = 1,
    search: str = "",
    difficulty: str = "",
    db: Session = Depends(get_db)
):
    """Redirect to /problems with category filter."""
    if slug not in CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")

    user = get_current_user(request, db)
    query = db.query(Problem).filter(Problem.category == slug)

    if search:
        query = query.filter(
            (Problem.title.ilike(f"%{search}%")) |
            (Problem.code.ilike(f"%{search}%"))
        )
    if difficulty:
        query = query.filter(Problem.difficulty == difficulty)

    total = query.count()
    problems = query.order_by(Problem.code).offset(
        (page - 1) * PROBLEMS_PER_PAGE
    ).limit(PROBLEMS_PER_PAGE).all()

    total_pages = (total + PROBLEMS_PER_PAGE - 1) // PROBLEMS_PER_PAGE

    solved_ids = set()
    if user:
        solved = db.query(Submission.problem_id).filter(
            Submission.user_id == user.id,
            Submission.status == SubmissionStatus.ACCEPTED
        ).distinct().all()
        solved_ids = {s[0] for s in solved}

    category_info = CATEGORIES[slug]

    return templates.TemplateResponse("problems.html", {
        "request": request,
        "user": user,
        "problems": problems,
        "page": page,
        "total_pages": total_pages,
        "search": search,
        "difficulty": difficulty,
        "category": slug,
        "category_info": category_info,
        "solved_ids": solved_ids,
    })


@router.get("/problem/{problem_code}")
async def problem_detail(
    request: Request,
    problem_code: str,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    problem = db.query(Problem).filter(Problem.code == problem_code).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    sample_testcases = db.query(TestCase).filter(
        TestCase.problem_id == problem.id,
        TestCase.is_sample == True
    ).order_by(TestCase.order).all()

    # Get user's submissions for this problem
    user_submissions = []
    if user:
        user_submissions = db.query(Submission).filter(
            Submission.user_id == user.id,
            Submission.problem_id == problem.id
        ).order_by(Submission.created_at.desc()).limit(10).all()

    return templates.TemplateResponse("problem_detail.html", {
        "request": request,
        "user": user,
        "problem": problem,
        "sample_testcases": sample_testcases,
        "user_submissions": user_submissions,
    })


# --- Admin Routes ---
@router.get("/admin/problems/add")
async def add_problem_page(
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_admin(request, db)
    return templates.TemplateResponse("admin/add_problem.html", {
        "request": request,
        "user": user,
        "error": None
    })


@router.post("/admin/problems/add")
async def add_problem(
    request: Request,
    code: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    input_description: str = Form(""),
    output_description: str = Form(""),
    sample_input: str = Form(""),
    sample_output: str = Form(""),
    difficulty: str = Form("Easy"),
    time_limit: float = Form(1.0),
    memory_limit: int = Form(256),
    db: Session = Depends(get_db)
):
    user = require_admin(request, db)

    # Check duplicate code
    existing = db.query(Problem).filter(Problem.code == code).first()
    if existing:
        return templates.TemplateResponse("admin/add_problem.html", {
            "request": request,
            "user": user,
            "error": f"Mã bài {code} đã tồn tại"
        })

    problem = Problem(
        code=code,
        title=title,
        description=description,
        input_description=input_description,
        output_description=output_description,
        sample_input=sample_input,
        sample_output=sample_output,
        difficulty=difficulty,
        time_limit=time_limit,
        memory_limit=memory_limit,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)

    # Add sample test case
    if sample_input and sample_output:
        tc = TestCase(
            problem_id=problem.id,
            input_data=sample_input.strip(),
            expected_output=sample_output.strip(),
            is_sample=True,
            order=0
        )
        db.add(tc)
        db.commit()

    return RedirectResponse(url=f"/problem/{code}", status_code=302)


@router.get("/admin/problem/{problem_code}/testcases")
async def manage_testcases_page(
    request: Request,
    problem_code: str,
    db: Session = Depends(get_db)
):
    user = require_admin(request, db)
    problem = db.query(Problem).filter(Problem.code == problem_code).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    testcases = db.query(TestCase).filter(
        TestCase.problem_id == problem.id
    ).order_by(TestCase.order).all()

    return templates.TemplateResponse("admin/testcases.html", {
        "request": request,
        "user": user,
        "problem": problem,
        "testcases": testcases,
    })


@router.post("/admin/problem/{problem_code}/testcases/add")
async def add_testcase(
    request: Request,
    problem_code: str,
    input_data: str = Form(...),
    expected_output: str = Form(...),
    is_sample: bool = Form(False),
    db: Session = Depends(get_db)
):
    user = require_admin(request, db)
    problem = db.query(Problem).filter(Problem.code == problem_code).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    max_order = db.query(TestCase).filter(
        TestCase.problem_id == problem.id
    ).count()

    tc = TestCase(
        problem_id=problem.id,
        input_data=input_data.strip(),
        expected_output=expected_output.strip(),
        is_sample=is_sample,
        order=max_order
    )
    db.add(tc)
    db.commit()

    return RedirectResponse(
        url=f"/admin/problem/{problem_code}/testcases", status_code=302
    )


@router.post("/admin/testcase/{testcase_id}/delete")
async def delete_testcase(
    request: Request,
    testcase_id: int,
    db: Session = Depends(get_db)
):
    user = require_admin(request, db)
    tc = db.query(TestCase).filter(TestCase.id == testcase_id).first()
    if not tc:
        raise HTTPException(status_code=404, detail="TestCase not found")

    problem_code = tc.problem.code
    db.delete(tc)
    db.commit()

    return RedirectResponse(
        url=f"/admin/problem/{problem_code}/testcases", status_code=302
    )
