import sys
import os
from optparse import OptionParser

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from microblog.models import User


def add_user():
    """Add a new user to the User database."""

    parser = OptionParser()
    parser.add_option("-u", "--username", dest="username", help="username for new user")
    parser.add_option("-p", "--password", dest="password", help="password for new user")

    (options, args) = parser.parse_args()

    user = User.add_user(username=options.username, password=options.password)
    print(user)

    return

if __name__ == '__main__':
    add_user()