from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

# Create a Form Class
class NamerForm(FlaskForm) :
    name = StringField("What is your name ?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create User Form Class
class UsersForm(FlaskForm) :
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired()])
    submit = SubmitField("Submit")

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    favory_color = db.Column(db.String(30))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

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
    form = UsersForm()
    # Validate form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name = form.name.data, email = form.email.data)
            db.session.add(user)
            db.session.commit()
            flash("User added successfully!")

        name = form.name.data
        form.name.data = ""
        form.email.data = ""

    all_users = Users.query.order_by(Users.date_added)

    return render_template("new_user.html", name = name, email = email, form = form, all_users = all_users)

@app.route("/user/<int:id>", methods=['GET', 'POST'])
def update_user(id):
    form = UsersForm()
    user = Users.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        try :
            db.session.commit()
            flash("User updated successfully")
            return redirect(url_for('new_user'))
        except :
            flash("An error occured")
            return redirect(url_for('new_user'))
    else :
        return render_template("update_user.html", form=form, user = user)

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