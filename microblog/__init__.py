from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from microblog import views, models, forms
from microblog.api import api_v1

app.jinja_env.filters['markdown_filter'] = models.format_markdown
