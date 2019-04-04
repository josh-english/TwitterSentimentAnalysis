from app import db
from app.twitter_visualization.models import Tweet

import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob


class TweetFetcher:
    """
    Generic Twitter Class for sentiment analysis.
    """

    def __init__(self):
        """
        Class constructor or initialization method.
        """
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'A6xpOxQJXPh4KuN0bBuJ4KYOf'
        consumer_secret = 'vQymfJkJy5YtGwsfFFMdPfjl2epVcfztFu8jGLSj4V0bzQoeMV'
        access_token = '930581527968219136-guZY4MWui7YkkUaC7O3S6LB1dfDoFji'
        access_token_secret = '7su6tFi4Nf66hWmzFgxlmNXgyucp4LADIUcs0oxXs9wlV'

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        """
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        """
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) \n {36}|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        """
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        """
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        return analysis.sentiment.polarity

    def get_tweets(self, query, count=10):
        """
        Main function to fetch tweets and parse them.
        """
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q=query, count=count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
                # add the date created to our dictionary
                parsed_tweet['created_at'] = tweet.created_at
                parsed_tweet['retweet_count'] = tweet.retweet_count
                parsed_tweet['favorite_count'] = tweet.favorite_count
                parsed_tweet['coordinates'] = tweet.coordinates

                if parsed_tweet['coordinates'] is not None:
                    # appending parsed tweet to tweets list
                    if tweet.retweet_count > 0:
                        # if tweet has retweets, ensure that it is appended only once
                        # Make sure the coordinates value isn't null too
                        if parsed_tweet not in tweets:
                            tweets.append(parsed_tweet)
                    else:
                        tweets.append(parsed_tweet)

                # return parsed tweets
            self.add_tweets_to_db(tweets)
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))

    # Adds completed tweet objects to the db. Assumes the tweets are fully updated.
    def add_tweets_to_db(self, tweets):
        for tweet in tweets:
            db_tweet = Tweet(text=tweet['text'], retweets=tweet['retweet_count'],  favorites=tweet['favorite_count'],
                             sentiment=tweet['sentiment'], created_at=tweet['created_at'],
                             latitude=tweet['coordinates'].coordinates.latitude,
                             longitude=tweet['coordinates'].coordinates.longitude)
            db.session.add(db_tweet)
