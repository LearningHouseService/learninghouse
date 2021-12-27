from fastapi import APIRouter
from fastapi.openapi.docs import (get_swagger_ui_html,
                                  get_swagger_ui_oauth2_redirect_html)

from starlette.responses import HTMLResponse

from learninghouse.core.settings import service_settings

settings = service_settings()

router = APIRouter(include_in_schema=False)


if settings.docs_url is not None:
    @router.get(settings.docs_url)
    async def custom_swagger_ui_html() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=settings.openapi_url,
            title=settings.title + " - Swagger UI",
            oauth2_redirect_url=settings.oauth2_redirect_url,
            swagger_js_url="/static/docs/swagger-ui-bundle.js",
            swagger_css_url="/static/docs/swagger-ui.css",
            swagger_favicon_url="/static/favicon.ico",
        )

    if settings.oauth2_redirect_url:
        @router.get(settings.oauth2_redirect_url)
        async def swagger_ui_redirect() -> HTMLResponse:
            return get_swagger_ui_oauth2_redirect_html()
