import os
import urllib.request
import time
import random

from api.twitter import TwitterScrapper
from api.reddit import RedditScraper
from common.logger import log
from services.data_handler import DataHandler
from common import directory


class Unixporn:
    def __init__(self, twitter_scrapper: TwitterScrapper):
        self.cwd_path = os.getcwd()
        self.media_directory = os.path.join(self.cwd_path, 'medias')
        self.delay_post_tweet_daily = 300
        self.delay_post_top_tweet = 3600
        self.app_version = os.environ["VERSION"]
        self.emoji = ["🦦", "🚀", "👍", "📥", "🆕", "⚡︎", "😱", "😳", "🧙", "🦊", "🔥", "🥇", "🎖️", "🏅"]
        self.allowed_media_extension = ["jpg", "jpeg", "png", "mp4", "gif"]
        self.twitter_client = twitter_scrapper.authentication()
        directory.exist(self.media_directory)

    def post_tweet_daily(self, reddit_client: RedditScraper):
        # Create database
        db = DataHandler(db_name="unixbot.db", table="reddit", column_name="reddit_id")
        db.create_table()

        # Update profile
        self.twitter_client.update_profile(
            description="🚀 Server version {}\n\nBuy me a coffee ☕️: https://www.buymeacoffee.com/bot_unixporn".format(
                self.app_version))
        while True:
            # Get last post from Reddit r/unixporn
            submission = reddit_client.get_latest_post()
            try:
                if not db.check_data_exist(data=submission.id):
                    log.info('[post_tweet_daily] New post title: {}'.format(submission.title))
                    # Get comment on last post from Reddit
                    comment = reddit_client.get_config_comment_on_post(submission.id)

                    # check if submission content is a video
                    if submission.is_video:
                        # download the video only if the duration is less than 140 sec allowed by twitter
                        # The output of submission.media['reddit_video']['fallback_url'] is on the following form
                        # https://v.redd.it/brj9krm7uf2b1/DASH_1080.mp4?source=fallback
                        filename = submission.media['reddit_video']['fallback_url'].split("/")[-1].split("?")[0]
                        local_filename, _ = urllib.request.urlretrieve(submission.media['reddit_video']['fallback_url'],
                                                                        filename=filename)
                        log.info('[post_tweet_daily] Media video: {}'.format(local_filename))
                        self.tweet_with_media(filename=local_filename, submission=submission, comment=comment,
                                                is_video=True)
                        os.remove(local_filename)

                    # Download media if exist
                    elif submission.url.split(".")[-1] in self.allowed_media_extension:
                        reddit_media_path = self.media_directory + "/" + submission.url.split("/")[-1]
                        local_filename, _ = urllib.request.urlretrieve(submission.url, filename=reddit_media_path)
                        log.info('[post_tweet_daily] Media: {}'.format(local_filename))
                        self.tweet_with_media(filename=local_filename, submission=submission, comment=comment,
                                              is_video=False)
                        os.remove(local_filename)
                    else:
                        log.warning("[post_tweet_daily] no media found: {}".format(submission.url))
                        log.warning("[post_tweet_daily] url post: {}".format(submission.shortlink))

                    # Insert submission_id on database
                    db.insert_data(submission.id)
            except Exception as e:
                log.error("[post_tweet_daily] Error while posting tweet: {}".format(e))

            time.sleep(self.delay_post_tweet_daily)

    def tweet_with_media(self, filename, submission, comment, is_video):
        # Tweet status with media
        try:
            if is_video:
                media = self.twitter_client.media_upload(filename, chunked=True, media_category="amplify_video")
            else:
                media = self.twitter_client.media_upload(filename)
            status = f'{random.choice(self.emoji)} - {submission.title}\nLink: {submission.shortlink} \n\nBuy me a coffee ☕️: https://www.buymeacoffee.com/bot_unixporn'
            tweet_status = self.twitter_client.update_status(status=status, media_ids=[media.media_id])
            log.info(f"[post_tweet_daily] Status updated\n{status}")
            # If comment exist, it means there is a configuration associated to the post
            if comment is not None:
                self.reply_to_status(tweet_status, comment)
        except Exception as e:
            log.error("[post_tweet_daily] Error while updating status with media: {}".format(e))

    def reply_to_status(self, tweet_status, comment):
        # Reply status with reddit configuration
        try:
            config_status = f"⚙️ Configuration below️\n{comment}"
            self.twitter_client.update_status(status=config_status, in_reply_to_status_id=tweet_status.id)
            log.info(f"[post_tweet_daily] Configuration status updated\n{config_status}")
        except Exception as e:
            log.error("[post_tweet_daily] Error while reply to status: {}".format(e))

    def post_fav_tweet(self, twitter_scrapper: TwitterScrapper):
        while True:
            now = time.localtime()
            if now.tm_wday == 6 and now.tm_hour == 17:
                media_urls, tweet_url = twitter_scrapper.get_top_fav_tweets_of_the_week()

                # Post 4 top fav config
                status = f'🚀 The top 4 of favorite linux configuration of this week 🏆\n---\n{media_urls}'
                tweet_status = self.twitter_client.update_status(status=status)
                log.info(f"[post_fav_tweet] Status posted: {status}")

                # Reply to the main tweet with url of config
                links = f"Links\n---\n{tweet_url}"
                self.twitter_client.update_status(status=links, in_reply_to_status_id=tweet_status.id)
                log.info(f"[post_fav_tweet] Link posted: {links}")
            time.sleep(self.delay_post_top_tweet)
