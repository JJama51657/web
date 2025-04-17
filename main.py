from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request, session
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm, registerff, loginform, Commentform
from flask_session import Session
from functools import wraps
import smtplib
import os
from dotenv import load_dotenv
'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt
CVworthyprojects.py
On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("app_secretkey")
ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login

Lgrequired = login_required
# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts6.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
loginmanager = LoginManager()
loginmanager.init_app(app)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


# TODO: Create a User table for all your registered users.


class User(db.Model, UserMixin):
    __tablename__ = "Authors1"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    posts = relationship('BlogPost', back_populates="author")
    comments = relationship('comments', back_populates='commentors')


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("Authors1.id"))
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(
        String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    fans = relationship("comments", back_populates='Bgpost')


class comments(db.Model):
    __tablename__ = "User_Comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    commend_id: Mapped[int] = mapped_column(Integer, ForeignKey("Authors1.id"))
    text: Mapped[str] = mapped_column(String)
    commentors = relationship('User', back_populates='comments')
    Bgpost = relationship('BlogPost', back_populates='fans')
    Bgpost_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("blog_posts.id"))


app.config['SESSION_PROTECTION'] = "strong"
with app.app_context():
    db.create_all()


@loginmanager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)
# TODO: Use Werkzeug to hash the user's password when creating a new user.


@app.route('/register', methods=["POST", "GET"])
def register():
    error = None
    form = loginform()
    registerf = registerff()
    if registerf.validate_on_submit():
        passw = generate_password_hash(
            password=request.form["password"], method='pbkdf2:sha256', salt_length=8)
        user = User(
            email=request.form["email"],
            password=passw,
            name=request.form["name"]
        )

        if db.session.execute(db.select(User).where(User.email == user.email)).scalar():
            error = "You have already signed up with that email\nLogin instead"
            return render_template("login.html", error=error, form=form, current_user=current_user)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=registerf, current_user=current_user)


# TODO: Retrieve a user from the database based on their email.
@app.route('/login', methods=["POST", "GET"])
def login():
    error = None
    form = loginform()
    if form.validate_on_submit():
        if db.session.execute(db.select(User).where(User.email == form.Email.data)).scalar():
            em = db.session.execute(db.select(User).where(
                User.email == form.Email.data)).scalar()
            if check_password_hash(pwhash=em.password, password=form.Password.data):
                result = db.session.execute(db.select(BlogPost))
                posts = result.scalars().all()
                login_user(em)
                return render_template("index.html", all_posts=posts, current_user=current_user)
            else:
                error = "Invalid Password"
                return render_template("login.html", form=form, error=error, current_user=current_user)
        else:
            error = "Invalid Email"
            return render_template("login.html", form=form, error=error, current_user=current_user)
    return render_template("login.html", form=form, current_user=current_user)


@Lgrequired
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


def admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.id != 1:
            abort(403)
        return f(*args, **kwargs)
    return wrap


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    print(posts)
    return render_template("index.html", all_posts=posts, current_user=current_user)


# TODO: Allow logged-in users to comment on posts

@app.route("/post/<int:post_id>", methods=["POST", "GET"])
def show_post(post_id):
    error = None
    commentpost = Commentform()
    requested_post = db.get_or_404(BlogPost, post_id)
    if commentpost.validate_on_submit():
        if not current_user.is_authenticated:
            error = "Login in order to comment!"
            return redirect(url_for("login"))

        newc = comments(
            text=commentpost.body.data,
            commentors=current_user,
            Bgpost=requested_post,
        )
        db.session.add(newc)
        db.session.commit()
    return render_template("post.html", post=requested_post, current_user=current_user, cs=commentpost)


# TODO: Use a decorator so only an admin user can create a new post

@app.route("/new-post", methods=["GET", "POST"])
@admin
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


# TODO: Use a decorator so only an admin user can delete a post

@app.route("/delete/<int:post_id>")
@admin
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


load_dotenv()

adr = os.getenv("email")
passwords = os.getenv("passw")


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        Message = request.form.get("message")
        body = f"Subject:Website Complaint\n\n{Message}"

        with smtplib.SMTP("smtp.gmail.com") as connect:
            connect.starttls()
            connect.login(user=adr, password=passwords)
            connect.sendmail(from_addr=request.form.get("email"), to_addrs=adr,
                             msg=body)
    return render_template("contact.html", current_user=current_user)


if __name__ == "__main__":
    app.run(debug=False, threaded=False, port=5002)
