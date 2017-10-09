from flask import redirect, render_template, abort, request, url_for, flash
from flask_login import login_user, logout_user, current_user
from flask_login import login_required

import datetime

from sqlalchemy import desc

from projects import app, db
from projects.forms import LoginForm, EditProjectForm, EditPostForm
from projects.models import User, Project, Post


@app.login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


"""

Routes for web interface
========================

    - index: main page with all projects listed
    - login/logout: routes for logging in and out
    - project/<project_name>: each project gets a single page, where names's are random strings (see below)
    - project/<project_name>/post/<post_id>: each project gets unlimited posts

    In this structure, the project own's the posts associated with it. A project may have only a single post
    in which case it appears like a normal single blog post. A project may have multiple posts however which
    is may be useful in some circumstances, .

"""

########
#
#  Login/out Routes
#
#######


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route for logging in."""

    if not current_user.is_anonymous:
        # user is already logged in so we redirect to index
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        # login attempted, try to get user data, confirm password, then login
        user = User.query.filter_by(username=form.username.data).limit(1).first()
        if user is not None:
            if user.password == form.password.data:
                login_user(user)
                # redirect to next if specified, else index
                return redirect(request.args.get('next') or url_for('index'))

            else:
                # password does not match
                flash('Invalid password', 'danger')
                return redirect(url_for('login'))
        else:
            # username does not exist
            flash('Invalid username', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Route for logging out."""
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
    """Displays page summaries sorted by date created in descending order."""

    projects = Project.query.filter_by(user_id=current_user.id).order_by(desc(Project.created)).all()
    return render_template('index.html', projects=projects)


@app.route('/project/<project_name>', methods=['GET'])
@login_required
def view_project(project_name):
    """Default route for viewing a project and its most recent post if it exists."""

    # None if no page with page_name exists
    project = Project.query.filter_by(user_id=current_user.id, name=project_name).first()
    posts = [post for post in project.posts]

    if len(posts) > 1:
        # get most recent post by default
        post = posts[-1]
    else:
        post = None

    if project is None:
        # if project is None then the page doesn't exist so we abort
        abort(404)
    return render_template('viewer.html', project=project, posts=posts, post=post)


@app.route('/project/<project_name>/post/<int:post_id>', methods=['GET'])
@login_required
def view_post(project_name, post_id):
    """Route for viewing a specific post belonging to a page."""

    # None if no page with page_name exists
    project = Project.query.filter_by(user_id=current_user.id, name=project_name).first()
    post = project.posts.filter_by(post_id=post_id).first()

    if project is None or post is None:
        # Abort if page_data or post_data are None; occurs when the page_name does not exist, or when the
        # post_id does not exist for that page_name.
        abort(404)

    return render_template('viewer.html', project=project, post=post)

########
#
#  Routes for creating
#
#######


@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """Route for creating a new project."""

    form = EditProjectForm()

    if form.validate_on_submit() and request.method == 'POST':

        try:
            project = Project(
                name=Project.generate_page_name(),
                title=form.title.data,
                body=form.body.data,
                created=datetime.datetime.now(),
                private=form.private.data,
                user=current_user
            )
            db.session.add(project)
            db.session.commit()

            return redirect(url_for('view_project', project_name=project.name))

        except Exception as e:
            print('[ERROR]: ', e)
            # TODO handle this error better
            return redirect(url_for('index'))

    # Render without any page content to auto fill editor with as we're creating a new project
    return render_template('editor.html', form=form, type_='project', new=True, data=None)


@app.route('/project/<project_name>/post/new', methods=['GET', 'POST'])
@login_required
def new_post(project_name):
    """Route for creating a new post."""

    # None if no page with page_name exists
    project = Project.query.filter_by(user_id=current_user.id, name=project_name).first()

    if project is None:
        # if page_data is None then the page doesn't exist in the database so we abort
        abort(404)

    form = EditPostForm()

    if form.validate_on_submit() and request.method == 'POST':
        try:

            num_posts = len([post for post in project.posts])

            post = Post(
                post_id=num_posts + 1,  # need a better way of doing this as it is prone to break
                title=project.title,  # posts get their title from the project
                body=form.body.data,
                created=datetime.datetime.now(),
                private=form.private.data,
                project=project
            )
            db.session.add(post)
            db.session.commit()

            return redirect(url_for('view_post', project_name=post.project.name, post_id=post.id))

        except Exception as e:
            print('[ERROR]: ', e)
            # TODO handle this error better
            return redirect(url_for('index'))

    # Render without any page content to auto fill editor with as we're creating a new post
    return render_template('editor.html', form=form, type_='post', new=True, data=project)


########
#
#  Routes for editing
#
#######


@app.route('/project/<project_name>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_name):
    """Route for editing an existing project."""

    # None if no page with page_name exists
    project = Project.query.filter_by(user_id=current_user.id, name=project_name).first()

    if project is None:
        # if project is None then the project doesn't exist in the database so we abort
        abort(404)

    # populate editor with existing data
    form = EditProjectForm(title=project.title, body=project.body, private=project.private)

    if form.validate_on_submit() and request.method == 'POST':
        try:
            project.title = form.title.data
            project.body = form.body.data
            project.edited = datetime.datetime.now()
            project.private = form.private.data

            db.session.commit()

            return redirect(url_for('view_project', project_name=project.name))

        except Exception as e:
            print('[ERROR]: ', e)
            # TODO handle this error better
            return redirect(url_for('index'))

    return render_template('editor.html', form=form, type_='project', new=False, data=project)


@app.route('/project/<project_name>/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(project_name, post_id):
    """Route for editing an existing post."""

    # None if no page with page_name exists
    project = Project.query.filter_by(user_id=current_user.id, name=project_name).first()
    post = project.posts.filter_by(post_id=post_id).first()

    if project is None or post is None:
        # Abort if project or post_data are None; occurs when the page_name does not exist, or when the
        # post_id does not exist for that page_name.
        abort(404)

    # Get post data for given page and pre-fill form with existing post data and render
    form = EditPostForm(body=post.body, private=post.private)

    if form.validate_on_submit() and request.method == 'POST':
        try:
            post.body = form.body.data
            post.edited = datetime.datetime.now()
            post.private = form.private.data

            db.session.commit()

            return redirect(url_for('view_post', project_name=project.name, post_id=post.id))

        except Exception as e:
            print('[ERROR]: ', e)
            # TODO handle this error better
            return redirect(url_for('index'))

    return render_template('editor.html', form=form, type_='post', new=False, data=post)

########
#
#  Routes for deleting
#
#######

@app.route('/project/<project_name>/delete', methods=['GET'])
@login_required
def delete_page(project_name):
    """Delete page from the database.

    NOTE: will delete all associated posts as well.

    """

    # None if no page with page_name exists
    project = Project.query.filter_by(user_id=current_user.id, name=project_name).first()

    if project is None:
        # Abort if project or are None; occurs when the page_name does not exist, or when the
        # post_id does not exist for that page_name.
        abort(404)

    # delete posts for the project first
    for post in project.posts:
        Post.query.filter_by(id=post.id).delete()

    Project.query.filter_by(user_id=current_user.id, name=project_name).delete()

    db.session.commit()

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
