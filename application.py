import datetime
import bcrypt
import config
import smtplib
import os
from flask import Flask, jsonify, session, render_template, request, flash, redirect, url_for, abort, send_from_directory
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_paginate import Pagination
from flask_moment import Moment
from dbhelper import DBHelper
from bson import json_util
from user import User, AnonymousUser
from forms import EditProfileForm, User_EditForm, PostForm, CommentForm, ContactForm
from flask_mail import Mail
from werkzeug.utils import secure_filename


application = Flask(__name__)
application.secret_key = config.app_key_auth
application.jinja_env.add_extension("jinja2.ext.do")
application.jinja_env.add_extension("jinja2.ext.loopcontrols")
login_manager = LoginManager(application)
DB = DBHelper()
moment = Moment(application)
mail = Mail(application)


ROLE_USER = 1
ROLE_MODERATOR = 2
ROLE_ADMINISTRATOR = 3

UPLOAD_FOLDER = config.UPLOAD_FOLDER
ALLOWED_EXTENSIONS = config.ALLOWED_EXTENSIONS


def send_email(user_fromaddress, pwd, recipient, subject, form, confirmation=True, **kwargs):

    gmail_user = user_fromaddress
    gmail_pwd = pwd
    FROM = user_fromaddress
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    contact_msg = "From: %s <%s>\n\n\n Message: %s" % (form.name.data, form.email.data, form.message.data)
    TEXT = render_template('mail.txt', **kwargs) if confirmation is True else contact_msg
    print(form)
    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('successfully sent the email')
    except:
        print("failed to send mail")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS





@application.route('/', defaults={'page':1})
@application.route('/page/<int:page>')
def home(page):
    per_page = 5

    if page is 1:
        start_at = 0
    else:
        start_at = (page * per_page) - per_page

    all_posts = DB.get_all_posts()
    comments = DB.get_comments()
    posts = DB.get_limited_posts(start_at=start_at, per_page=per_page)


    paginate = Pagination(page=page, per_page=per_page, record_name='posts', total=all_posts.__len__(),
                          format_total=True, css_framework='bootstrap3')

    return render_template("post_info.html", form=PostForm(), posts=posts, paginate=paginate, comments=comments)

@application.route('/about')

def about():
    user = DB.get_user_by_name("ljheidrick")

    return render_template('about2-0.html', user=user)

@application.route('/archive' , defaults={'page':1})
@application.route('/archive/page/<int:page>')
def show_archive(page):

    per_page = 10

    if page is 1:
        start_at = 0
    else:
        start_at = (page * per_page) - per_page

    all_posts = DB.get_all_posts()
    comments = DB.get_comments()
    posts = DB.get_limited_posts(start_at=start_at, per_page=per_page)

    paginate = Pagination(page=page, per_page=per_page, record_name='posts', total=all_posts.__len__(),
                          format_total=True, css_framework='bootstrap3')

    return render_template("archive_posts.html", posts=posts, paginate=paginate, comments=comments)


@application.route('/post/<int:id>')
def permalink_post(id):
    post = DB.get_post_id(id)
    user = current_user._get_current_object()
    comments = DB.get_comments_by_author(id)
    DB.update_comment(len(comments), id)
    return render_template("post2-0.html", user=user, comments=comments, posts=post, form=CommentForm())


@application.route('/comment/<int:id>', methods=['POST'])
@login_required
def post_comment(id):
    form = CommentForm()
    user = current_user._get_current_object()

    if form.validate_on_submit:
        DB.insert_comment(request.form['comment_body'], datetime.datetime.utcnow(),
                          user.id, id, False, datetime.datetime.utcnow())
        comments = DB.get_comments_by_author(id)
        DB.update_comment(len(comments), id)
        return redirect(url_for('permalink_post', id=id))
    return url_for('permalink_post', id=id)


@application.route('/change/<int:id>')
@login_required
def post_edit(id):
    post = DB.get_post_id(id)
    return render_template("edit_post.html", form=PostForm(), post=post)


@application.route('/comment/<int:id>/post/<int:post_id>')
@login_required
def comment_disable(id, post_id):
    comment = DB.get_comments_by_id(id)
    is_disabled = True if comment[0]['is_disabled'] == False else False
    DB.mod_comment(is_disabled, id)
    return redirect(url_for('permalink_post', id=post_id))


@application.route('/edit/<int:id>', methods=["POST"])
@login_required
def edit_post(id):
    post = DB.get_post_id(id)
    user = current_user._get_current_object()

    if user.role != ROLE_ADMINISTRATOR or user.id != post[0]['author_id']:
        abort(403)

    form = PostForm()
    if form.validate_on_submit:
        post[0]['body'] = request.form['text_post']
        post[0]['post_title'] = form.title.data
        DB.update_post(post)
        return redirect(url_for('permalink_post', id=post[0]['posts_id']))
    return render_template("edit_post.html", form=form, post=post)


@application.route('/submit_blog_post', methods=["POST"])
def submit_post():
    form = PostForm()
    user = current_user._get_current_object()
    file = request.files['files']
    if form.validate_on_submit and user.role is ROLE_ADMINISTRATOR:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        img_src = os.path.join(UPLOAD_FOLDER, filename)

        DB.create_blog_post(author_id=user.id, body=request.form['text_post'],
                            post_title=form.title.data, post_time=datetime.datetime.now(), modified_time=datetime.datetime.now(), img_src=img_src)

    return redirect(url_for('home'))

@application.route('/contact')
def contact():
    return render_template('contact.html', form=ContactForm())

