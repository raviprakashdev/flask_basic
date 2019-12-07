from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
import math
import json
import os
from datetime import datetime
# from flask_mail import  Mail

local_server = "True"
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
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
    posts = Post.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))

    # pagination logic
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page=int(page)
    posts = posts[(page-1) * int(params['no_of_posts']):(page-1) * int(params['no_of_posts']) + int(params['no_of_posts'])]
    if(page==1):
        prev = "#"
        next = "/?page="+str(page+1)
    elif (page==last):
        prev = "/?page="+str(page-1)
        next = "#"
    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)


    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Post.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method=='POST':
       username = request.form.get('uname')
       userpass = request.form.get('pass')
       if (username == params['admin_user'] and userpass == params['admin_pass']):
           session['user'] = username
           posts = Post.query.all()
           return render_template('dashboard.html', posts=posts, params=params)

    return render_template('login.html', params=params)

@app.route("/uploader", methods=['GET', "POST"])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:
        if (request.method=="POST"):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        return "Uploaded successfully"

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()

    return render_template('post.html', params=params, post=post)


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if'user' in session and session['user'] == params['admin_user']:
        post = Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno =='0':
                post = Post(title=box_title,slug=slug,content=content,tag_line=tline,img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Post.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.tag_line = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/'+sno)

        post = Post.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, sno=sno)




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