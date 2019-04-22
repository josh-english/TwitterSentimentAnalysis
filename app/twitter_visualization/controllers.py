# Import flask dependencies
from flask import Blueprint, request, render_template, jsonify

# Import the database object from the main app module
from app import app
from threading import Thread

from .TweetStreamer import MyStreamListener

# Import module models (i.e. User)
from app.twitter_visualization.models import Tweet, DaysStats
from tweepy import OAuthHandler
import tweepy
from app import db

# Define the blueprint: 'auth', set its url prefix: app.url/auth
index_blueprint = Blueprint('index', __name__)
fetch_blueprint = Blueprint('fetch', __name__)

# keys and tokens from the Twitter Dev Console
consumer_key = 'A6xpOxQJXPh4KuN0bBuJ4KYOf'
consumer_secret = 'vQymfJkJy5YtGwsfFFMdPfjl2epVcfztFu8jGLSj4V0bzQoeMV'
access_token = '930581527968219136-guZY4MWui7YkkUaC7O3S6LB1dfDoFji'
access_token_secret = '7su6tFi4Nf66hWmzFgxlmNXgyucp4LADIUcs0oxXs9wlV'

# keys for heroku
# keys and tokens from the Twitter Dev Console
# consumer_key = 'MB8FIedv6xIA4m6ZjB6FGwGhW'
# consumer_secret = 'u1gbR8PeJy0ZgL3wLlKA8x9ZqtlmcE5dITr7ULXSv9VylQEuyY'
# access_token = '930581527968219136-R0fpb7ghJrBgRa9CWpWMjNFqLjMYRs1'
# access_token_secret = 'NCVT0Z2k8BXw6P48X5yKNjO8PwgV6y0PjbgWRVwRvabaD'

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
    tweet_streamer = tweepy.Stream(auth=api.auth, listener=MyStreamListener())
    thread = Thread(target=tweet_streamer.filter, kwargs={'locations': [-125, 25, -65, 48]})
    thread.start()

except ValueError as error:
    print("Error: Authentication Failed")


@app.route('/', methods=['GET'])
def index():
    if tweet_streamer is None:
        print('streamer is offline')
    print('hit index route\n\n')

    return render_template("index.html")


@app.route('/fetch', methods=['GET'])
def fetch():
    date_start = MyStreamListener.to_datetime(request.args.get('dateTime_start'))
    date_end = MyStreamListener.to_datetime(request.args.get('dateTime_end'))
    list_of_candidates = request.args.get('candidates')
    stats = {}
    serializable_tweets = []
    locations = {'lats': [], 'longs': [], 'sentiment': []}
    for candidate in list_of_candidates.split(','):
        tweets = Tweet.query.filter(Tweet.created_at <= date_end).filter(Tweet.created_at >= date_start) \
            .filter(Tweet.candidate == candidate).all()
        stats[candidate] = {'length': len(tweets)}
        sentiment_sum = 0
        if len(tweets) > 0:
            for tweet in tweets:
                dict_tweet = tweet.as_dict()
                locations['lats'].append(dict_tweet['latitude'])
                locations['longs'].append(dict_tweet['longitude'])
                locations['sentiment'].append(float(dict_tweet['sentiment']))
                sentiment_sum += float(dict_tweet['sentiment'])
                serializable_tweets.append(dict_tweet)
            average = sentiment_sum / len(tweets)
            stats[candidate]['avg_sentiment'] = average
            stats[candidate]['date_start'] = date_start
            stats[candidate]['date_end'] = date_end
        else:
            stats[candidate]['avg_sentiment'] = 0
            stats[candidate]['date_start'] = date_start
            stats[candidate]['date_end'] = date_end
        add_stats_to_db(stats)
    return jsonify({'stats': stats, 'tweets': serializable_tweets})


def add_stats_to_db(stats):
    for key, value in stats.items():
        existing_stats = DaysStats.query.filter_by(range_start=value['date_start']).filter_by(
                         range_end=value['date_end']).all()
        for s in existing_stats:
            db.session.delete(s)
        stat = DaysStats(candidate=key, range_start=value['date_start'],
                         range_end=value['date_end'], total_tweets=value['length'],
                         average_sentiment=value['avg_sentiment'])
        db.session.add(stat)
        db.session.commit()
