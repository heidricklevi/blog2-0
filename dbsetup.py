import pymysql
import dbconfig

connection = pymysql.connect(host='localhost', port=3306, user=dbconfig.db_user, passwd=dbconfig.db_password)

try:
    with connection.cursor() as cursor:
        sql = "CREATE DATABASE IF NOT EXISTS blog"
        cursor.execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS blog.users (

              id int NOT NULL AUTO_INCREMENT,
              roles_id int,
              name VARCHAR(1000),
              email VARCHAR(255),
              registration_date DATETIME,
              password VARCHAR(255),
              modified_at TIMESTAMP,
              confirmed BOOLEAN,
              FOREIGN KEY (roles_id) REFERENCES blog.roles(roles_id),
              PRIMARY KEY (id))"""

        cursor.execute(sql)

        sql = """CREATE TABLE IF NOT EXISTS blog.roles (

              roles_id int NOT NULL AUTO_INCREMENT,
              name VARCHAR(64) UNIQUE,
              default_permission BOOLEAN,
              permissions int,
              PRIMARY KEY (roles_id)
              )"""
        cursor.execute(sql)

        sql = """CREATE TABLE IF NOT EXISTS blog.posts (

              posts_id int NOT NULL AUTO_INCREMENT,
              author_id int,
              body VARCHAR(21830),
              post_time TIMESTAMP,
              FOREIGN KEY (author_id) REFERENCES blog.users(id),
              PRIMARY KEY (posts_id)
              )"""

        cursor.execute(sql)

        sql = """CREATE TABLE if NOT EXISTS blog.comments (

              id int NOT NULL AUTO_INCREMENT,
              body TEXT NOT NULL,
              comment_time TIMESTAMP,
              author_id int,
              post_id int,
              FOREIGN KEY (author_id) REFERENCES blog.users(id),
              FOREIGN KEY (post_id) REFERENCES blog.posts(posts_id),
              PRIMARY KEY (id)

              )"""

        cursor.execute(sql)

    connection.commit()
finally:
    connection.close()
