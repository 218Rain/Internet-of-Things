from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
class IndexForm(FlaskForm) :
    email = StringField(label='邮箱', validators=[DataRequired(), Email(), Length(6,128)])
    password = PasswordField(label='密码', validators=[DataRequired(), Length(1, 128)])
    submit = SubmitField(label='')

class EditYHForm(FlaskForm):
    name = StringField(label='昵称', validators=[DataRequired(), Length(2, 128)])
    password = PasswordField(label='密码', validators=[DataRequired(), Length(1, 128)])
    password_again = PasswordField(label='确认密码', validators=[EqualTo('password', '两次密码不一致')])
    submit = SubmitField(label='')
