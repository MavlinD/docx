from fastapi import Request, HTTPException
from src.docx.assets import APIRouter
from logrich.logger_ import log  # noqa
from yarl import URL
from src.docx.config import templates
from typing import Any
from starlette.responses import HTMLResponse


router = APIRouter()


@router.get("/", include_in_schema=False, response_class=HTMLResponse)
async def read_home(request: Request) -> Any:
    """домашняя страница"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/{article:str}", include_in_schema=False, response_class=HTMLResponse)
async def read_wiki_structure(request: Request) -> Any:
    """страницы помощи"""
    url = URL(str(request.url))
    article = url.name or url.parts[-2]
    try:
        return templates.TemplateResponse(f"{article}/index.html", {"request": request})
    except Exception as err:
        raise HTTPException(status_code=404, detail="Ничего нет")


@router.get("/search/search_index.json", include_in_schema=False, response_class=HTMLResponse)
async def search(request: Request) -> Any:
    """поиск"""
    return templates.TemplateResponse("search/search_index.json", {"request": request})
