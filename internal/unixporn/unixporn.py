import os
import time
import requests

from internal.api.interact_browser import tweet_with_media
from internal.api.reddit import RedditScraper
from internal.api.lemmy import LemmyScraper
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
        self.allowed_media_extension = ["jpg", "jpeg", "png", "mp4", "gif", "webp"]
        directory.exist(self.media_directory)
        directory.exist(self.screenshot_directory)

    def post_tweet_daily(self, reddit_client: RedditScraper):
        # Connect to redis database
        db = RedisDataManager(host=os.environ["REDIS_HOST"])
        # Initialize Lemmy API client
        lemmyapi = LemmyScraper()
        while True:
            # Get last post from Reddit r/unixporn
            submission = reddit_client.get_latest_post()

            # Get last post from Lemmy r/unixporn
            lemmy_post = lemmyapi.get_latest_posts(limit=1, sort='New')

            try:
                # Check for reddit submission if it exists
                if not db.check_data_exist(submission.id):
                    # Insert submission_id on database
                    db.insert_data(submission.id)
                    
                    log.info('[post_tweet_daily] New Reddit post title: {}'.format(submission.title))
                    # Get comment on last post from Reddit
                    comment = reddit_client.get_config_comment_on_post(submission.id)

                    # check if submission content is a video
                    if submission.is_video:
                        filename = submission.media['reddit_video']['fallback_url'].split("/")[-2] + ".mp4"
                        reddit_media_path = self.media_directory + "/" + filename
                        self.download_media(submission.media['reddit_video']['fallback_url'], reddit_media_path)
                        tweet_with_media(reddit_media_path, submission.title, submission.shortlink, comment)
                        os.remove(reddit_media_path)

                    elif submission.url.split(".")[-1] in self.allowed_media_extension:
                        reddit_media_path = self.media_directory + "/" + submission.url.split("/")[-1]
                        self.download_media(submission.url, reddit_media_path)
                        tweet_with_media(reddit_media_path, submission.title, submission.shortlink, comment)
                        os.remove(reddit_media_path)

                    else:
                        log.warning("[post_tweet_daily] no media found: {}".format(submission.url))
                        log.warning("[post_tweet_daily] url post: {}".format(submission.shortlink))
                
                # Check for lemmy post if it exists
                if not db.check_data_exist(lemmy_post['id']):
                    # Insert lemmy_post_id on database
                    db.insert_data(lemmy_post['id'])
                    
                    log.info('[post_tweet_daily] New Lemmy post title: {}'.format(lemmy_post['name']))
                    
                    if lemmy_post['url'].split(".")[-1] in self.allowed_media_extension:
                        lemmy_media_path = self.media_directory + "/" + lemmy_post['url'].split("/")[-1]
                        self.download_media(lemmy_post['url'], lemmy_media_path)
                        tweet_with_media(lemmy_media_path, lemmy_post['name'], lemmy_post['ap_id'], None)
                        os.remove(lemmy_media_path)

                    else:
                        log.warning("[post_tweet_daily] no media found: {}".format(lemmy_post['url']))
                        log.warning("[post_tweet_daily] url post: {}".format(lemmy_post['ap_id']))
            except Exception as e:
                log.error("[post_tweet_daily] Error while posting tweet: {}".format(e))

            time.sleep(self.delay_post_tweet_daily)

    def download_media(self, url, filename):
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        try:
            response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            log.info(f"[download_media] Image saved to {filename}")
        except requests.RequestException as e:
            log.error(f"[download_media] Error downloading media: {e}")
            return None
