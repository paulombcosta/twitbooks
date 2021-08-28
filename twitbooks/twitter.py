import tweepy
import os

from tweepy import API
from pydantic import BaseModel
from typing import List, Tuple


class Tweet(BaseModel):
    text: str
    id_str: str


class TimelineResult(BaseModel):
    max_id: int
    tweets: List[Tweet]


class TwitterConfigError(BaseModel):
    msg: str


class TwitterApi:

    def __init__(self, tweepy_api: API):
        self.tweepy_api = tweepy_api

    def verify_credentials(self):
        return self.tweepy_api.verify_credentials()

    def user_timeline(self, screen_name: str, count: int, max_id: int = None) -> TimelineResult:
        return _parse_timeline(self._get_timeline(screen_name, count, max_id))

    def get_user(self, screen_name: str):
        return self.tweepy_api.get_user(screen_name=screen_name)

    def rate_limit_status(self):
        return self.tweepy_api.rate_limit_status()

    def _get_timeline(self, screen_name: str, count: int, max_id: int = None):
        if max_id is None:
            return self.tweepy_api.user_timeline(screen_name=screen_name, count=count)
        return self.tweepy_api.user_timeline(screen_name=screen_name, count=count, max_id=max_id)


def _parse_timeline(timeline: any) -> TimelineResult:
    return TimelineResult(max_id=timeline.max_id, tweets=list(map(lambda tweet: _parse_tweet(tweet), timeline)))


def _parse_tweet(tweet: any) -> Tweet:
    return Tweet(id_str=tweet.id_str, text=tweet.text)


def _get_api() -> Tuple[TwitterApi, TwitterConfigError]:
    keys = {key: os.getenv(key) for key in ["TWITTER_CONSUMER_KEY",
                                            "TWITTER_CONSUMER_SECRET",
                                            "TWITTER_ACCESS_TOKEN_KEY",
                                            "TWITTER_ACCESS_TOKEN_SECRET"]}

    errors = [k for k, v in keys.items() if v is None]

    if len(errors) > 0:
        return None, TwitterConfigError(msg="{} must be present on the environment".format(",".join(errors)))

    auth = tweepy.OAuthHandler(keys["TWITTER_CONSUMER_KEY"], keys["TWITTER_CONSUMER_SECRET"])
    auth.set_access_token(keys["TWITTER_ACCESS_TOKEN_KEY"], keys["TWITTER_ACCESS_TOKEN_SECRET"])
    api = tweepy.API(auth)
    return TwitterApi(api), None


def new() -> Tuple[TwitterApi, TwitterConfigError]:
    return _get_api()
