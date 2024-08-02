from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = "My Super Secret Key"

# Create a Form Class
class NamerForm(FlaskForm) :
    name = StringField("What is your name ?", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Index route
@app.route("/")
def index():
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

    return render_template("name.html", name = name, form = form)

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