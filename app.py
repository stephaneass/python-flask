from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea

app = Flask(__name__)
app.config['SECRET_KEY'] = "My Super Secret Key"
#Config database
# For SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#For MySql
## Échappez le caractère @ dans le mot de passe
password = 'stephaneP%40ssw0rd'
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://stephane:{password}@localhost/flaskers"
#Init database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create a Form Class
class NamerForm(FlaskForm) :
    name = StringField("What is your name ?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create User Form Class
class UsersForm(FlaskForm) :
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired()])
    favorte_color = StringField("Favorite Color")
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo("password_hash2", message="Password Must Match")])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Login Form Class
class LoginForm(FlaskForm) :
    email = StringField("E-mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PostsForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("Submit")

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    favorte_color = db.Column(db.String(30))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    #Do some password stuff!
    password_hash = db.Column(db.String(255))

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")
    
    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def verify_password(self, pwd) : 
        return check_password_hash(self.password_hash, pwd)

    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

#Index route
@app.route("/")
def index():
    flash("Welcome to our site!")
    return render_template("index.html")

#Profile route
@app.route("/user/<name>")
def user_profile(name):
    return render_template("profile.html", name=name)

@app.route("/name", methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Form submitted successfully!")

    return render_template("name.html", name = name, form = form)

# Create or add new user
@app.route("/new-user", methods=['GET', 'POST'])
def new_user():
    name = None
    email = None
    favorte_color = None
    form = UsersForm()
    # Validate form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name = form.name.data, email = form.email.data, 
                         favorte_color = form.favorte_color.data,
                         password = form.password_hash.data)
            db.session.add(user)
            db.session.commit()
            flash("User added successfully!")

        name = form.name.data
        form.name.data = ""
        form.email.data = ""
        form.favorte_color.data = ""
        form.password_hash.data = ""
        form.password_hash.data = ""

    all_users = Users.query.order_by(Users.date_added)

    return render_template("new_user.html", name = name, email = email, 
                           favorte_color = favorte_color, form = form, all_users = all_users)

@app.route("/user/<int:id>", methods=['GET', 'POST'])
def update_user(id):
    form = UsersForm()
    user = Users.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.favorte_color = request.form['favorte_color']
        try :
            db.session.commit()
            flash("User updated successfully")
            return redirect(url_for('new_user'))
        except :
            flash("An error occured")
            return redirect(url_for('new_user'))
    else :
        return render_template("update_user.html", form=form, user = user)

@app.route("/login", methods=['GET', 'POST'])
def login():
    email = None
    password = None
    form = LoginForm()
    # Validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        form.email.data = ""
        form.password.data = ""
        user = Users.query.filter_by(email = email).first()
        if user is not None :
            passed = user.verify_password(password)
            if passed :
                flash("Logged In Successfully")
                return redirect(url_for("new_user"))
            else :
                flash("Credentials failed", category='error')
        else :
            flash("Credentials not corrected")

    return render_template("login.html", email = email, password = password, form = form)

@app.route("/delete/<int:id>")
def delete(id):
    user = Users.query.get_or_404(id)
    try :
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully")
        return redirect(url_for("new_user"))
    except :
        flash("Whooops! An error occured")
        return redirect(url_for("new_user"))

@app.route("/posts", methods=["GET", "POST"])
def posts():
    form = PostsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        author = form.author.data
        slug = form.slug.data
        form.title.data = ""
        form.content.data = ""
        form.author.data = ""
        form.slug.data = ""

        post = Posts(title = title, content = content, author = author, slug = slug)
        try : 
            db.session.add(post)
            db.session.commit()
            flash("Post saved successfully")
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            flash("Whoooops!!! An error occured")

    posts = Posts.query.order_by("created_at")
    return render_template("post_new.html", form = form, posts = posts)

@app.route("/post/<int:id>")
def show_post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post_show.html", post = post)

@app.route("/post/edit/<int:id>", methods=['GET', 'POST'])
def edit_post(id) :
    post = Posts.query.get_or_404(id)
    form = PostsForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        try : 
            db.session.commit()
            flash("Post updated successfully")
            return redirect(url_for('posts'))
        except Exception as err:
            print(f"The error is {err=}")
            flash("Whaooooops !!! An error occured")
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template("post_edit.html", form=form)

@app.route('/post/delete/<int:id>')
def delete_post(id) :
    post = Posts.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully")
    return redirect(url_for('posts'))

#Invalid URL
@app.errorhandler(404)
def page_not_found(e) :
    return render_template("400.html"), 404

#Server error
@app.errorhandler(500)
def page_not_found(e) :
    return render_template("500.html"), 500

if __name__ == '__main__' : 
    app.run(debug=True)