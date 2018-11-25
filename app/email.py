from app import mail
from flask_mail import Message
from threading import Thread
from flask import current_app

# 发送同步邮件，调用此函数的时候会阻塞，也就是说会导致页面卡顿
def send_sync_email(subject, recvs, body, html):
    # html如果为空为空的话body有效，recipients：接收者（是一个列表），body：文本（优先级低于html），html：发送内容
    msg = Message(subject=subject, recipients=recvs, body=body, html=html)
    msg.sender = current_app.config['MAIL_USERNAME']    # 发送者
    # 发送，在不同的线程中获取到，把app对象传递给线程
    # 上下文：环境：变量、函数、内存
    with current_app.app_context():
        mail.send(msg)


# 发送异步邮件
def send_async_email(subject, recvs, body, html) :
    msg = Message(subject=subject, recipients=recvs, body=body, html=html)
    msg.sender = current_app.config['MAIL_USERNAME']
    # 获取current_app代理的正真的app
    app = current_app._get_current_object()
    thead = Thread(target=send_email, args=[app, msg])
    thead.start()

def send_email(app, msg):
    with app.app_context():
        mail.send(msg)


