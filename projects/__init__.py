from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from projects import views, models, forms, helpers
from projects.api import api_v1

app.jinja_env.filters['markdown_filter'] = helpers.format_markdown
