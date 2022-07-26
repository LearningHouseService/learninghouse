from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import HTMLResponse

from learninghouse.core.settings import service_settings
from learninghouse.services.authorization import API_KEY_NAME

settings = service_settings()

router = APIRouter(include_in_schema=False)


@router.get(settings.docs_url)
async def custom_swagger_ui_html() -> HTMLResponse:
    response = get_swagger_ui_html(
        openapi_url=settings.openapi_file,
        title=settings.title + " - Swagger UI",
        oauth2_redirect_url=None,
        swagger_js_url="/static/docs/swagger-ui-bundle.js",
        swagger_css_url="/static/docs/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico",
    )

    if settings.api_key_required:
        response.set_cookie(
            API_KEY_NAME,
            value=settings.api_key,
            httponly=True,
            max_age=1800,
            expires=1800
        )

    return response
