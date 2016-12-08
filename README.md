# microvlog 0.1.0

## Description

A Flask based micro-blogging service.

## Deployment

Use ``pip install -r requirements.txt`` to install the required package dependencies.

The application uses an SQL based database to store the user and link information ([PostgreSQL](https://www.postgresql.org/)
 recommended.)

Before the first use create a valid configuration file using the instructions provided by the example file in ``config/``.
Specifically, provide a secret key and a valid URI to an SQL database. 

During development you can run the application using ``run.py`` directly, but for deployment I recommend using 
[uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) or equivalent to serve the application behind a web server like
[nginx](https://www.nginx.com/). There are many good examples out there for how to serve Flask applications with uWSGI
and nginx.
