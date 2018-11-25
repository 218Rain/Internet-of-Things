from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired, Length
# 发表文章
class PostEssay(FlaskForm):
    title = StringField(label='标题', validators=[DataRequired(), Length(1, 128)])
    body = TextAreaField(label="正文", validators=[DataRequired()])
    submit = SubmitField(label="")