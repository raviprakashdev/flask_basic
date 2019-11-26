from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
# from flask_mail import  Mail

local_server = "True"
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key= 'super-secret-key'
# app.config.update(
#     Mail_SERVER='smtp.gmail.com',
#     MAIL_PORT='465',
#     MAIL_USE_SSL=True,
#     MAIl_USERNAME=params['gmail-user'],
#     MAIL_PASSWORD=params['gmail-password']
# )
# mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

class Contact(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)
class Post(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(12), nullable=False)
    tag_line = db.Column(db.String(12), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts = Post.query.filter_by().all()[0:5]
    return render_template('index.html', params=params, posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user']==params['admin_user']:
        return render_template('dashboard.html')

    if request.method=='POST':
       username = request.form.get('uname')
       userpass = request.form.get('pass')
       if (username == params['admin_user'] and userpass == params['admin_pass']):
           session['user'] = username
           return render_template('dashboard.html')

    return render_template('login.html', params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()

    return render_template('post.html', params=params, post=post)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the data base'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')
        entry = Contact(name=name, phone=phone, date=datetime.now(), msg=msg, email=email)
        db.session.add(entry)
        db.session.commit()
        # mail.send_message('new msg from blog',
        #                   sender=email,
        #                   recipients=[params['gmail-user']],
        #                   body=msg + "\n" + phone
        #                   )
    return render_template('contact.html', params=params)




app.run(debug=True)