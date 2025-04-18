from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired


class NotesForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    information = StringField('Informaton', validators=[DataRequired()])
    is_anon = BooleanField("Anonymously?")
    submit = SubmitField('Submit')