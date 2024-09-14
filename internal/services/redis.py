import redis
from common.logger import log


class RedisDataManager:
    def __init__(self, host):
        self.key = "submission_ids"
        try:
            self.conn = redis.Redis(host=host, port=6379, db=0)
        except redis.ConnectionError as e:
            log.error(f"Failed to connect to Redis: {e}")

    def insert_data(self, value):
        try:
            self.conn.sadd(self.key, value)
            log.info(f"Inserted {value} into {self.key}")
        except redis.RedisError as e:
            log.error(f"Error inserting data into Redis: {e}")

    def check_data_exist(self, value):
        try:
            if self.conn.sismember(self.key, value):
                log.info(f"Post ID {value} exists in Redis")
                return True
            else:
                return False
        except redis.RedisError as e:
            log.error(f"Error checking data in Redis: {e}")
            return False
