from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired


class NotesForm(FlaskForm):
    title = StringField('Название места', validators=[DataRequired()])
    location = StringField('Локация', validators=[DataRequired()])
    information = StringField('Описание', validators=[DataRequired()])
    image = FileField('Фотография', validators=[DataRequired()])
    color = StringField('Цвет в RGB(Подсказка внизу)', validators=[DataRequired()])
    is_anon = BooleanField("Анонимно?")
    submit = SubmitField('Submit')