from flask import Blueprint

exchange = Blueprint('exchange', __name__)

from . import views