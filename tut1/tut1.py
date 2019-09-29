from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('home.html')


@app.route("/ravi")
def ravi():
    return "<h1 style='color:red;'>Hello Ravi</h1>"


@app.route("/about")
def about():
    return render_template('about.html')


app.run(debug=True)
