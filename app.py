from flask import Flask, render_template

app = Flask(__name__)

#Index route
@app.route("/")
def index():
    return render_template("index.html")

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