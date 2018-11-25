from urllib.request import urlopen
import json
import requests

def get_token() :
    header = {'content-type':'application/json'}
    try :
        response = requests.get('http://127.0.0.1:5000/api/1_0/token', headers=header, auth=('1934237939@qq.com', '123456'), timeout=1);
    except :
        print('timeout1')
        return
    s = response.content.decode('utf-8')
    data = json.loads(s)
    return data['token']

# 上传数据
def upload_data(token, dev_id, sen_id, value) :
    header = {'content-type':'application/json'}
    auth = (token, '')
    url = 'http://127.0.0.1:5000/api/1_0/device/{}/sensor/{}/data'
    url = url.format(dev_id, sen_id)
    d = {'data':value}
    try :
        response = requests.post(url, headers=header, auth=auth, data=json.dumps(d), timeout=1)
        print(response.content)
    except :
        print('timeout3')
        return

# 下载数据


import time
token = get_token()
data = 22.5
while True :
    data += 1.3
    upload_data(token, 1, 1, data)
    time.sleep(5)
    if data > 50 :
        data = 22.5

#测试
#upload_data(get_token(), 20, 68, 1)
#status = get_status(get_token(), 20, 68)
#print(status)
#ht = get_hum_temp()
#print(ht)
#token = get_token()
#print(token)
