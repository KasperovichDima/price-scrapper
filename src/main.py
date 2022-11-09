"""Application main."""
from authentication.router import router as auth_router
from report.router import router as report_router

from dependencies import oauth2_scheme

from fastapi import Depends, FastAPI


app = FastAPI()
app.include_router(auth_router)
app.include_router(report_router)


@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}
