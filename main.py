import threading
import os

# Common
from internal.config import config
from common.common import dir_exist
from common.logger import log

# Services
from internal.services.redis import RedisDataManager
from internal.api.reddit import RedditScraper

# Bot functions
from internal.bot.reddit import RedditBot
from internal.bot.lemmy import LemmyBot


def main():
    media_directory = os.path.join(os.getcwd(), 'medias')
    screenshot_directory = os.path.join(os.getcwd(), 'screenshot')
    dir_exist(media_directory)
    dir_exist(screenshot_directory)
    
    # Initialize Redis Data Manager
    db = RedisDataManager(host=config.get('redis', 'host'))
    
    # Start bots based on configuration
    if config.getboolean('lemmy', 'enabled'):
        thread_run_lemmy_bot = threading.Thread(target=LemmyBot().run, args=(db, config.get('lemmy', 'community_name')))
        thread_run_lemmy_bot.start()
        log.info("[main] Lemmy bot started with community: {}".format(config.get('lemmy', 'community_name')))
    if config.getboolean('reddit', 'enabled'):
        thread_run_reddit_bot = threading.Thread(target=RedditBot().run, args=(db, 
                                                                               config.get('reddit', 'subreddit'),
                                                                               RedditScraper(
                                                                                   user_agent=config.get('reddit', 'username'),
                                                                                   client_id=config.get('reddit', 'client_id'),
                                                                                   client_secret=config.get('reddit', 'client_secret'),
                                                                                   username=config.get('reddit', 'username'),
                                                                                   password=config.get('reddit', 'password'),
                                                                                   flair_list=config.get('reddit', 'flair_list').split(',')
                                                                               )
                                                                           ))
        thread_run_reddit_bot.start()
        log.info("[main] Reddit bot started with subreddit: {}".format(config.get('reddit', 'subreddit')))

if __name__ == '__main__':
    main()
