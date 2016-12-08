from flask import jsonify
import random
import datetime

from microblog import db, app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from flask import url_for

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc

from flask import Markup
from CommonMark import commonmark


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

    """

    #TODO: add api key column, and methods for generating/regenerating the api key.

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    password_hash = db.Column(db.String(120))

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

    # TODO fix expiration.
    # TODO change to using an actual token, not just user id number.
    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @classmethod
    def add_user(cls, username, password, api=False):
        """Add a new user to the User table and return the id of the user, else None."""

        user = User()

        user.username = username
        user.password_hash = cls.hash_password(password)

        db.session.add(user)
        db.session.commit()

        return user.get_id()

    @classmethod
    def delete_user(cls, username):
        # TODO implement
        pass

    @classmethod
    def change_password(cls, username):
        # TODO implement
        pass

    @staticmethod
    def hash_password(password):
        """Return hash of submitted password."""
        return pwd_context.encrypt(password)

    def verify_password(self, password):
        """Return whether submitted password matches stored hash."""
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return '<User %r>' % self.username


class Page(db.Model):
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
    content
        Main content of page

    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    title = db.Column(db.String)#, nullable=False)
    body = db.Column(db.String)#, nullable=False)
    created = db.Column(db.DateTime)
    edited = db.Column(db.DateTime)
    private = db.Column(db.Boolean)
    posts = db.relationship('Post', backref='page', lazy='dynamic', cascade="all, delete, delete-orphan")

    @classmethod
    def retrieve_page(cls, name):
        """Return a page object as a dictionary for a valid page id, else None."""

        # Result is none if page id does not exist
        result = cls.query.filter_by(name=name).first()

        if result is not None:
            formatted_result = vars(result)
            # append list of post_id's to formatted result which are not included by default
            # if no posts exist list will be empty.
            formatted_result['posts'] = [post.post_id for post in result.posts]
            return formatted_result
        else:
            return None

    @classmethod
    def retrieve_pages(cls):
        """Return a list of page objects as dictionaries, else None."""

        # TODO implement pagination
        result = cls.query.order_by(desc(Page.created)).all()

        # An empty list is returned from the above queries if no matching results exist.
        if result:
            formatted_results = [vars(rec) for rec in result]
            return formatted_results
        else:
            return None

    @classmethod
    def add_page(cls, title, body, private):
        """Add a new page to the database and return the link object, else None."""

        page = cls()

        page.name = Page.generate_page_name()
        page.title = title
        page.body = body
        page.private = private
        page.created = datetime.datetime.now()
        page.edited = datetime.datetime.now()

        db.session.add(page)
        db.session.commit()

        page_data = Page.retrieve_page(name=page.name)

        return page_data

    @classmethod
    def edit_page(cls, name, title, body, private):

        # Get page object from page_name
        page = cls.query.filter_by(name=name).first()

        page.title = title
        page.body = body
        page.private = private
        page.edited = datetime.datetime.now()

        db.session.commit()

        # Retrieve new page to return
        page_data = Page.retrieve_page(name=name)

        return page_data

    @classmethod
    def delete_page(cls, name):
        """Delete a page from the database and return the deleted page, else None."""

        # First fetch the page so we can return this to the view, then delete the record.
        page_data = Page.retrieve_page(name=name)
        cls.query.filter_by(name=name).delete()
        db.session.commit()

        # will return none if the requested page never existed
        return page_data

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
            if Page.query.filter_by(name=name).first() is None:
                return name

    def __repr__(self):
        return '<Page %r>' % self.id


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
    name
        Page name (unique)
    content
        Main content of page

    """

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    body = db.Column(db.Text)
    created = db.Column(db.DateTime)
    edited = db.Column(db.DateTime)
    private = db.Column(db.Boolean)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

    @classmethod
    def retrieve_post(cls, page_name, post_id):
        """Return a post object as a dictionary for a valid post id, else None."""

        # Result is none if page id does not exist
        page = Page.query.filter_by(name=page_name).first()

        if page is not None:
            # Result is empty list if no posts exist
            posts = Post.query.filter_by(page_id=page.id)
            posts_list = [post.post_id for post in page.posts]

            if post_id in posts_list:
                result = posts.filter_by(post_id=post_id).first()
                formatted_result = vars(result)
                return formatted_result

        else:
            # returns None if specified page or post does not exist
            return None

    # NOT SURE WE NEED THIS METHOD AS IT'S NEVER CALLED
    #
    # @classmethod
    # def retrieve_posts(cls):
    #     """Return a list of post objects as dictionaries, else None."""
    #
    #     # TODO implement pagination
    #     result = cls.query.order_by(desc(Post.created)).all()
    #
    #     # An empty list is returned from the above queries if no matching results exist.
    #     if result:
    #         formatted_results = [vars(rec) for rec in result]
    #         return formatted_results
    #     else:
    #         return None

    @classmethod
    def add_post(cls, page_name, body, private):
        """Add a new post to the database and return the link object, else None."""

        # Get Page object from page_name
        page = Page.query.filter_by(name=page_name).first()

        # Create new post
        post = cls()

        # Set new post's id as one higher than previous. NOTE: post_id is 1 indexed
        post.post_id = len(page.posts.all()) + 1

        post.body = body
        post.private = private
        post.created = datetime.datetime.now()
        post.edited = datetime.datetime.now()

        # add post to page object
        post.page = page

        db.session.add(post)
        db.session.commit()

        post_data = Post.retrieve_post(page_name=page.name, post_id=post.post_id)

        return post_data

    @classmethod
    def edit_post(cls, page_name, post_id, body, private):

        # Get page object
        page = Page.query.filter_by(name=page_name).first()

        # Get post object from page object and post_id, and update
        post = cls.query.filter_by(page_id=page.id, post_id=post_id).first()

        post.body = body
        post.private = private
        post.edited = datetime.datetime.now()

        db.session.commit()

        # Retrieve new page to return
        post_data = Post.retrieve_post(page_name=page_name, post_id=post_id)

        return post_data

    @classmethod
    def delete_post(cls, page_name, post_id):
        """Delete a post from the database and return the deleted post, else None."""

        # initialise post_data
        post_data = None

        # First fetch the page and post so we can return this to the view, then delete the record.
        page_data = Page.retrieve_page(name=page_name)
        if page_data is not None:

            # First fetch the post so we can return this to the view, then delete the record.
            post_data = Post.retrieve_post(page_name=page_name, post_id=post_id)
            cls.query.filter_by(id=post_data['id']).delete()
            db.session.commit()

        # will return None, None if the requested page and post never existed repectivley
        return page_data, post_data

    def __repr__(self):
        return '<Post %r>' % self.id


def format_markdown(text):

    return Markup(commonmark(text))