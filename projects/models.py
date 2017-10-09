import random

from projects import db
from sqlalchemy_utils import PasswordType, force_auto_coercion


force_auto_coercion()


class User(db.Model):
    """User table object representation.

    The user only exists to restrict editing of blog content to an authenticated user. It is not intended for
    the platform to support multiple users... for now.

    Columns
    -------
    id
        Unique auto incrementing identifier.
    username
        Unique username used to login.
    password_hash
        Hash of users password.
    api_token
        API token used for restricted API access

    """

    #TODO: add api key column, and methods for generating/regenerating the api key.

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    api_token = db.Column(PasswordType(schemes=['pbkdf2_sha512']))

    projects = db.relationship('Project', backref='user', lazy='dynamic', cascade="all, delete, delete-orphan")

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def change_password(self, username):
        # TODO implement
        pass

    def __repr__(self):
        return '<User %r>' % self.username


class Project(db.Model):
    """Page table object representation.

    The page object is the main object with which various posts will be associated.
    Each page has some content associated with it which is an overview of the page topic
    and important initial links.
    The Post object stores individual posts that are associated with a given page.

    Columns
    -------
    id
        Unique auto incrementing identifier.
    name
        Page name (unique)
    title
        Title of the project
    description
        Brief descriptive overview of the project, saved for editing
    description_htl
        The description but rendered as html, for display
    created
        When the Project was first created
    edited
        When the Project was last edited
    private
        Whether the Project is private, and therefore visible to the API
    posts
        Posts linked to this Project

    """

    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, nullable=False)
    title = db.Column(db.String)
    body = db.Column(db.String)
    created = db.Column(db.DateTime, nullable=False)
    edited = db.Column(db.DateTime)
    private = db.Column(db.Boolean, nullable=False, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    posts = db.relationship('Post', backref='project', lazy='dynamic', cascade="all, delete, delete-orphan")

    @staticmethod
    def generate_page_name():

        word_dict = {
            'adjectives': ['Melodic', 'Fluffy', 'Climbing', 'Whispering', 'Thundering', 'Crooked', 'Shallow', 'Obnoxious', 'Bewildered', 'Jolly', 'Agreeable', 'Gifted', 'Handsome', 'Drab', 'Magnificent', 'Boiling', 'Bumpy', 'Cuddly', 'Abundant', 'Sparse'],
            'colors': ['Amber', 'Auburn', 'Azure', 'Beige', 'Brass', 'Carmine', 'Cerulean', 'Champagne', 'Cinnabar', 'Crimson', 'Cyan', 'Ebony', 'Fuchsia', 'Ginger', 'Indigo', 'Lavender', 'Lemon', 'Mahogany', 'Mauve', 'Ochre', 'Olive', 'Scarlet', 'Tan', 'Maroon', 'Vermillion', 'Tangerine', 'Viridian', 'Violet'],
            'animals': ['Aardvark', 'Alligator', 'Alpaca', 'Armadillo', 'Buffalo', 'Caribou', 'Cheetah', 'Chinchilla', 'Dugong', 'Eagle', 'Echidna', 'Emu', 'Flamingo', 'Gazelle', 'Giraffe', 'Goose', 'Grouse', 'Hippo', 'Ibex', 'Jackal', 'Jaguar', 'Kangaroo', 'Llama', 'Lion', 'Mallard', 'Mongoose', 'Marwhal', 'Owl', 'Panther', 'Parrot', 'Penguin', 'Raven', 'Rhino', 'Seal', 'Squirrel', 'Swan', 'Tapir', 'Tiger', 'Turkey', 'Wallaby', 'Walrus', 'Wombat', 'Yak', 'Zebra']
        }

        while True:
            name = ''.join([random.SystemRandom().choice(word_dict['adjectives'] + word_dict['colors']),
                            random.SystemRandom().choice(word_dict['animals'])])
            if Project.query.filter_by(name=name).first() is None:
                return name

    def __repr__(self):
        return '<Project %r>' % self.id


class Post(db.Model):
    """Post table object representation.

    The page object is the main object with which various posts will be associated.
    Each page has some content associated with it which is an overview of the page
    and important initial links.
    The Post object stores individual posts that are associated with a given page.

    Columns
    -------
    id
        Unique auto incrementing identifier.
    post_id
        Unique auto incrementing identifier for the posts for a specific project
    content
        Main content of post

    """

    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String)
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, nullable=False)
    edited = db.Column(db.DateTime)
    private = db.Column(db.Boolean, nullable=False, default=True)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    def __repr__(self):
        return '<Project %r>.<Post %r>' % (self.project_id, self.id)
