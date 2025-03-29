from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
router = APIRouter()
router.mount("/static", StaticFiles(directory="app/templates/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
@router.get("/")
async def root(request: Request):
    print('web')
    return templates.TemplateResponse("index.html", {"request": request})
def mount_static(app):
    app.mount("/static", StaticFiles(directory="app/templates/static"), name="static")