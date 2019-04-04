import tweepy
import json
from app import db
from app.twitter_visualization.models import Tweet
from textblob import TextBlob
import re
from datetime import datetime, timedelta
from email.utils import parsedate_tz


# override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        print('Error: ' + status_code)
        # 420 (blaze it) is the tweepy error code for rate limiting meaning we need to disconnect
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def on_data(self, data):
        tweet = json.loads(data)

        tweets = []
        # empty dictionary to store required params of a tweet
        parsed_tweet = {}

        # saving text of tweet
        parsed_tweet['text'] = tweet['text'].lower()
        parsed_tweet['candidate'] = self.get_candidate(tweet['text'].lower())
        if parsed_tweet['candidate'] is None:
            # keep the stream open but we don't care about this tweet
            return True
        # saving sentiment of tweet
        parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet['text'])
        # add the date created to our dictionary
        parsed_tweet['created_at'] = self.to_datetime(tweet['created_at'])
        parsed_tweet['retweet_count'] = tweet['retweet_count']
        parsed_tweet['favorite_count'] = tweet['favorite_count']
        if tweet['coordinates'] is not None:
            parsed_tweet['coordinates'] = tweet['coordinates']['coordinates']
        elif tweet['place'] is not None:
            parsed_tweet['coordinates'] = tweet['place']['bounding_box']['coordinates'][0][0]
        else:
            parsed_tweet['coordinates'] = None

        if parsed_tweet['coordinates'] is not None:
            # appending parsed tweet to tweets list
            if tweet['retweet_count'] > 0:
                # if tweet has retweets, ensure that it is appended only once
                # Make sure the coordinates value isn't null too
                if parsed_tweet not in tweets:
                    tweets.append(parsed_tweet)
            else:
                tweets.append(parsed_tweet)

            # return parsed tweets
        self.add_tweets_to_db(tweets)
        return True

    # Adds completed tweet objects to the db. Assumes the tweets are fully updated.
    def add_tweets_to_db(self, tweets):
        for tweet in tweets:
            db_tweet = Tweet(text=tweet['text'], retweets=tweet['retweet_count'], favorites=tweet['favorite_count'],
                             sentiment=tweet['sentiment'], created_at=tweet['created_at'],
                             latitude=tweet['coordinates'][1],
                             longitude=tweet['coordinates'][0],
                             candidate=tweet['candidate'])
            db.session.add(db_tweet)
            db.session.commit()

    def get_tweet_sentiment(self, tweet):
        """
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        """
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        return analysis.sentiment.polarity

    def get_candidate(self, text):
        # tweet_streamer.filter(track=['Donald', 'Trump', 'Tim Ryan', 'Gillibrand', 'Beto', 'O\'Rourke', 'ORourke',
        #                              'Hickenlooper', 'inslee', 'bernie', 'sanders', 'klobuchar', 'Warren',
        #                              'Kamala Harris',
        #                              'Buttigeig', 'buttigieg', 'Julian Castro', 'John Delaney', 'Tulsi Gabbard',
        #                              'Cory Booker',
        #                              'Biden'])
        if 'donald' in text or 'trump' in text:
            return 'trump'
        elif 'tim ryan' in text or 'timryan' in text:
            return 'ryan'
        elif 'gillibrand' in text:
            return 'gilliband'
        elif 'beto' in text or 'orourke' in text or 'o\'rourke' in text:
            return 'rourke'
        elif 'hickenlooper' in text:
            return 'hickenlooper'
        elif 'inslee' in text:
            return 'inslee'
        elif 'bernie' in text or 'sanders' in text:
            return 'sanders'
        elif 'klobuchar' in text:
            return 'klobuchar'
        elif 'warren' in text:
            return 'warren'
        elif 'kamala' in text:
            return 'harris'
        elif 'buttigeig' in text or 'buttigieg' in text:
            return 'buttigieg'
        elif 'julian castro' in text or 'juliancastro' in text:
            return 'castro'
        elif 'john delaney' in text or 'johnkdelaney' in text:
            return 'delaney'
        elif 'tulsi gabbard' in text or 'tulsigabbard' in text:
            return 'gabbard'
        elif 'corey booker' in text or 'coreybooker' in text:
            return 'booker'
        elif 'biden' in text:
            return 'biden'
        else:
            return None

    def clean_tweet(self, tweet):
        """
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        """
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) \n {36}|(\w+:\/\/\S+)", " ", tweet).split())

    @staticmethod
    def to_datetime(datestring):
        time_tuple = parsedate_tz(datestring.strip())
        dt = datetime(*time_tuple[:6])
        return dt - timedelta(seconds=time_tuple[-1])