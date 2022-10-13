"""Project entry point."""
from typing import List
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import interfaces as i
from db_config import SessionLocal
import crud
import models as m
from validation import schemas
import project_typing as pt
from core import report_manager

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_db():
    """Dependency injection."""
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()

@app.get('/home')
def home(request: Request):
    """Home page."""
    return templates.TemplateResponse('home.jinja', {'request': request})

@app.get('/report/form')
def get_report_form(request: Request):
    """Return form to create new report."""
    return templates.TemplateResponse('new_report_form.jinja', {'request': request})

@app.post('/report/create')
def create_report(name: str = Form(), note: str = Form(), db: Session = Depends(get_db)):
    """Create new report by form data."""
    ### MOCK ###
    user: i.IUser = db.query(m.User).first()
    ### MOCK ###
    report_manager.create_report(name, note, user)
    return RedirectResponse('/get_content_of/root', 302)

@app.post('/add_elements')
def add_elements(elements: List[int] = Form()):
    """Add some element of product catalog to request."""
    print(elements)

@app.get('/get_content_of/root', response_model=List[schemas.CatalogElement])
def get_content_of_root(request: Request, db: Session = Depends(get_db)):
    """Get root content of catalog."""
    model = m.Category
    return templates.TemplateResponse(
        'show_elements.jinja',{
            'request': request,
            'elements': crud.get_elements(model, db),
        }
    )

@app.get('/get_content_of/{model_name}/{id}', response_model=List[schemas.CatalogElement])
def get_content_of(request: Request, model_name: pt.ElNames,
    id: int, db: Session = Depends(get_db)):
    """Get inline content of specified model by specified id."""
    return templates.TemplateResponse(
        'show_elements.jinja',{
            'request': request,
            'elements': crud.get_content_by_model_name(model_name, id, db),
        }
    )
