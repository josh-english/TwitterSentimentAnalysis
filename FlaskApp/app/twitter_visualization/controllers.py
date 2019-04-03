# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db, app

# Import module models (i.e. User)
from app.twitter_visualization.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
index_blueprint = Blueprint('index', __name__)

@app.route('/', methods=['GET'])
def signin():
    print('hit index route')

    return render_template("index.html")