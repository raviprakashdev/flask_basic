from flask import Flask,render_template
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/ravi")
def ravi():
    return "Hello Ravi!"

@app.route("/about")
def about():
    name = "Ravi Prakash"
    return render_template('about.html', name=name)


app.run(debug=True)