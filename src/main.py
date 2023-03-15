"""Application main."""
from authentication.models import User  # noqa: F401
from authentication.router import router as auth_router

from catalog.models import Folder, Product  # noqa: F401
from catalog.router import router as catalog_router

from core.router import router as core_router

from dependencies import oauth2_scheme

from fastapi import Depends, FastAPI

import uvicorn


app = FastAPI(title='PriceScrapper',
              description='Main service of all price control system.')
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(core_router)

@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
