import os
import time
import urllib.request

from internal.api.interact_browser import tweet_with_media
from internal.api.reddit import RedditScraper
from common.logger import log
from internal.services.redis import RedisDataManager
from common import directory


class Unixporn:
    def __init__(self):
        self.cwd_path = os.getcwd()
        self.media_directory = os.path.join(self.cwd_path, 'medias')
        self.screenshot_directory = os.path.join(self.cwd_path, 'screenshot')
        self.delay_post_tweet_daily = 300
        self.delay_post_top_tweet = 3600
        self.emoji = ["🦦", "🚀", "👍", "📥", "🆕", "⚡︎", "😱", "😳", "🧙", "🦊", "🔥", "🥇", "🎖️", "🏅"]
        self.allowed_media_extension = ["jpg", "jpeg", "png", "mp4", "gif"]
        directory.exist(self.media_directory)
        directory.exist(self.screenshot_directory)

    def post_tweet_daily(self, reddit_client: RedditScraper):
        # Connect to redis database
        db = RedisDataManager(host=os.environ["REDIS_HOST"])

        while True:
            # Get last post from Reddit r/unixporn
            submission = reddit_client.get_latest_post()

            try:
                if not db.check_data_exist(submission.id):
                    # Insert submission_id on database
                    db.insert_data(submission.id)
                    
                    log.info('[post_tweet_daily] New post title: {}'.format(submission.title))
                    # Get comment on last post from Reddit
                    comment = reddit_client.get_config_comment_on_post(submission.id)

                    # check if submission content is a video
                    if submission.is_video:
                        filename = submission.media['reddit_video']['fallback_url'].split("/")[-1].split("?")[0]
                        local_filename, _ = urllib.request.urlretrieve(submission.media['reddit_video']['fallback_url'],
                                                                       filename=filename)
                        log.info('[post_tweet_daily] Media video: {}'.format(local_filename))
                        tweet_with_media(filename=self.cwd_path + "/" +local_filename, submission=submission, comment=comment)
                        os.remove(local_filename)

                    elif submission.url.split(".")[-1] in self.allowed_media_extension:
                        reddit_media_path = self.media_directory + "/" + submission.url.split("/")[-1]
                        local_filename, _ = urllib.request.urlretrieve(submission.url, filename=reddit_media_path)
                        log.info('[post_tweet_daily] Media: {}'.format(local_filename))
                        tweet_with_media(local_filename, submission, comment)
                        os.remove(local_filename)

                    else:
                        log.warning("[post_tweet_daily] no media found: {}".format(submission.url))
                        log.warning("[post_tweet_daily] url post: {}".format(submission.shortlink))

            except Exception as e:
                log.error("[post_tweet_daily] Error while posting tweet: {}".format(e))

            time.sleep(self.delay_post_tweet_daily)
