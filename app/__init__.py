# 前端框架Bootstrap
from flask_bootstrap import Bootstrap
# 能够将utc时间渲染成当地时间
from flask_moment import Moment
#邮件
from flask_mail import Mail, Message
from flask import Flask
# 数据库
from flask_sqlalchemy import SQLAlchemy
# 导入配置：导入config.py中的config字典
from config import config

# 变量名不能改变
bootstrap = Bootstrap()
moment = Moment()

# 创建login_manager对象：login_manager通过操作session来控制用户的登陆状态
# 通过session的判断来决定用户能够访问的视图函数
from flask_login import LoginManager
login_manager = LoginManager()
# strong，Flask-Login记录客户端IP地址和浏览器的用户代理信息，有异动就退出登录
login_manager.session_protection = 'strong'
# 指定登陆路由，在蓝本auth中的login，访问登陆后才能访问的页面时候重定向的auth.login
login_manager.login_view = 'main.index'

mail = Mail()
# 访问数据库
db = SQLAlchemy()



# 提供一个创建app的函数
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # 绑定app
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # 注册蓝本
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .api1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix = '/api/1_0')

    from .exchange import exchange as exchange_blueprint
    app.register_blueprint(exchange_blueprint, url_prefix = '/exchange')

    return app