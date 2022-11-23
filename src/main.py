"""Application main."""
from authentication.models import User  # noqa: F401
from authentication.router import router as auth_router

from catalog.models import Group, Product  # noqa: F401
from catalog.router import router as catalog_router

from database import Retailer, URL, WebPage  # noqa: F401

from dependencies import oauth2_scheme

from fastapi import Depends, FastAPI

from report.models import ReportHeader, ReportLine  # noqa: F401
from report.router import router as report_router

import uvicorn

app = FastAPI()
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(report_router)


@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
