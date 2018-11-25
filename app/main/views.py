from . import main
from flask import render_template
from .forms import IndexForm
from app.models import User
from flask import abort
from flask import flash, redirect, url_for

# 主页 | 登录
from flask_login import login_user
@main.route('/', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user is None:
            abort(404)
        if user.check_password(password):
            login_user(user)
            return redirect(url_for('auth.user', id=user.id))
        else:
            flash('密码错误')
            return redirect(url_for('.index'))
    # render_template会去app/templates下找模板
    return render_template('main/index.html', form=form)

# 个人信息主页，没有认证就不能访问
from flask_login import login_required
from flask import request
@main.route('/user_info', methods=['GET', 'POST'])
@login_required
def user_info():
    # 访问视图用户资料视图
    id = request.args.get('id')
    if id is None:
        abort(404)
    user = User.query.filter_by(id = id).first()
    if user is None:
        abort(404)
    return render_template('main/index.html', user=user)

# 管理中心
from app.models import User
@main.route('/glzx', methods=['GET', 'POST'])
@login_required
def glzx():
    page = request.args.get('page', type=int, default=1)
    paginate = User.query.paginate(page=page, per_page=5, error_out=False)
    return render_template('main/glzx.html', paginate=paginate)

# 评论管理
@main.route('/plgl')
@login_required
def plgl():
    return render_template('main/plgl.html')

# 编辑用户
from .forms import EditYHForm
from app import db
from flask_login import current_user
@main.route('/edit_yonghu', methods=['GET', 'POST'])
@login_required
def edit_yonghu():
    id = request.args.get('id')
    user = User.query.filter_by(id=id).first()
    form = EditYHForm()
    if form.validate_on_submit():
        user.name = form.name.data
        user.password = form.password.data
        user.password_again = form.password_again.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('main/edit_yonghu.html', form=form)

# 删除用户
@main.route('/delete_yonghu')
@login_required
def delete_yonghu():
    id = request.args.get('id')
    if id is None:
        abort(404)
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('main.glzx'))



