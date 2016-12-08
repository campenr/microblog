from microblog import db, app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.validators import Email


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class EditProjectForm(FlaskForm):
    title = StringField ('title')
    body = TextAreaField('body')
    private = BooleanField('private')
    save = SubmitField('save')


class EditPostForm(FlaskForm):
    body = TextAreaField('body')
    private = BooleanField('private')
    save = SubmitField('save')