@application.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@application.route('/confirm')
@login_required
def resend_confirmation():
    user = current_user._get_current_object()
    if user.confirmed:
        return render_template("index.html")
    token = user.generate_confirmation_token()

    send_email(config.from_address, config.mail_password, config.to_address, "Confirmation Email", user=user, token=token)
    return redirect(url_for('home'))


@application.route('/account')
@login_required
def account():
    return render_template("account.html")


@application.route('/user/<username>')
def user(username):
    user = DB.get_user_by_name(username)
    if user is None:
        abort(404)

    user_one = User(user[0]['email'], user[0]['username'], user[0]['password'], user[0]['confirmed'], user[0]['roles_id'])
    posts = DB.get_posts_by_user(user[0]["id"])

    return render_template("user.html", user=user, user_one=user_one, posts=posts)


@application.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        DB.update_user_profile(current_user)
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@application.route('/confirm/<token>')
@login_required
def confirm(token):
    user = current_user._get_current_object()
    if current_user.confirmed:
        print(user.confirmed)
        return redirect(url_for('home'))
    if current_user.confirm(token):
        print('successfully confirmed')
        flash("Thank you for confirming your account!")
        if user.role == ROLE_ADMINISTRATOR:
            return render_template('admin.html')
    else:
        flash("Confirmation link invalid or expired.")
    return redirect(url_for('login'))


@application.route('/register', methods=['POST'])
def create_user():
    form_name = request.form['signup-name']
    form_username = request.form['signup-username']
    form_email = request.form['signup-email']
    form_password = request.form['signup-password']
    form_confirm_password = request.form['signup-password-confirm']

    stored_user = DB.get_user_login(form_email)
    if stored_user:
        error = "Email Address already registered"
        return redirect(url_for('home'))
    hashed = bcrypt.hashpw(str(form_password).encode(), bcrypt.gensalt())

    ROLE = ROLE_ADMINISTRATOR if form_email in config.administrators else ROLE_USER

    DB.create_user(ROLE, form_username, form_name, form_email, datetime.datetime.now(), hashed,
                       datetime.datetime.now(), False)
    user = User(email=form_email, username=form_username, password=hashed, confirmed=False, role=ROLE)
    token = User.generate_confirmation_token(user, expiration=3600)
    send_email(config.mail_username, config.mail_password, config.to_address, "test", user=user, token=token)
    return redirect(url_for('home'))


@application.route('/admin/', defaults={'page':1})
@application.route('/admin/<int:page>')
@login_required
def admin_panel(page):
    all_records = DB.get_all_users()
    user = current_user._get_current_object()
    if user.role != ROLE_ADMINISTRATOR:
        abort(403)

    per_page = 10
    if page is 1:
        start_at = 0
    else:
        start_at = (page * per_page) - per_page

    records = DB.get_limited_users(start_at, per_page)
    paginate = Pagination(page=page, per_page=per_page, record_name='records', total=all_records.__len__(),
                          format_total=True, css_framework='bootstrap3')

    # import json
    # with open('static\\js\\json.js', 'w') as file:
    #     json.dump(all_records, file, default=json_util.default)
    
    return render_template("admin/tables_dynamic.html", records=records, form=User_EditForm(), paginate=paginate)


@application.route('/admin/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    DB.delete_user(id)
    return redirect(url_for('admin_panel'))


@application.route('/send-contact-message', methods=['GET', 'POST'])
def contact_form():
    form = ContactForm()
    f_obj = form.name.data, form.email.data, form.message.data
    print(f_obj)
    send_email(config.mail_username, config.mail_password, config.mail_username,
               subject="A message from website visitor", form=ContactForm(), confirmation=False)
    return redirect(url_for("contact"))


@application.route('/admin/update/<id>', methods=['POST'])
@login_required
def update_user(id):
    user = DB.get_user_by_id(id)
    form = User_EditForm()

    if form.validate_on_submit:
        user[0]['id'] = id
        user[0]['location'] = form.location.data
        user[0]['about_me'] = form.about_me.data
        user[0]['name'] = form.name.data
        user[0]['email'] = form.email.data
        user[0]['confirmed'] = form.confirmed.data
        user[0]['roles_id'] = form.role.data
        DB.update_user(user)
        return redirect(url_for('admin_panel'))

    form.email.data = user[0]['email']
    form.role.data = user[0]['roles_id']
    form.confirmed.data = user[0]['confirmed']
    form.about_me.data = user[0]['about_me']
    form.location.data = user[0]['location']
    form.name.data = user[0]['name']
    return render_template("admin.html", user=user, form=form)


@application.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("home"))


@application.route('/login', methods=['POST'])
def login():

        form_email = request.form['login_email']
        form_password = request.form['password']

        stored_user = DB.get_user_login(form_email)
        print(stored_user)
        hashed = str(stored_user[0]['password']).encode()

        if stored_user and bcrypt.hashpw(str(form_password).encode(), hashed) == hashed:
            user = User(form_email, username=stored_user[0]['username'], password=hashed,
                        confirmed=stored_user[0]['confirmed'], role=stored_user[0]['roles_id'])
            login_user(user, remember=True)
            return redirect(url_for("home"))

        return redirect(url_for("home"))

@application.route('/loginorsignup')
def login_or_signup():
    return render_template('loginorsignup.html')

@login_manager.user_loader
def load_user(user_id):
    stored_user = DB.get_user_login(user_id)
    user_password = str(stored_user[0]['password'].encode())
    if user_password:
        return User(stored_user[0]['email'], username=stored_user[0]['username'], password=user_password,
                    confirmed=stored_user[0]['confirmed'], role=stored_user[0]['roles_id'])

if __name__ == '__main__':
    application.debug = True
    application.run()
