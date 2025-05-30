from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Create a RegisterForm to register new users
class registerff(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField("Submit")

# TODO: Create a LoginForm to login existing users


class loginform(FlaskForm):
    Email = StringField('Email', validators=[DataRequired()])
    Password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# TODO: Create a CommentForm so users can leave comments below posts


class Commentform(FlaskForm):
    body = CKEditorField("Comment Secion")
    submit = SubmitField("Submit")