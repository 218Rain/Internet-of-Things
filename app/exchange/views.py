from . import exchange
from flask_login import login_required
from flask import render_template

# 发表文章
from .forms import PostEssay
from app.models import Essay
from flask_login import current_user
from app import db
from flask import redirect, url_for
@exchange.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = PostEssay()
    if form.validate_on_submit():
        essay = Essay()
        essay.title = form.title.data
        essay.body = form.body.data
        essay.user_id = current_user.id
        db.session.add(essay)
        db.session.commit()
        return redirect(url_for('main.all_news'))
    return render_template('exchange/add.html', form = form)

# 全部帖子
from flask import request
from app.models import Essay
@exchange.route('/all_news')
def all_news() :
    page = request.args.get('page', type=int, default=1)
    paginate = Essay.query.paginate(page=page, per_page=5, error_out=False)
    return render_template('exchange/all_news.html', paginate = paginate)