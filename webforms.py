from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea


# Create a Form Class
class NamerForm(FlaskForm) :
    name = StringField("What is your name ?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create User Form Class
class UsersForm(FlaskForm) :
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    favorte_color = StringField("Favorite Color")
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo("password_hash2", message="Password Must Match")])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Login Form Class
class TestLoginForm(FlaskForm) :
    email = StringField("E-mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Login Form Class
class LoginForm(FlaskForm) :
    username = StringField("UserName", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PostsForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("Submit")

