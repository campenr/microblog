from flask import redirect, render_template, abort, request, url_for
from flask_login import login_user, logout_user, current_user
from flask_login import login_required

from microblog import app
from microblog.forms import LoginForm, EditProjectForm, EditPostForm
from microblog.models import User, Page, Post



@app.login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(id=user_id).limit(1).first()
    return user


"""

Routes for web interface
========================

    - index: main page with login link
    - login/logout: routes for logging in and out
    - page/<page_name>: each topic gets a single page, where names's are random strings (see below)
    - page/<page_name>/<post_id>: each page gets unlimited? posts

    In this structure, the page own's the posts associated with it. A page may have only a single post
    in which case it appears like a normal single blogpost. A page may have multiple posts however which
    is useful in the case of a page being about a project, and posts documenting ongoing progress over
    time for that project.

"""

########
#
#  Login/out Routes
#
#######

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route for displaying login page."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).limit(1).first()
        if user is not None:
            if user.verify_password(form.password.data):
                login_user(user)
                # Ignore next property, always redirect to index on login.
                return redirect(url_for('index'))
        # TODO handle incorrect password better

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Route for logging out user."""
    logout_user()
    return redirect(url_for('index'))

########
#
#  Routes for viewing
#
#######

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@login_required
def index():
    """Route for displaying index page.

    Displays page summaries sorted by date created in descending order.
    """

    # None if no pages exist
    pages_data = Page.retrieve_pages()

    return render_template('index.html', pages_data=pages_data)


@app.route('/view/<page_name>', methods=['GET'])
@login_required
def view_page(page_name):
    """Default route for viewing the most recent post for a given page."""

    # None if no page with page_name exists
    page_data = Page.retrieve_page(name=page_name)
    if page_data is not None:

        # check that there are posts and redirect to the latest post; otherwise render without posts
        if page_data['posts']:
            return redirect(url_for('view_post', page_name=page_name, post_id=page_data['posts'][-1]))
        else:
            return render_template('viewer.html', page_data=page_data, post_data=None)

    # if page_data is None then the page doesn't exist so we abort
    abort(404)


@app.route('/view/<page_name>/<int:post_id>', methods=['GET'])
@login_required
def view_post(page_name, post_id):
    """Route for viewing a specific post belonging to a page."""

    page_data = Page.retrieve_page(name=page_name)
    if page_data is not None:

        # Get post data for given page and render
        post_data = Post.retrieve_post(page_name=page_data['name'], post_id=post_id)
        if post_data is not None:
            return render_template('viewer.html', page_data=page_data, post_data=post_data)

    # Abort if page_data or post_data are None; occurs when the page_name does not exist, or when the
    # post_id does not exist for that page_name.
    abort(404)

########
#
#  Routes for creating
#
#######

@app.route('/editor/new', methods=['GET', 'POST'])
@login_required
def new_page():
    """Route for creating a new project."""

    form = EditProjectForm()

    # POST endpoint
    if form.validate_on_submit():

        try:
            page_data = Page.add_page(title=form.title.data, body=form.body.data, private=form.private.data)
            return redirect(url_for('view_page', page_name=page_data['name']))
        except Exception as e:
            print('[ERROR]: ', e)
            # TODO handle this error better
            return redirect(url_for('index'))

    # GET endpoint
    # Render without any page content to auto fill editor with as we're creating a new page
    return render_template('editor.html', form=form, title=None, data=None)


@app.route('/editor/<page_name>/new', methods=['GET', 'POST'])
@login_required
def new_post(page_name):
    """Route for creating a new post."""

    # None if no page with page_name exists
    page_data = Page.retrieve_page(name=page_name)

    if page_data is not None:

        form = EditPostForm()

        # POST endpoint
        if form.validate_on_submit():

            try:
                post_data = Post.add_post(page_name=page_name, body=form.body.data, private=form.private.data)
                return redirect(url_for('view_post', page_name=page_name, post_id=post_data['post_id']))
            except Exception as e:
                print('[ERROR]: ', e)
                # TODO handle this error better
                return redirect(url_for('index'))

        # GET endpoint
        # Render without any page content to auto fill editor with as we're creating a new page
        return render_template('editor.html', form=form, title=page_data['title'], data=None)

    # if page_data is None then the page doesn't exist in the database so we abort
    abort(404)

########
#
#  Routes for editing
#
#######

@app.route('/editor/<page_name>', methods=['GET', 'POST'])
@login_required
def edit_page(page_name):
    """Route for editing an existing page."""

    # None if no page with page_name exists
    page_data = Page.retrieve_page(name=page_name)

    if page_data is not None:

        form = EditProjectForm(title=page_data['title'], body=page_data['body'], private=page_data['private'])

        # POST endpoint
        if form.validate_on_submit():
            try:
                page_data = Page.edit_page(name=page_name, title=form.title.data, body=form.body.data, private=form.private.data)
                return redirect(url_for('view_page', page_name=page_data['name']))
            except Exception as e:
                print('[ERROR]: ', e)
                # TODO handle this error better
                return redirect(url_for('index'))

        # GET endpoint
        return render_template('editor.html', form=form, title=page_data['title'], data=page_data)

    # if page_data is None then the page doesn't exist in the database so we abort
    abort(404)


@app.route('/editor/<page_name>/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(page_name, post_id):
    """Route for editing an existing post."""

    # None if no page with page_name exists
    page_data = Page.retrieve_page(name=page_name)

    if page_data is not None:

        # If post id is 0 redirect to editing page description; NOTE: valid posts are 1 indexed
        if post_id == 0:
            return redirect(url_for('edit_page', page_name=page_name))

        # Get post data for given page and pre-fill form with existing post data and render
        post_data = Post.retrieve_post(page_name=page_data['name'], post_id=post_id)
        if post_data is not None:
            form = EditPostForm(body=post_data['body'], private=post_data['private'])

            # POST endpoint
            if form.validate_on_submit():

                try:
                    post_data = Post.edit_post(page_name=page_name, post_id=post_id, body=form.body.data, private=form.private.data)
                    return redirect(url_for('view_post', page_name=page_data['name'], post_id=post_data['post_id']))
                except Exception as e:
                    print('[ERROR]: ', e)
                    # TODO handle this error better
                    return redirect(url_for('index'))

            # GET endpoint
            return render_template('editor.html', form=form, title=page_data['title'], data=post_data)

    # Abort if page_data or post_data are None; occurs when the page_name does not exist, or when the
    # post_id does not exist for that page_name.
    abort(404)

########
#
#  Routes for deleting
#
#######

@app.route('/delete/page', methods=['POST'])
@login_required
def delete_page():
    """Delete page from the database.

    NOTE: will delete all associated posts as well.
    """

    try:
        page_name = request.form['page_name']
    except Exception as e:
        print(e)
        return redirect(url_for('index'))

    # None if no page with page_name exists
    page_data = Page.delete_page(name=page_name)

    return redirect(url_for('index'))


@app.route('/delete/post', methods=['POST'])
@login_required
def delete_post():
    """Delete post from the database."""

    try:
        page_name = request.form['page_name']
        post_id = request.form['post_id']
    except Exception as e:
        print(e)
        return redirect(url_for('index'))

    # None if no page with page_name exists
    page_data, post_data = Post.delete_post(page_name=page_name, post_id=post_id)

    return redirect(url_for('index'))