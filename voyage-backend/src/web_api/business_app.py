from flask import Flask
from waitress import serve
import logging as logger

logger.basicConfig(level=logger.INFO)

business_app = Flask(__name__)


def run():
    serve(business_app, host="0.0.0.0", port=8080)
