import os
import time

# API
from internal.api.interact_browser import tweet_with_media
from internal.api.lemmy import LemmyScraper

# Common
from common.logger import log
from internal.config import config
from common.common import download_media

# Services
from internal.services.redis import RedisDataManager


class LemmyBot:
    def __init__(self):
        self.media_directory = os.path.join(os.getcwd(), 'medias')
        self.screenshot_directory = os.path.join(os.getcwd(), 'screenshot')
        self.delay = config.getint('lemmy', 'delay', fallback=300)
        self.allowed_media_extension = ["jpg", "jpeg", "png", "mp4", "gif", "webp"]

    def run(self, db: RedisDataManager, community_name):
        # Initialize Lemmy API client
        lemmyapi = LemmyScraper()
        while True:
            # Get last post from Lemmy r/unixporn
            lemmy_post = lemmyapi.get_latest_posts(limit=1, sort='New', community_name=community_name)
            try:
                # Check for lemmy post if it exists
                if not db.check_data_exist(lemmy_post['id']):
                    # Insert lemmy_post_id on database
                    db.insert_data(lemmy_post['id'])

                    log.info('[post_from_lemmy] New Lemmy post title: {}'.format(lemmy_post['name']))

                    if lemmy_post['url'].split(".")[-1] in self.allowed_media_extension:
                        lemmy_media_path = self.media_directory + "/" + lemmy_post['url'].split("/")[-1]
                        download_media(lemmy_post['url'], lemmy_media_path)
                        tweet_with_media(lemmy_media_path, lemmy_post['name'], lemmy_post['ap_id'], None)
                        os.remove(lemmy_media_path)
                    else:
                        log.warning("[post_from_lemmy] no media found: {}".format(lemmy_post['url']))
                        log.warning("[post_from_lemmy] url post: {}".format(lemmy_post['ap_id']))
            except Exception as e:
                log.error("[post_from_lemmy] Error while posting tweet: {}".format(e))
            time.sleep(self.delay)

    
