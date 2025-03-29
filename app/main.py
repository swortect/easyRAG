from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from app.config import TORTOISE_ORM
from tortoise.contrib.fastapi import register_tortoise
# from tortoise import Tortoise
from app.routes import router as main_router
from app.routes.web import mount_static

from app.utils import VectorEncoder

app = FastAPI()

app.include_router(main_router, prefix="")
mount_static(app)



register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)


app.vectorEncoderInstance = VectorEncoder()

app.connected_websockets={}