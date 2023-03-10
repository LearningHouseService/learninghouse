from os import path
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse

from learninghouse.api.errors import LearningHouseSecurityException
from learninghouse.core.settings import service_settings

settings = service_settings()

router = APIRouter(include_in_schema=False)

UI_DIRECTORY = str(Path(__file__).parent.parent / 'ui')


def is_ui_installed() -> bool:
    return path.exists(UI_DIRECTORY)


if is_ui_installed():
    ASSETS_DIRECTORY = f'{UI_DIRECTORY}/assets'

    with open(f'{ASSETS_DIRECTORY}/env.template.js', 'r', encoding='utf-8') as template_file:
        content = template_file.read()
        content = content.replace(
            '${LEARNINGHOUSE_API_URL}', f'{settings.base_url_calculated}/api')

        with open(f'{ASSETS_DIRECTORY}/env.js', 'w', encoding='utf-8') as dest_file:
            dest_file.write(content)

    @router.get('/')
    async def redirect_root():
        return RedirectResponse('/ui')

    @router.get('/ui{ui_path:path}')
    async def get_ui(ui_path: str):
        if ui_path and ui_path != '/':
            fullpath = path.normpath(f'{UI_DIRECTORY}{ui_path}')
            if not fullpath.startswith(UI_DIRECTORY):
                raise LearningHouseSecurityException(
                    'Requested file name breaks directory structure')

            if not path.exists(fullpath):
                fullpath = f'{UI_DIRECTORY}/index.html'
        else:
            fullpath = f'{UI_DIRECTORY}/index.html'

        return FileResponse(fullpath)
