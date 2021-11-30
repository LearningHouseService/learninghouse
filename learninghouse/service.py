from fastapi import FastAPI
import uvicorn


from learninghouse import versions, logger
from learninghouse.brain import register as brain_register_api

APP_REFERENCE = "learninghouse.service:app"

app = FastAPI(
    title='learningHouse Service',
    version=versions.service)
app = brain_register_api(app)


def run(production, host, port):
    logger.info('Running LearningHouse service % s', versions.service)
    logger.info('Libraries scikit-learn (%s), pandas(%s), numpy(%s), FastAPI(%s)',
                versions.sklearn, versions.pandas, versions.numpy, versions.fastapi)

    if production:
        logger.info('Running in production mode')
        uvicorn.run(APP_REFERENCE, host=host, port=port)
    else:
        logger.info('Running in development mode')
        uvicorn.run(APP_REFERENCE, host=host, port=port, reload=True)
