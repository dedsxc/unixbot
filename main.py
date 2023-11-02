import os
import threading

from internal.api.reddit import RedditScraper
from internal.unixporn.unixporn import Unixporn


class Bot:
    def __init__(self):
        self.reddit_client = RedditScraper(user_agent=os.environ['REDDIT_USERNAME'],
                                           client_id=os.environ['REDDIT_CLIENT_ID'],
                                           client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                                           username=os.environ['REDDIT_USERNAME'],
                                           password=os.environ['REDDIT_PASSWORD'])
        self.unixporn = Unixporn()
        self.thread_post_tweet_daily = threading.Thread(target=self.unixporn.post_tweet_daily,args=(self.reddit_client,))
        #self.thread_post_fav_tweet = threading.Thread(target=self.unixporn.post_fav_tweet,args=(self.twitter_scrapper,))

    def start(self):
        self.thread_post_tweet_daily.start()
        #self.thread_post_fav_tweet.start()


if __name__ == '__main__':
    bot = Bot()
    bot.start()
