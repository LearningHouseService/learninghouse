from fastapi import FastAPI, Request

from learninghouse.api import brain
from learninghouse.core.settings import service_settings
from learninghouse.core.exceptions import LearningHouseException


app = FastAPI(**service_settings().fastapi_kwargs)
app.include_router(brain.router)


@app.exception_handler(LearningHouseException)
async def exception_handler(request: Request, exc: LearningHouseException):  # pylint: disable=unused-argument
    return exc.response()
