#coding: utf-8

from flask import Flask
from flask_restful import Api 
from .model import ModelPrediction, ModelTraining
app = Flask(__name__)
api = Api(app)

api.add_resource(ModelPrediction, '/prediction/<string:model>')
api.add_resource(ModelTraining, '/training/<string:model>')
