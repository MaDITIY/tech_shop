import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mega-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/tech_shop?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
    POSTS_PER_PAGE = 10
    UPLOAD_FOLDER = 'uploads'