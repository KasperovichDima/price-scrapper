"""Application main."""
from authentication.router import router as auth_router

from catalog.router import router as catalog_router

from dependencies import oauth2_scheme

from fastapi import Depends, FastAPI

from report.router import router as report_router


from authentication.models import User
from catalog.models import Group, Product
from report.models import ReportHeader, ReportLine
from database import Retailer
from database import WebPage, URL


app = FastAPI()
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(report_router)


@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}
