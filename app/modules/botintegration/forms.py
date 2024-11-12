from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class BotIntegrationForm(FlaskForm):
    parent_id = StringField(
        "Parent ID",
        validators=[DataRequired()]
    )
    name = StringField(
        "Name",
        validators=[Length(min=2, max=255)]
    )
    option = SelectField(
        "Options",
        choices=[],
        validators=[DataRequired()]
    )
    submit = SubmitField("Añadir")
