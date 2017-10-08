from flask import Markup
from markdown import markdown
from CommonMark import commonmark


def format_markdown(text):

    common_marked = commonmark(text)

    return Markup(common_marked)