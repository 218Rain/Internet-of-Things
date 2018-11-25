from . import auth
from app import db
from flask import render_template

# 用户界面
from app.models import User, Essay
@auth.route('/user', methods=['GET', 'POST'])
def user():
    page = request.args.get('page', type=int, default=1)
    paginate = User.query.order_by(User.id.desc()).paginate(page=page, per_page=5, error_out=False)

    paginate1 = Essay.query.paginate(page=page, per_page=5, error_out=False)
    return render_template('auth/user.html', paginate=paginate, paginate1 = paginate1)


# 注销
from flask_login import logout_user, login_required
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# 注册
from app.email import send_async_email
from .forms import RegisterForm
from flask import current_app, flash, redirect, url_for
from app.models import Role
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        user.email = form.email.data
        user.name = form.name.data
        user.password = form.password.data
        if user.email == current_app.config['MAIL_USERNAME']:
            # 管理员
            user.role = Role.query.filter_by(name = 'admin').first()
        else:
            user.role = Role.query.filter_by(default = True).first()
        db.session.add(user)
        db.session.commit()
        # 产生API—KEY
        user.generate_api_token();
        # 发送邮件
        token = user.generate_confirmed_token()
        html = render_template('email/register.html', token=token, user_name=user.name)
        send_async_email(subject='验证', recvs=[user.email], body=None, html=html)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form = form)

# 邮件重发
@auth.route('/resend_email')
def resend_email():
    # 发送邮件
    token = current_user.generate_confirmed_token()
    html = render_template('email/register.html', token = token, user_name=current_user.name)
    send_async_email(subject='验证', recvs=[current_user.email], body=None, html=html)
    return redirect(url_for('main.index'))

from flask import request, abort
from flask_login import current_user, login_required
# 处理用户验证：使用该路由之前用户要先登陆
@auth.route('/confirm')
@login_required
def confirm():
    token = request.args.get('token')
    if token is None:
        abort(404)
    if current_user.confirm(token):
        # 认证后用户的界面
        return redirect(url_for('auth.user'))
    # 页面超时
    return render_template('email/resend_email.html')

# 钩子函数
@auth.before_app_request
def before_app_request():
    if current_user.is_authenticated and \
        not current_user.confirmed and \
        request.endpoint[:5] != 'auth.' and \
        request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if not current_user.confirmed :
        return render_template('email/unconfirmed.html')
    # 成功登录
    return redirect(url_for('main.index'))

# 全部设备信息
@auth.route('/shebei')
def shebei():
    page = request.args.get('page', type=int, default=1)
    paginate = Device.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('equipment/shebei.html', paginate=paginate)

# 添加设备信息
from .forms import SheBeiFrom
from app.models import Device
@auth.route('/add_shebei', methods=['GET', 'POST'])
@login_required
def add_shebei():
    form = SheBeiFrom()
    if form.validate_on_submit():
        device = Device()
        device.name = form.device_name.data
        device.describe = form.device_description.data
        device.location = form.device_address.data
        device.user_id = current_user.id

        db.session.add(device)
        db.session.commit()
        return redirect(url_for('auth.shebei'))
    return render_template('equipment/add-shebei.html', form = form)

# 删除设备
@auth.route('/delete_shebei')
@login_required
def delete_shebei():
    dev_id = request.args.get("dev_id")
    if dev_id is None:
        abort(404)
    device = Device.query.filter_by(id = dev_id).first()
    if device is None:
        abort(404)
    db.session.delete(device)
    db.session.commit()
    return redirect(url_for('auth.shebei'))

# 修改设备信息
from .forms import EditSBForm
@auth.route('/sbbj', methods=['GET', 'POST'])
def sbbj():
    d_id = request.args.get('dev_id')
    device = Device.query.filter_by(id = d_id).first()
    form = EditSBForm()
    if form.validate_on_submit():
        device.name = form.e_name.data
        device.describe = form.e_description.data
        device.location = form.e_address.data
        db.session.add(device)
        db.session.commit()
        return redirect(url_for('auth.shebei', id=current_user.id))
    return render_template('equipment/edit.html', form=form)

# 传感器信息
@auth.route('/sbxq', methods=['GET', 'POST'])
def sbxq():
    id = request.args.get('id')
    sb = Device.query.filter_by(id = id).first()
    page = request.args.get('page', type=int, default=1)
    paginate = Sensor.query.paginate(page=page, per_page=15, error_out=False)
    return render_template('equipment/sbxq.html', paginate=paginate, sb = sb)

# 添加传感器
from .forms import ChuanGanQiFrom
from app.models import Sensor
@auth.route('/add_cgq', methods=['GET', 'POST'])
@login_required
def add_cgq():
    id = request.args.get('id')
    sen = Device.query.filter_by(id=id).first()
    form = ChuanGanQiFrom()
    if form.validate_on_submit():
        sensor = Sensor()
        sensor.name = form.sensors_name.data
        sensor.describe = form.sensors_description.data
        sensor.unit = form.sensors_unit.data
        sensor.devices_id = sen.id
        db.session.add(sensor)
        db.session.commit()
        return redirect(url_for('auth.shebei'))
    return render_template('equipment/add-chuanganqi.html', form = form)

# 删除传感器
@auth.route('/delete_cgq')
@login_required
def delete_cgq():
    sen_id = request.args.get("sen_id")
    id = request.args.get('dev_id')
    devices = Device.query.filter_by(id = id).first()
    if id is None:
        abort(404)
    sensor = Sensor.query.filter_by(id = sen_id).first()
    if sensor is None:
        abort(404)
    db.session.delete(sensor)
    db.session.commit()
    return redirect(url_for('.sbxq',id=devices.id))

# 传感器折线数据
from app.models import Data
@auth.route('/cgqsj')
@login_required
def cgqsj():
    sensor_id = request.args.get('sen_id', type=int, default=1)
    device_id = request.args.get('dev_id', default=1, type=int)
    device = current_user.devices.filter_by(id = device_id).first()
    if not device:
        abort(404)
    sensor = device.sensors.filter_by(id = sensor_id).first()
    if not sensor:
        abort(404)
    page = request.args.get('page', default=1, type=int)
    paginate = sensor.datas.order_by(Data.timestamp.desc()).paginate(page=page, per_page=20, error_out=False)
    dataCount = int(len(paginate.items) / 3)
    data1 = paginate.items[0:dataCount]
    data2 = paginate.items[dataCount:dataCount * 2]
    data3 = paginate.items[dataCount * 2:]

    xlist = []
    ylist = []
    items = paginate.items[::-1]
    for data in items:
        xlist.append(data.timestamp.strftime('%y-%m-%d %H:%M:%S'))
        ylist.append(data.data)
    return render_template('equipment/sd-cgq.html', sensor = sensor, data1 = data1, data2 = data2, data3 = data3, \
                           paginate = paginate, xDataArray = xlist, yDataArray = ylist, page = page, device = device)

@auth.route('/cgq')
def cgq():
    page = request.args.get('page', type=int, default=1)
    # order_by(News.id.desc())降序
    paginate = Sensor.query.order_by(Sensor.id.desc()).paginate(page=page, per_page=5, error_out=False)
    return render_template('equipment/sbxq.html', paginate = paginate)

# 设备报警
from app.models import Alert
@auth.route('/baojin')
def baojin():
    page = request.args.get('page', type=int, default=1)
    paginate = Alert.query.order_by(Alert.id.desc()).paginate(page=page, per_page=5, error_out=False)
    return render_template('equipment/baojing.html', paginate=paginate)

