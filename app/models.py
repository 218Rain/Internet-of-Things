from app import db

# 权限类：代表的是网站的功能
class Permission() :
    ADD_DEVICE=0x0001
    DELETE_DEVICE=0x0002
    EDIT_DEVICE=0x0004
    ADD_SENSOR=0x0008
    DELETE_SENSOR=0x0010
    EDIT_SENSOR=0x0020

    ADD_USER=0x0040
    DELETE_USER=0x0080
    EDIT_USER=0x0100

# 用户表
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
class User(db.Model, UserMixin) :
    # 表名
    __tablename__ = 'users'
    # id主键
    id = db.Column(db.Integer, primary_key=True)
    # 邮箱
    email = db.Column(db.String(128))
    # 名字
    name = db.Column(db.String(128), default='李清照')
    # 密码
    password_hash = db.Column(db.String(128))
    # 注册时间，register_time存放的都是修改表（数据库迁移）的时间，存放的是创建User对象的时间
    register_time = db.Column(db.DateTime, default=datetime.utcnow)
    # 最后访问时间
    access_time = db.Column(db.DateTime, default=datetime.utcnow)
    # 是否验证
    confirmed = db.Column(db.Boolean, default=False)
    # 外键，角色
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    #API-KEY(生成邮箱验证的方法，128位）
    api_key = db.Column(db.String(128))
    # 设备的反向关系
    devices = db.relationship('Device', backref='user', lazy='dynamic', cascade='all,delete-orphan')

    # ----------------- 用于邮箱验证 --------------------------
    def generate_confirmed_token(self):
        s = Serializer(secret_key=current_app.config['SECRET_KEY'], expires_in=120)
        # 用户id加密
        token = s.dumps({'id': self.id})
        return token

    def confirm(self, token):
        s = Serializer(secret_key=current_app.config['SECRET_KEY'])
        try:
            # token超时异常
            d = s.loads(token)
        except:
            return False

        if d.get('id') == self.id:
            self.confirmed = True
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def __str__(self):
        return str(self.id) + ':' + self.name

    # 构建一个属性：隐藏细节，截获它
    @property
    def password(self):
        # 密码不能被读取，否则抛出异常
        raise AttributeError('不能读取密码')

    @password.setter
    def password(self, password):
        # 利用sha256+杂质串的方法产生hash方法
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # 验证密码是否正确
        return check_password_hash(self.password_hash, password)

    # ----------------- 实现权限认证方法 --------------------------
    def has_permission(self, permission):
        return self.role.permissions & permission == permission

    def is_admin(self):
        return self.has_permission(0xff)

    #为了支持智能硬件用户验证，添加API_KEY的支持
    #1.生成API—KEY
    api_token = db.Column(db.String(256))

    def generate_api_token(self):
        s = Serializer(secret_key=current_app.config['SECRET_KEY'], expires_in=60*60*24*365*100)
        self.api_token = s.dumps({'id':self.id})
        db.session.add(self)
        db.session.commit()

    #2.获取API—KEY
    def get_api_token(self):
        return self.api_token

    #3.验证API_KEY 如果验证成功返回用户对象，否则返回None
    @staticmethod
    def check_api_token(token):
        s = Serializer(secret_key=current_app.config['SECRET_KEY'])
        try :
            data = s.loads(token)
        except:
            return None
        if 'id' not in data.keys() :
            return None
        return User.query.filter_by(id=int(data['id'])).first()

# 角色模型
class Role(db.Model):
    # 表名
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False)
    users = db.relationship('User', backref='role')
#     #创建角色方法（静态方法）
#         #需要创建3个角色：
#             #普通用户：ADD_DEVICE、DELETE_DEVICE、EDIT_DEVICE、ADD_SENSOR、DELETE_SENSOR，EDIT_SENSOR
#             #企业用户：EDIT_DEVICE、EDIT_SENSOR
#             #管理员：任何权限   0xffff
#
    @staticmethod
    def create_roles():
        roles = {
            'user': [
                Permission.ADD_DEVICE | Permission.DELETE_DEVICE | Permission.EDIT_DEVICE | Permission.ADD_SENSOR \
                | Permission.DELETE_SENSOR | Permission.EDIT_SENSOR,True],
            'company': [Permission.EDIT_DEVICE | Permission.EDIT_SENSOR, False],
            'admin': [0xff, False]
        }

        for r in roles :
            role = Role.query.filter_by(name=r).first()
            if role is None :
                role = Role()
                role.name = r
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

