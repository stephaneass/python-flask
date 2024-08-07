from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, TestLoginForm, PostsForm, NamerForm, UsersForm

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

#Flask-Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorte_color = db.Column(db.String(30))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    #Do some password stuff!
    password_hash = db.Column(db.String(255))

    # relationship
    posts = db.relationship('Posts', backref='user')

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
    author = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    #add foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#Index route
@app.route("/")
def index():
    flash("Welcome to our site!")
    return render_template("index.html")

#Profile route
@app.route("/user/<name>")
@login_required
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
    username = None
    form = UsersForm()
    # Validate form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(username = form.username.data, name = form.name.data, 
                         email = form.email.data, favorte_color = form.favorte_color.data,
                         password = form.password_hash.data)
            db.session.add(user)
            db.session.commit()
            flash("User added successfully!")

        name = form.name.data
        form.name.data = ""
        form.email.data = ""
        form.username.data = ""
        form.favorte_color.data = ""
        form.password_hash.data = ""
        form.password_hash2.data = ""

    all_users = Users.query.order_by(Users.date_added)

    return render_template("new_user.html", name = name, username = username, email = email, 
                           favorte_color = favorte_color, form = form, all_users = all_users)

@app.route("/user/<int:id>", methods=['GET', 'POST'])
@login_required
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

@app.route("/test-login", methods=['GET', 'POST'])
def test_login():
    email = None
    password = None
    form = TestLoginForm()
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

    return render_template("test_login.html", email = email, password = password, form = form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    username = None
    password = None
    form = LoginForm()
    # Validate form
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        form.username.data = ""
        form.password.data = ""
        user = Users.query.filter_by(username = username).first()
        if user is not None :
            passed = user.verify_password(password)
            if passed :
                login_user(user)
                flash("Logged In Successfully")
                return redirect(url_for("dashboad"))
            else :
                flash("Credentials failed", category='error')
        else :
            flash("Credentials not corrected")

    return render_template("login.html", form = form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("User logged out successfull")
    return redirect(url_for('login'))

@app.route("/delete/<int:id>")
@login_required
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
@login_required
def posts():
    form = PostsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        slug = form.slug.data
        form.title.data = ""
        form.content.data = ""
        form.author.data = ""
        form.slug.data = ""

        post = Posts(title = title, content = content, user_id = current_user.id, slug = slug)
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
@login_required
def show_post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post_show.html", post = post)

@app.route("/post/edit/<int:id>", methods=['GET', 'POST'])
@login_required
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
@login_required
def delete_post(id) :
    post = Posts.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully")
    return redirect(url_for('posts'))

@app.route('/dashboad')
@login_required
def dashboad():
    return render_template('dashboad.html')

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