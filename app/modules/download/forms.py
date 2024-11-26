from flask_wtf import FlaskForm
from wtforms import SubmitField


class DownloadForm(FlaskForm):
    submit = SubmitField('Save download')
