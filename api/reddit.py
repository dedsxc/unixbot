import praw

from common.logger import log


class RedditScraper:
    def __init__(self, user_agent, client_id, client_secret, username, password):
        self.user_agent = user_agent
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.client = praw.Reddit(
            user_agent=self.user_agent,
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password,
        )
        log.info("[praw] version {}".format(praw.__version__))
        log.info('[authentication][reddit] Connected as {}'.format(self.client.user.me()))

    def get_latest_post(self):
        try:
            subreddit = self.client.subreddit('unixporn').new(limit=1)
            return next(subreddit)
        except Exception as e:
            log.error("[get_latest_post] Error while getting latest post on reddit: {}".format(e))

    def get_post_by_id(self, submission_id):
        return self.client.submission(id=submission_id)

    def get_config_comment_on_post(self, submission_id):
        submission = self.client.submission(id=submission_id)
        # Look for the author comment of the post and check if he post his configuration
        for comment in list(submission.comments):
            if comment.author == submission.author:
                if "https" in comment.body.lower():
                    log.info(f"[get_config_comment_on_post] configuration comment found !\n{comment.body}")
                    # If the comment length is more than the maximum character allowed in twitter
                    # return the link of the comment
                    if len(comment.body) > 280:
                        link = f"https://www.reddit.com/{comment.permalink}"
                        return link
                    else:
                        return comment.body
        return None
