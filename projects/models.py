import random
import datetime

from projects import db, app
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

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, nullable=False)
    title = db.Column(db.String)
    body = db.Column(db.String)
    created = db.Column(db.DateTime, nullable=False)
    edited = db.Column(db.DateTime)
    private = db.Column(db.Boolean)
    posts = db.relationship('Post', backref='project', lazy='dynamic', cascade="all, delete, delete-orphan")

    # @classmethod
    # def retrieve_page(cls, name):
    #     """Return a page object as a dictionary for a valid page id, else None."""
    #
    #     # Result is none if page id does not exist
    #     result = cls.query.filter_by(name=name).first()
    #
    #     if result is not None:
    #         formatted_result = vars(result)
    #         # append list of post_id's to formatted result which are not included by default
    #         # if no posts exist list will be empty.
    #         formatted_result['posts'] = [post.post_id for post in result.posts]
    #         return formatted_result
    #     else:
    #         return None

    # @classmethod
    # def retrieve_pages(cls):
    #     """Return a list of page objects as dictionaries, else None."""
    #
    #     # TODO implement pagination
    #     result = cls.query.order_by(desc(Project.created)).all()
    #
    #     # An empty list is returned from the above queries if no matching results exist.
    #     if result:
    #         formatted_results = [vars(rec) for rec in result]
    #         return formatted_results
    #     else:
    #         return None

    # @classmethod
    # def add_page(cls, title, body, private):
    #     """Add a new page to the database and return the link object, else None."""
    #
    #     page = cls()
    #
    #     page.name = Project.generate_page_name()
    #     page.title = title
    #     page.body = body
    #     page.private = private
    #     page.created = datetime.datetime.now()
    #     page.edited = datetime.datetime.now()
    #
    #     db.session.add(page)
    #     db.session.commit()
    #
    #     page_data = Project.retrieve_page(name=page.name)
    #
    #     return page_data

    # @classmethod
    # def edit_page(cls, name, title, body, private):
    #
    #     # Get page object from page_name
    #     page = cls.query.filter_by(name=name).first()
    #
    #     page.title = title
    #     page.body = body
    #     page.private = private
    #     page.edited = datetime.datetime.now()
    #
    #     db.session.commit()
    #
    #     # Retrieve new page to return
    #     page_data = Project.retrieve_page(name=name)
    #
    #     return page_data

    # @classmethod
    # def delete_page(cls, name):
    #     """Delete a page from the database and return the deleted page, else None."""
    #
    #     # First fetch the page so we can return this to the view, then delete the record.
    #     page_data = Project.retrieve_page(name=name)
    #     cls.query.filter_by(name=name).delete()
    #     db.session.commit()
    #
    #     # will return none if the requested page never existed
    #     return page_data

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
    content
        Main content of post

    """

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    title = db.Column(db.String)
    body = db.Column(db.Text)
    created = db.Column(db.DateTime)
    edited = db.Column(db.DateTime)
    private = db.Column(db.Boolean)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    @classmethod
    def retrieve_post(cls, page_name, post_id):
        """Return a post object as a dictionary for a valid post id, else None."""

        # Result is none if page id does not exist
        page = Project.query.filter_by(name=page_name).first()

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
        page = Project.query.filter_by(name=page_name).first()

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
        page = Project.query.filter_by(name=page_name).first()

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
        page_data = Project.retrieve_page(name=page_name)
        if page_data is not None:

            # First fetch the post so we can return this to the view, then delete the record.
            post_data = Post.retrieve_post(page_name=page_name, post_id=post_id)
            cls.query.filter_by(id=post_data['id']).delete()
            db.session.commit()

        # will return None, None if the requested page and post never existed repectivley
        return page_data, post_data

    def __repr__(self):
        return '<Post %r>' % self.id