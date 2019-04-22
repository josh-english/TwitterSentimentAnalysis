# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db


# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


class DaysStats(Base):
    range_start = db.Column(db.DateTime, nullable=False)
    range_end = db.Column(db.DateTime, nullable=False)
    candidate = db.Column(db.String(256), nullable=False)
    total_tweets = db.Column(db.Integer(), nullable=False, default=0)
    average_sentiment = db.Column(db.Float(), nullable=False)


class Tweet(Base):
    __tablename__ = 'tweet'
    twitter_id = db.Column(db.String(256), nullable=False)
    text = db.Column(db.String(512), nullable=False)
    username = db.Column(db.String(256), nullable=False)
    candidate = db.Column(db.String(256), nullable=False)
    retweets = db.Column(db.Integer(), nullable=False, default=0)
    favorites = db.Column(db.Integer(), nullable=False, default=0)
    sentiment = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float(), nullable=False)
    longitude = db.Column(db.Float(), nullable=False)

    def as_dict(self):
        a_dict = {'text': self.text,
                  'username': self.username,
                  'candidate': self.candidate,
                  'retweets': self.retweets,
                  'favorites': self.favorites,
                  'sentiment': self.sentiment,
                  'created_at': self.created_at,
                  'latitude': self.latitude,
                  'longitude': self.longitude}
        return a_dict
