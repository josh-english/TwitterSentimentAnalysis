# Import flask dependencies
from flask import Blueprint, request, render_template, \
    flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import app

from .TweetFetcher import TweetFetcher

# Import module models (i.e. User)
from app.twitter_visualization.models import Tweet

# Define the blueprint: 'auth', set its url prefix: app.url/auth
index_blueprint = Blueprint('index', __name__)

tweet_fetcher = TweetFetcher()


@app.route('/', methods=['GET'])
def index():
    print('hit index route\n\n')
    print(tweet_fetcher.get_tweets(query='Donald', count=200))
    print('\n\nFrom DB')
    print(Tweet.query.all())
    return render_template("index.html")

