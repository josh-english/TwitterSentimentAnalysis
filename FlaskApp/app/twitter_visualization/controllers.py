# Import flask dependencies
from flask import Blueprint, request, render_template, \
    flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import app
from threading import Thread

from .TweetFetcher import TweetFetcher
from .TweetStreamer import MyStreamListener

# Import module models (i.e. User)
from app.twitter_visualization.models import Tweet
from tweepy import OAuthHandler
import tweepy

# Define the blueprint: 'auth', set its url prefix: app.url/auth
index_blueprint = Blueprint('index', __name__)
fetch_blueprint = Blueprint('fetch', __name__)

# keys and tokens from the Twitter Dev Console
consumer_key = 'A6xpOxQJXPh4KuN0bBuJ4KYOf'
consumer_secret = 'vQymfJkJy5YtGwsfFFMdPfjl2epVcfztFu8jGLSj4V0bzQoeMV'
access_token = '930581527968219136-guZY4MWui7YkkUaC7O3S6LB1dfDoFji'
access_token_secret = '7su6tFi4Nf66hWmzFgxlmNXgyucp4LADIUcs0oxXs9wlV'
tweet_fetcher = None
tweet_streamer = None
# attempt authentication
try:
    # create OAuthHandler object
    auth = OAuthHandler(consumer_key, consumer_secret)
    # set access token and secret
    auth.set_access_token(access_token, access_token_secret)
    # create tweepy API object to fetch tweets
    api = tweepy.API(auth)
    # tweet_fetcher = TweetFetcher()
    tweet_streamer = tweepy.Stream(auth=api.auth, listener=MyStreamListener())
    thread = Thread(target=tweet_streamer.filter, kwargs={'locations': [-125, 25, -65, 48]})


    # tweet_streamer.filter(track=['Donald', 'Trump', 'Tim Ryan', 'Gillibrand', 'Beto', 'O\'Rourke', 'ORourke',
    #                              'HIckenlooper', 'inslee', 'bernie', 'sanders', 'klobuchar', 'Warren', 'Kamala',
    #                              'Buttigeig', 'buttigieg', 'Julian Castro', 'John Delaney', 'Tulsi Gabbard', 'Cory Booker',
    #                              'Biden'])
except ValueError as error:
    print("Error: Authentication Failed")


@app.route('/fetch', methods=['GET'])
def fetch():
    if tweet_fetcher is None:
        return 'Auth Error with Twitter API'
    print('hit fetch route\n\n')
    print(tweet_fetcher.get_tweets(query='Donald', count=300))
    print('\n\nFrom DB')
    print(Tweet.query.all())
    return render_template("MostRecentTweets.html")


@app.route('/', methods=['GET'])
def index():
    if tweet_streamer is None:
        print('streamer is offline')
    print('hit index route\n\n')

    print('\n\nFrom DB')
    print(Tweet.query.all())
    return render_template("Index.html")
