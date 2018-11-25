from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class RegisterForm(FlaskForm):
    email = StringField(label='邮箱', validators=[DataRequired(), Email(), Length(6, 128)])
    name = StringField(label='昵称', validators=[DataRequired(), Length(2, 128)])
    password = PasswordField(label='密码', validators=[DataRequired(), Length(1, 128)])
    password_again = PasswordField(label='确认密码', validators=[EqualTo('password', '两次密码不一致')])
    submit = SubmitField(label='')
    # 唯一性验证
    def validate_email(self, field):
        user = User.query.filter_by(email = field.data).first()
        if user is not None:
            # 会被表单捕获
            raise ValidationError('邮箱已存在')

class SheBeiFrom(FlaskForm):
    device_name = StringField(label='设备名字', validators=[DataRequired(), Length(2, 128)])
    device_description = TextAreaField(label='设备描述', validators=[DataRequired()])
    device_address = TextAreaField(label='设备地址', validators=[DataRequired()])
    submit = SubmitField(label='')

class ChuanGanQiFrom(FlaskForm):
    sensors_name = StringField(label='传感器名字', validators=[DataRequired(), Length(2, 128)])
    sensors_description = TextAreaField(label='传感器描述', validators=[DataRequired()])
    sensors_unit = StringField(label='传感器单位', validators=[DataRequired(), Length(2, 128)])
    submit = SubmitField(label='')

class EditSBForm(FlaskForm):
    e_name = StringField(label='设备名字', validators=[DataRequired(), Length(2, 128)])
    e_description = TextAreaField(label='设备描述', validators=[DataRequired()])
    e_address = TextAreaField(label='设备地址', validators=[DataRequired()])
    submit = SubmitField(label='')
