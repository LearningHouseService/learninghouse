from flask import Flask, __version__ as flask_version
from flask_restful import Api
from paste.translogger import TransLogger
from waitress import serve

from sklearn import __version__ as skl_version
from pandas import __version__ as pd_version
from numpy.version import version as np_version

from . import __version__, logger
from .model import ModelAPI, ModelPrediction, ModelTraining

app = Flask(__name__)
api = Api(app)

api.add_resource(ModelPrediction, '/prediction/<string:model>')
api.add_resource(ModelTraining, '/training/<string:model>')
api.add_resource(ModelAPI, '/info/<string:model>')


def run(production, host, port):
    logger.info('Running LearningHouse service % s', __version__)
    logger.info('Libraries scikit-learn (%s), pandas(%s), numpy(%s), flask(%s)',
                skl_version, pd_version, np_version, flask_version)

    if production:
        logger.info('Running in production mode')
        serve(TransLogger(app, logger=logger), host=host, port=port)
    else:
        logger.info('Running in development mode')
        app.run(host=host, port=port, debug=False)
