#coding: utf-8
import logging

from flask import Flask
from flask_restful import Api
from paste.translogger import TransLogger
from waitress import serve

from . import __version__, logger
from .model import ModelAPI, ModelPrediction, ModelTraining

app = Flask(__name__)
api = Api(app)

api.add_resource(ModelPrediction, '/prediction/<string:model>')
api.add_resource(ModelTraining, '/training/<string:model>')
api.add_resource(ModelAPI, '/info/<string:model>')


def run(production, host, port):
    if production:
        logger.info('Running learninghouse %s in production mode', __version__)
        serve(TransLogger(app, logger=logger), host=host, port=port)
    else:
        logger.info('Running learninghouse %s in development mode', __version__)
        app.run(host=host, port=port, debug=False)
