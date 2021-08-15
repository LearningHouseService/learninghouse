#coding: utf-8

from flask import Flask
from flask_restful import Api

from waitress import serve

from . import __version__

from .model import ModelPrediction, ModelTraining, ModelAPI

print(__version__)

app = Flask(__name__)
api = Api(app)

api.add_resource(ModelPrediction, '/prediction/<string:model>')
api.add_resource(ModelTraining, '/training/<string:model>')
api.add_resource(ModelAPI, '/info/<string:model>')


def run(production, host, port):
    if production:
        serve(app, host=host, port=port)
    else:
        app.run(host=host, port=port, debug=False)
