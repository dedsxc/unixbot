import tweepy
import pytz
from datetime import datetime, timedelta
from common.logger import log


class TwitterScrapper:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret) -> None:
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.client = tweepy.API
        log.info("[tweepy] version {}".format(tweepy.__version__))

    def authentication(self) -> tweepy.API:
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.client = tweepy.API(auth)
        if self.client.verify_credentials():
            log.info("[authentication][twitter] Authentication success")
        else:
            log.error("[authentication][twitter] Error during authentication")
            exit(0)
        return self.client

    def get_top_fav_tweets_of_the_week(self):
        timezone = pytz.timezone('UTC')
        now = datetime.now(timezone)
        one_week_ago = now - timedelta(days=6)
        # Retrieve all tweets from all time
        log.info("[get_top_fav_tweets_of_the_week] Process ...")
        tweets = []
        max_id = None
        while True:
            new_tweets = self.client.user_timeline(max_id=max_id)
            if not new_tweets:
                break
            tweets.extend(new_tweets)
            max_id = min([tweet.id for tweet in new_tweets]) - 1

        # Filter out tweets that were not created in the past 7 days
        tweets = [tweet for tweet in tweets if tweet.created_at >= one_week_ago]
        # Sort the tweets by the number of favorites they have received
        sorted_tweets = sorted(tweets, key=lambda x: x.favorite_count, reverse=True)

        # Get the top 4 most favorited tweets
        # Get the media url of the top 4 most favorited tweets
        top_4_tweets_media_url = []
        for tweet in sorted_tweets[:4]:
            top_4_tweets_media_url.append(self.get_media_url_from_id(tweet.id))

        # Concatenate the top_4_tweets_media_url list to a string
        medias_url = "\n".join(top_4_tweets_media_url)

        # Retrieve the url of tweet and add it in list
        tweet_url_array = []
        for url in top_4_tweets_media_url:
            tweet_url_array.append(url.split("/photo/1")[0])
        # Concatenate the top_4_tweets_url list to a string
        tweet_url = ""
        for i, elem in enumerate(tweet_url_array, start=1):
            tweet_url += f"{str(i)}. {elem}\n"

        return medias_url, tweet_url

    def get_media_url_from_id(self, tweet_id: int) -> str:
        tweet = self.client.get_status(tweet_id, tweet_mode='extended')
        # Get the media entity from the tweet
        media = tweet.entities["media"][0]
        # Get the URL of the media file
        expanded_url = media["expanded_url"]
        return expanded_url
