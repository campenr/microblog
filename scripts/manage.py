"""
To setup migrations run 'python manage.py db init'
To create a migration script, under the correct environment run 'python manage.py db migrate'
Manually check the migration script to check it is correct.
To upgrade the database using the latest migration script run 'python manage.py db upgrade'
To downgrade the database to the previous version run 'python manage.py db downgrade'
"""

import sys
import os

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from projects import app, db


app.config.from_object('config')
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
