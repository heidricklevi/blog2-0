import datetime
import hashlib
from flask_login import AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from dbhelper import DBHelper

db = DBHelper()

class User:

    def __init__(self, email, username, password, confirmed, role):
        self.modifified_date = db.get_modified_date_time(email)
        if self.modifified_date is None:
            self.modifified_date = datetime.datetime.now()

        self.registration_date = db.get_registration_date(email)
        self.name = db.get_user_data(email)[0]['name']
        self.location = db.get_user_data(email)[0]['location']
        self.about_me = db.get_user_data(email)[0]['about_me']
        self.id = db.get_user_data(email)[0]['id']
        self.gravatar_hash = db.get_user_data(email)[0]['gravatar_hash']

        if self.gravatar_hash is None and email is not None:
            self.gravatar_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
            db.insert_gravatar_hash(email, self.gravatar_hash)

        self.email = email
        self.password = password
        self.role = role
        self.confirmed = confirmed
        self.username = username

    def ping(self):
        self.modifified_date = datetime.datetime.utcnow()
        db.update_modified_time(self.modifified_date, self.email)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.email})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.email:
            return False
        self.confirmed = True
        print(self)
        db.update_confirmed_state(self)
        return True

    def gravatar(self, size=180, default='identicon', rating='g'):
        if request.is_secure:
            url = "https://secure.gravatar.com/avatar"
        else:
            url = "http://www.gravatar.com/avatar"

        hash = self.gravatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating
        )

    def get_id(self):
        return self.email

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def get_email(self):
        return self.email

    @staticmethod
    def generate_fake_user(count=100):
        from random import seed
        import forgery_py


        seed()
        for i in range(count):

            email = forgery_py.internet.email_address()
            confirmed = True
            password = forgery_py.lorem_ipsum.word()
            role = 1

            name = forgery_py.internet.user_name()
            username = forgery_py.internet.user_name()
            registration_date = forgery_py.date.date(True)
            modifified_date = forgery_py.date.date(False)

            db.create_user(roles_id=role, username=username, name=name, email=email, registration_date=registration_date,
                           password=password, modified_at=modifified_date, confirmed=confirmed)

            u = User(email=email, username=username, password=password, confirmed=confirmed, role=role)

            u.about_me = forgery_py.lorem_ipsum.sentence()
            u.location = forgery_py.address.city()

            db.update_user_profile(u)

    @staticmethod
    def generate_fake_posts(count=100):
        from random import seed, randint
        import forgery_py


        seed()
        users = db.get_all_users()
        for i in range(count):
            user = users[randint(0, users.__len__() - 1)]
            author_id = user['id']
            post_title = forgery_py.lorem_ipsum.word()
            body = forgery_py.lorem_ipsum.sentences(randint(1, 50))
            timestamp = forgery_py.date.date(True)

            db.create_blog_post(author_id=author_id, post_title=post_title, body=body, post_time=timestamp)


class AnonymousUser(AnonymousUserMixin):
    def is_anonymous(self):
        return True
