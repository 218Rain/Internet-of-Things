#用户认证
# Flask-HttpAuth
#1.安装Flask-HttpAuth
#2.导入类

from flask_httpauth import HTTPBasicAuth
from flask import jsonify
from . import api
from app.models import User
from flask import request

#g是一个全局有效的变量（对象）
from flask import g

auth = HTTPBasicAuth()

# auth.login_required
# auth.error_handler
# auth.verify_password

#问：email_token和password从哪里来？
#答：从http请求头中来
@auth.verify_password
def verify_user(email_token, password) :
    # print('email_token:' + email_token)
    # print('password:' + password)

    if len(email_token) == 0 :
        return False

    #token
    if len(password) == 0:
        user = User.check_api_token(email_token)
        if user is None :
            return False
        g.current_user = user
        return True

    #email password
    user = User.query.filter_by(email=email_token).first()
    if user is None :
        print('******')
        return False
    if user.check_password(password) :
        g.current_user = user
        return True

    return False

@auth.error_handler
def error() :
    return jsonify({'status':123, 'info':'auth error'})

@api.route('/')
@auth.login_required
def test() :
    return jsonify({'status':200, 'info':'welcom'})

@api.route('/token')
@auth.login_required
def token() :
    return jsonify({'status':200, 'token':g.current_user.api_token})

#获取自己所有设备的API
@api.route('/devices')
@auth.login_required
def devices() :
    ds = g.current_user.devices.all()
    dlist = []
    for d in ds :
        dlist.append(d.to_json())

    return jsonify({'status':200, 'devices':dlist})

#上传数据
from app.models import Data
from app import db
@api.route('/device/<int:did>/sensor/<int:sid>/data', methods=['POST'])
@auth.login_required
def data(did, sid) :
    #print(type(request.json), request.json)
    device = g.current_user.devices.filter_by(id=did).first()
    if device is None :
        return jsonify({'status':404, 'info':'找不到你的设备'})

    sensor = device.sensors.filter_by(id=sid).first()
    if sensor is None :
        return jsonify({'status':404, 'info':'找不到你的传感器'})

    if request.json is None :
        return jsonify({'status': 404, 'info': '找不到你的数据'})

    if 'data' not in request.json.keys() :
        return jsonify({'status': 404, 'info': '找不到你的传感器'})

    #在这里判断要不要报警
    data = Data()
    data.data = request.json.get('data')
    data.sensor_id = sid
    db.session.add(data)
    db.session.commit()
    #
    # if int(request.json.get('data')) > int(sensor.max):
    #     pass
    return jsonify({'status':300})

# 下载数据
@api.route('/device/<int:did>/sensor/<int:sid>/all_data', methods=['GET'])
@auth.login_required
def all_data(did, sid):
    device = g.current_user.devices.filter_by(id=did).first()
    if device is None :
        return jsonify({'status':404, 'info':'找不到你的设备'})
    sensor = device.sensors.filter_by(id=sid).first()
    if sensor is None:
        return jsonify({'status': 404, 'info': '找不到你的传感器'})
    s_data = sensor.datas.all()
    s_datalist = []
    for i in s_data:
        s_datalist.append(i.to_json())
    return jsonify({'status': 200, 'data':s_datalist})


# 下载传感器
from app.models import Sensor
@api.route('/device/<int:did>/sensors', methods=['GET'])
@auth.login_required
def sensors(did):
    if did is None:
        return jsonify({'status': 404, 'info': '找不到你的传感器ID'})
    sensors = Sensor.query.filter_by(devices_id=did)
    if sensors is None:
        return jsonify({'status': 404, 'info': '找不到你的设备'})
    sensor_list = []
    for i in sensors:
        sensor_list.append(i.to_json())
    return jsonify({'status': 200, 'sensors':sensor_list})


