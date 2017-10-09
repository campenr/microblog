from flask import abort, jsonify, request, url_for
from flask_login import current_user
from sqlalchemy import desc

from projects import app
from projects.models import Project


# @app.login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# TODO: implement token based API authorization

"""

API Routes
========================

    API only has read access to data (no ability to add or modify projects/posts).
    
    Endpoints:
      - /api/projects  :  return all pages(TODO add pagination here)
      - /api/project/<project_name>  :  return specific project
      
    A successful request will result in a JSON response object containing the requested data in `data`. Any attempt to 
    access a project or post that does not exist, or is private, will return a 404 instead of a JSON response, and a bad
    request will return a 400.

"""

PROJECT_KEY_FILTER = ['name', 'title', 'body', 'created', 'edited']
POST_KEY_FILTER = ['post_id', 'body', 'created', 'edited']

# ---------------- API routes ---------------- #


@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Returns all projects."""

    # None if no pages exist
    projects = Project.query.filter_by(user_id=current_user.id).order_by(desc(Project.created)).all()

    # init response data container
    formatted_projects_data = []

    if projects is None:
        # if project is None then the project doesn't exist so we abort
        abort(404)

    # go through projects, filtering to only the fields we want returned, and only if page is not private.
    for project in projects:
        if not project.private:

            # filter project data sent in response
            formatted_project_data = format_project_data(project)
            formatted_projects_data.append(formatted_project_data)

    return jsonify({'data': formatted_projects_data})


@app.route('/api/project', methods=['GET'])
def get_project():
    """Returns a single project."""

    # get project and post identifiers from the request
    project_name = request.args.get('name')

    if project_name is None:
        # no project_name specified so we abort with bad request response
        abort(400)

    # None if no page with page_name exists
    project = Project.query.filter_by(user_id=current_user.id, name=project_name).first()
    if project is not None:
        if project.private:
            # treat private projects as not existing
            project = None

    # return not found error if project does not exist or is private
    if project is None:
        abort(404)

    # get list of non-private posts for the project
    posts = [post for post in project.posts if not post.private]

    formatted_project_data = format_project_data(project)
    if len(posts) >= 1:
        # get most recent post by default
        formatted_project_data['post'] = format_post_data(posts[-1])
    else:
        formatted_project_data['post'] = None

    return jsonify({'data': formatted_project_data})


@app.route('/api/post', methods=['GET'])
def get_post():
    """Returns a specified post."""

    # get project and post identifiers from the request
    project_name = request.args.get('name')
    post_id = request.args.get('id')

    if project_name is None or post_id is None:
        # no project_name or post_id specified so we abort with bad request response
        abort(400)

    # None if no page with page_name exists
    project = Project.query.filter_by(user_id=current_user.id, name=project_name).first()
    if project is not None:
        if project.private:
            # treat private projects as not existing
            project = None

    # return not found error if project does not exist or is private
    if project is None:
        abort(404)

    post = project.posts.filter_by(id=post_id).first()
    if post is not None:
        if post.private:
            # treat private posts as not existing
            post = None

    # return not found error if post does not exist or is private
    if post is None:
        abort(404)

    formatted_page_data = format_project_data(project)
    formatted_page_data['post'] = format_post_data(post)

    return jsonify({'data': formatted_page_data})


# ---------------- helper functions ---------------- #


def format_project_data(project_data):
    """Filter our fields from project_data that aren't in PROJECT_KEY_FILTER."""

    formatted_data = {key: value for key, value in vars(project_data).items() if key in PROJECT_KEY_FILTER}
    formatted_data['uri'] = url_for('get_project', name=project_data.name)

    return formatted_data


def format_post_data(post_data):
    """Filter out fields from post_data that aren't in POST_KEY_FILTER."""

    return {key: value for key, value in vars(post_data).items() if key in POST_KEY_FILTER}
