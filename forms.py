from flask_wtf import Form
from wtforms import PasswordField, TextField, TextAreaField, BooleanField, IntegerField, HiddenField
from wtforms import SubmitField, StringField
from wtforms.fields.html5 import EmailField
from wtforms import validators
from wtforms.validators import Length


class EditProfileForm(Form):
    name = StringField('Real Name', validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0,64)])
    about_me = TextAreaField('About Me')
    submit = SubmitField('Submit')


class User_EditForm(Form):
    name = HiddenField("name")
    location = HiddenField("Location", validators=[Length(0,64)])
    about_me = HiddenField('About Me')
    email = HiddenField('Email', validators=[validators.DataRequired(), Length(1, 64), EmailField()])
    confirmed = IntegerField("Confirmed")
    role = IntegerField('role')


class PostForm(Form):
    body = HiddenField("Type Blog content here.", validators=[validators.DataRequired()])
    title = TextField("Put your Blog post title here...", validators=[validators.DataRequired()])
    submit = SubmitField("Submit")


class CommentForm(Form):
    body = TextAreaField("Type your comment here...", validators=[validators.DataRequired()])
    submit = SubmitField("Post Comment")

class ContactForm(Form):
    name = StringField('Real Name', validators=[Length(0, 64)])
    email = StringField('Email', validators=[validators.DataRequired(), Length(1, 64)])
    message = TextAreaField("Type your message here", validators=[validators.DataRequired()])
    submit = SubmitField("Send")