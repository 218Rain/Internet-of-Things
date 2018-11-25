# 导入蓝本类
from flask import Blueprint
main = Blueprint('main', __name__)
from . import views