#
# 在模型中添加回调函数
# 以接收以Unicode字符串表示的用户标识符，在logout_user中调用。获取用户后会把该用户设置为匿名用户
from app import login_manager
@login_manager.user_loader
def user_load(id):
    return User.query.get(int(id))

# 设备表
class Device(db.Model):
    # 表名
    __tablename__ = 'devices'
    # id主键
    id = db.Column(db.Integer, primary_key=True)
    # 名字
    name = db.Column(db.String(64))
    # 描述
    describe = db.Column(db.Text)
    # 位置
    location = db.Column(db.String(64))
    # 创建时间
    establish_time = db.Column(db.DateTime, default=datetime.utcnow)
    # 用户 ID（外键）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    #反向关系：
    sensors = db.relationship('Sensor', backref='device', lazy='dynamic', cascade='all,delete-orphan')

    def to_json(self):
        json_data = {
            'id': self.id,
            'name': self.name,
            'user': self.user.name,
        }
        return json_data

# 传感器表
class Sensor(db.Model):
    # 表名
    __tablename__ = 'sensors'
    # id主键
    id = db.Column(db.Integer, primary_key=True)
    #名字
    name = db.Column(db.String(64))
    # 描述
    describe = db.Column(db.Text)
    # 单位
    unit = db.Column(db.String(64))
    # 上限值
    max = db.Column(db.Float)
    # 下限值
    min = db.Column(db.Float)
    # 最近数据
    # 创建时间
    sensor_time = db.Column(db.DateTime, default=datetime.utcnow)
    #设备ID（外键）
    devices_id = db.Column(db.Integer, db.ForeignKey('devices.id', ondelete='CASCADE'))
    #反向关系：
    datas = db.relationship('Data', backref='sensor', lazy='dynamic', cascade='all,delete-orphan')

    def to_json(self):
        json_data = {
            'id': self.id,
            'name': self.name,
            'unit': self.unit,
            'timestamp': self.sensor_time
        }
        return json_data

# 数据表
class Data(db.Model) :
    # 表名
    __tablename__ = 'datas'
    # id主键
    id = db.Column(db.Integer, primary_key=True)
    # 数据（内容）
    data = db.Column(db.Float, default=0)
    #创建时间
    timestamp = db.Column(db.DateTime, default=datetime.now)
    #传感器ID（外键）
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id', ondelete='CASCADE'))
    #反向关系：
        #alerts=xxxxx
    def to_json(self):
        json_data = {
            'id': self.id,
            'data': self.data,
            'timestmap': self.timestamp,
            'sensor': self.sensor.name,
        }
        return json_data

#报警类
class Alert(db.Model) :
    # 表名
    __tablename__ = 'alerts'
    # id主键
    id = db.Column(db.Integer, primary_key=True)
    # 报警数据ID（外键）
    aletr_data_id = db.Column(db.Integer, db.ForeignKey('datas.id', ondelete='CASCADE'))
    # 报警当时的上线
    max = db.Column(db.Integer)
    #报警当时的下限
    min = db.Column(db.Integer)
    #报警时间
    alert_time = db.Column(db.DateTime, default=datetime.utcnow)
    #报警原因
    alert_describe = db.Column(db.Text)

# 匿名用户类，当一个没有登录的用户访问时，那么login_manager会创建一个匿名用户对象
# current_user会代理这个匿名用户
from flask_login import AnonymousUserMixin
class AnonymousUser(AnonymousUserMixin):
    name = '游客'
    def has_permission(self, permission):
        return False
    def is_admin(self):
        return False
    def flush_access_time(self):
        pass

# 文章类
class Essay(db.Model) :
    __tablename__ = 'essays'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    private = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    comment = db.relationship("Comment", backref="essays", lazy="dynamic")

# 评论类
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    color = db.Column(db.Integer)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id", ondelete='CASCADE'))
    essays_id = db.Column(db.Integer,db.ForeignKey("essays.id", ondelete='CASCADE'))


