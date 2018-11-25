import pymysql
from app import create_app
pymysql.install_as_MySQLdb()
app = create_app('iot_develop')

from flask_script import Manager
from app import db
from flask_migrate import Migrate, MigrateCommand
# 必须在app之后
manager = Manager(app)
migrate = Migrate(app, db)  # 创建一个数据库迁移对象（修改表）
manager.add_command('db', MigrateCommand)   # 增加一条命令叫做db

from app.models import User, Device, Sensor
def make_context():
    return dict(db=db, User=User, Device=Device, Sensor=Sensor)

from flask_script import Shell
manager.add_command('shell', Shell(make_context=make_context))

# 导入app/models.py的Role类（角色类）
from app.models import Role
@manager.command
def init() :
    # 执行创建角色
    Role.create_roles()


manager.run()