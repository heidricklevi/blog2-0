import pymysql
import dbconfig



class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTRATOR = 0x80

class DBHelper():

    def connect(self, database=dbconfig.db_name):
        return pymysql.connect(host=dbconfig.dev_host, user=dbconfig.db_user,
                               passwd=dbconfig.db_password, db=database,
                               cursorclass=pymysql.cursors.DictCursor)\

    def delete_user(self, id):
        conn = self.connect()
        try:
            query = "DELETE FROM blog.users WHERE id = %s;"
            with conn.cursor() as cursor:
                cursor.execute(query, id)
                conn.commit()
        finally:
            conn.close()

    def get_user_by_name(self, username):
        conn = self.connect()
        try:
            query = "SELECT * FROM blog.users WHERE username = %s;"
            with conn.cursor() as cursor:
                cursor.execute(query, username)
                return cursor.fetchall()
        finally:
            conn.close()


    def update_user(self, user):
        conn = self.connect()

        try:
            query = "UPDATE blog.users SET roles_id = %s, name = %s, email = %s," \
                    " registration_date = %s, password = %s, modified_at = %s, confirmed = %s, location = %s, about_me = %s WHERE id = %s"
            with conn.cursor() as cursor:
                cursor.execute(query, (user[0]["roles_id"], user[0]["name"], user[0]["email"],
                                       user[0]["registration_date"], user[0]["password"], user[0]["modified_at"], user[0]["confirmed"],
                                       user[0]["location"], user[0]["about_me"], user[0]["id"]))
                conn.commit()
        finally:
            conn.close()

    def update_post(self, post):
        conn = self.connect()
        try:
            query = "UPDATE blog.posts SET body = %s, post_title = %s WHERE posts_id = %s"
            with conn.cursor() as cursor:
                cursor.execute(query, (post[0]["body"], post[0]['post_title'], post[0]['posts_id']))
                conn.commit()
        finally:
            conn.close()


    def insert_gravatar_hash(self, email, hash):
        conn = self.connect()
        try:
            query = "UPDATE blog.users SET gravatar_hash = %s WHERE email = %s; "
            with conn.cursor() as cursor:
                cursor.execute(query, (hash, email))
                conn.commit()
        finally:
            conn.close()


    def get_user_data(self, email):
        connection = self.connect()
        try:
            query = "SELECT * FROM blog.users WHERE email = %s;"
            with connection.cursor() as cursor:
                cursor.execute(query, email)
            return cursor.fetchall()

        finally:
            connection.close()

    def get_user_by_id(self, id):
        connection = self.connect()
        try:
            query = "SELECT * FROM blog.users WHERE id = %s;"
            with connection.cursor() as cursor:
                cursor.execute(query, id)
            return cursor.fetchall()

        finally:
            connection.close()


    def get_all_users(self):
        connection = self.connect()
        try:
            query = "SELECT * FROM blog.users;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()

        finally:
            connection.close()

    def get_user_login(self, email):
        connection = self.connect()
        try:
            query = "SELECT email, username, password, confirmed, roles_id FROM blog.users WHERE email = %(email)s"
            with connection.cursor() as cursor:
                cursor.execute(query, {"email": email})
                return cursor.fetchall()

        finally:
            connection.close()

    def get_user(self, email):
        connection = self.connect()
        try:
            query = "SELECT email FROM blog.users WHERE email = %(email)s;"
            with connection.cursor() as cursor:
                cursor.execute(query, {"email": email})
            return cursor.fetchall()

        finally:
            connection.close()

    def create_user(self, roles_id, username, name, email, registration_date, password, modified_at, confirmed):
        connection = self.connect()
        try:
            query = "INSERT INTO users (roles_id, username, name, email, registration_date," \
                    " password, modified_at, confirmed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            with connection.cursor() as cursor:
                cursor.execute(query, (roles_id, username, name, email, registration_date, password, modified_at, confirmed))
                connection.commit()
        except Exception as e:
                print(e)
        finally:
            connection.close()

    def create_blog_post(self, author_id, post_title, body, post_time, modified_time, img_src):
        conn = self.connect()
        try:
            query = "INSERT INTO posts (author_id, post_title, body, post_time, modified_time, img_src) VALUES (%s, %s, %s, %s, %s, %s);"
            with conn.cursor() as cursor:
                cursor.execute(query, (author_id, post_title, body, post_time, modified_time, img_src))
                conn.commit()
        finally:
            conn.close()

    def insert_comment(self, body, comment_time, author_id, post_id, is_disabled, modified):
        conn = self.connect()
        try:
            query = "INSERT INTO comments (body, comment_time, author_id, post_id, is_disabled, modified) VALUES (%s, %s, %s, %s, %s, %s);"
            with conn.cursor() as cursor:
                cursor.execute(query, (body, comment_time, author_id, post_id, is_disabled, modified))
                conn.commit()
        finally:
            conn.close()

    def get_comments_by_author(self, post_id):
        conn = self.connect()
        try:
            query = """select users.username, users.gravatar_hash, users.confirmed, users.roles_id, users.email,
                       comments.body, comments.id, comments.comment_time, comments.modified, comments.is_disabled, comments.post_id
                       from blog.comments join users on comments.author_id = users.id
                       WHERE post_id = %s ORDER BY comment_time ASC;"""
            with conn.cursor() as cursor:
                cursor.execute(query, post_id)
                return cursor.fetchall()
        finally:
            conn.close()

    def get_comments(self):
        con = self.connect()
        try:
            query = "SELECT posts.post_title, users.username, comments.body, comments.id, comments.comment_time, " \
                    "comments.modified, comments.is_disabled, comments.post_id" \
                    " FROM blog.comments join posts on posts.posts_id = comments.post_id" \
                    " join users on posts.author_id = users.id ORDER BY comment_time ASC;"
            with con.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        finally:
            con.close()

    def insert_roles(self, roles_id, permissions):
        conn = self.connect()

        try:
                query = "UPDATE blog.roles SET permissions = %s WHERE roles_id = %s"
                with conn.cursor() as cursor:
                    cursor.execute(query, (permissions, roles_id))
                    conn.commit()
        finally:
          conn.close()

    def mod_comment(self, comment_mod, id):
        conn = self.connect()

        try:
                query = "UPDATE blog.comments SET is_disabled = %s WHERE id = %s"
                with conn.cursor() as cursor:
                    cursor.execute(query, (comment_mod, id))
                    conn.commit()
        finally:
          conn.close()

    def get_comments_by_id(self, id):
        conn = self.connect()

        try:
                query = "SELECT * FROM blog.comments WHERE id = %s"
                with conn.cursor() as cursor:
                    cursor.execute(query, id)
                    return cursor.fetchall()
        finally:
          conn.close()


    def update_comment(self, new_comment_amount, posts_id):
        conn = self.connect()

        try:
                query = "UPDATE blog.posts SET comment_count = %s WHERE posts_id = %s"
                with conn.cursor() as cursor:
                    cursor.execute(query, (new_comment_amount, posts_id))
                    conn.commit()
        finally:
          conn.close()

    def get_posts_by_user(self, id):
        conn = self.connect()
        try:
            query = "SELECT * FROM blog.posts WHERE author_id = %s ORDER BY post_time DESC;"
            with conn.cursor() as cursor:
                cursor.execute(query, id)
                return cursor.fetchall()

        finally:
            conn.close()

    def get_limited_posts(self, start_at, per_page):
        conn = self.connect()
        try:
            query = "select users.name, users.username, posts.author_id, posts.post_title, posts.body," \
                    " posts.post_time, posts.comment_count, posts.img_src, posts.posts_id from blog.posts" \
                    " join users on posts.author_id = users.id ORDER BY post_time DESC LIMIT %s, %s;"
            with conn.cursor() as cursor:
                cursor.execute(query, (start_at, per_page))
                return cursor.fetchall()
        finally:
            conn.close()

    def get_limited_users(self, start_at, per_page):
        conn = self.connect()
        try:
            query = "select * FROM blog.users ORDER BY registration_date DESC LIMIT %s, %s;"
            with conn.cursor() as cursor:
                cursor.execute(query, (start_at, per_page))
                return cursor.fetchall()
        finally:
            conn.close()

    def get_all_posts(self):
        con = self.connect()
        try:
            query = "select users.name, users.username, posts.author_id, posts.post_title," \
                    " posts.body, posts.comment_count, posts.post_time, posts.posts_id " \
                    "from blog.posts join users on posts.author_id = users.id ORDER BY post_time;"
            with con.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        finally:
            con.close()

    def get_post_id(self, id):
        conn = self.connect()
        try:
            # query = "select * from blog.posts WHERE posts_id = %s"
            query = "select users.name, users.username, users.gravatar_hash," \
                    " posts.author_id, posts.post_title, posts.comment_count, posts.body, posts.post_time, posts.posts_id, posts.img_src " \
                    "from blog.posts join users on posts.author_id = users.id WHERE posts_id = %s"
            with conn.cursor() as cursor:
                cursor.execute(query, id)
                return cursor.fetchall()
        finally:
            conn.close()

    def update_user_permissions(self, roles, email):
        conn = self.connect()

        try:
            query = "UPDATE blog.users SET roles_id = %(roles)s WHERE email = %(email)s"
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
        finally:
            conn.close()

    def update_user_profile(self, user):
        conn = self.connect()
        try:
            query = "UPDATE blog.users SET name = %s, location = %s, about_me = %s WHERE email = %s"
            with conn.cursor() as cursor:
                cursor.execute(query, (user.name, user.location, user.about_me, user.email))
                conn.commit()
        finally:
            conn.close()

    def update_confirmed_state(self, user):
        conn = self.connect()
        try:
            query = "UPDATE blog.users SET confirmed = %s WHERE email = %s"
            with conn.cursor() as cursor:
                cursor.execute(query, (user.confirmed, user.email))
                conn.commit()
        finally:
            conn.close()

    def get_modified_date_time(self, email):
        conn = self.connect()
        try:
            query = "SELECT modified_at FROM blog.users WHERE email = %s"
            with conn.cursor() as cursor:
                cursor.execute(query, (email))
                conn.commit()
                return cursor.fetchall()
        except:
            conn.close()

    def get_registration_date(self, email):
        conn = self.connect()
        try:
            query = "SELECT registration_date FROM blog.users WHERE email = %s"
            with conn.cursor() as cursor:
                cursor.execute(query, (email))
                conn.commit()
                return cursor.fetchall()
        except:
            conn.close()

    def update_modified_time(self, modified_at, email):
        conn = self.connect()
        try:
            query = "UPDATE blog.users SET modified_at = %s WHERE email = %s"
            with conn.cursor() as cursor:
                cursor.execute(query, (modified_at, email))
                conn.commit()
        finally:
            conn.close()

class DBRole:
    def update_role_permissions(self, roles_id, permissions):
        conn = DBHelper.connect(DBHelper(), database=dbconfig.db_name)

        try:
                query = "UPDATE blog.roles SET permissions = %s WHERE roles_id = %s"
                with conn.cursor() as cursor:
                    cursor.execute(query, (permissions, roles_id))
                    conn.commit()
        finally:
          conn.close()


    def get_roles(self, name):
        conn = DBHelper.connect(DBHelper(), database=dbconfig.db_name)
        try:
            query = "SELECT * FROM blog.roles WHERE name = s(name)%"
            with conn.cursor() as cursor:
                cursor.execute(query, {'name': name})
                return cursor.fetchall()
        finally:
            conn.close()
