from flask import redirect, render_template, abort, request, url_for, jsonify
from flask_login import login_user, logout_user, current_user
from flask_login import login_required

from projects import app
from projects.forms import LoginForm, EditProjectForm
from projects.models import User, Project, Post



@app.login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(id=user_id).limit(1).first()
    return user

"""

Routes for v1 RESTful api
========================

    API only has read access to data (no ability to add or modify page/posts).

    Endpoints:
      - /api_v1/pages  :  return all pages(TODO add pagination here)
      - /api_v1/pages/<page_name>/<int:page_id>  :  return page with specific post

    NOTE: posts are 1 indexed, with post 0 an alias for the most recent post.

"""

PAGE_KEY_FILTER = ['name', 'title', 'body', 'created', 'edited']
POST_KEY_FILTER = ['body', 'created', 'edited']

#######
#
#  API Routes
#
#######

@app.route('/api_v1/pages', methods=['GET'])
def get_pages():
    """Route for getting most recent pages."""

    # None if no pages exist
    pages_data = Project.retrieve_pages()

    # init formatted_pages_data here so that an empty list is returned both if there are no pages,
    # or if there are no non-private pages
    formatted_pages_data = []

    if pages_data is not None:

        # go through pages_data, filtering to only the fields we want returned, and only if page is not private.
        for page_data in pages_data:
            if not page_data['private']:

                # filter page data
                formatted_page_data = format_page_data(page_data)
                formatted_pages_data.append(formatted_page_data)

    return jsonify({'data': formatted_pages_data})


@app.route('/api_v1/pages/<page_name>', methods=['GET'])
def get_page(page_name):
    """Default route for getting the most recent post for a given page."""

    # None if no page with page_name exists
    page_data = Project.retrieve_page(name=page_name)
    if page_data is not None:

        # init latest_pubic_post here so that if no pubic posts exist, formatted_page_data['post'] is returned as None.
        latest_public_post = None

        if page_data['posts']:

            # find the most recent non-private post
            for post_id in page_data['posts'][::-1]:
                post_data = Post.retrieve_post(page_name=page_name, post_id=post_id)
                if not post_data['private']:
                    latest_public_post = post_data
                    break

        formatted_page_data = format_page_data(page_data)

        if latest_public_post is not None:
            formatted_page_data['post'] = format_post_data(latest_public_post)
        else:
            formatted_page_data['post'] = None

        return jsonify({'data': formatted_page_data})

    # if page_data is None then the page doesn't exist so we abort
    abort(404)


@app.route('/api_v1/pages/<page_name>/<int:post_id>', methods=['GET'])
def get_post(page_name, post_id):
    """Route for getting a specific page, along with the most recent post."""

    # None if no page with page_name exists
    page_data = Project.retrieve_page(name=page_name)

    if page_data is not None:
        if not page_data['private']:

            # Get requested post data
            post_data = Post.retrieve_post(page_name=page_data['name'], post_id=post_id)

            if post_data is not None:
                if not post_data['private']:
                    formatted_page_data = format_page_data(page_data)
                    formatted_page_data['post'] = format_post_data(post_data)

                    return jsonify({'data': formatted_page_data})

    # abort with response code 404 if either the specified page or post do not exist,
    # or if either the specified page or post are private.
    abort(404)

#######
#
#  Helper functions
#
#######

def format_page_data(page_data):
    """Filter our fields from page_data that aren't in PAGE_KEY_FILTER."""

    return {key: value for key, value in page_data.items() if key in PAGE_KEY_FILTER}

def format_post_data(post_data):
    """Filter out fields from post_data that aren't in POST_KEY_FILTER."""

    return {key: value for key, value in post_data.items() if key in POST_KEY_FILTER}