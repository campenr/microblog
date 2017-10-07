# Copyright 2016 Richard Campen
# All rights reserved

"""Flask based micro-blogging service.

# microblog 0.1.0

For complete documentation see README.md.
"""

# Set the values below as indicated, and rename this file to __init__.py

import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True

# Set this to something unique
SECRET_KEY = os.urandom(24)

# Set this to the URI to the database that you wish to use for this application
SQLALCHEMY_DATABASE_URI = ""

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False
