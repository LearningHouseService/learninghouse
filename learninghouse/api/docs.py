from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import HTMLResponse

from learninghouse.core.settings import service_settings

settings = service_settings()

router = APIRouter(include_in_schema=False)


@router.get(settings.docs_url)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=settings.openapi_file,
        title=settings.title + " - Swagger UI",
        oauth2_redirect_url=None,
        swagger_js_url="/static/docs/swagger-ui-bundle.js",
        swagger_css_url="/static/docs/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico",
    )
