from enum import Enum, auto
from tweepy.error import TweepError
from typing import List, Tuple, Optional

from twitbooks.twitter import TwitterApi
from twitbooks.ner import NER
from twitbooks.book.api import BookApi
from pydantic import BaseModel
from twitbooks.console import sync_progress
import twitbooks.console as console

MAX_ITERATIONS = 10


class SyncError(Enum):
    ERR_USER_NOT_FOUND = auto()
    ERR_UNKNOWN = auto()
    ERR_RATE_LIMITED = auto()

    def msg(self) -> str:
        if self == SyncError.ERR_USER_NOT_FOUND:
            return "User not found"
        if self == SyncError.ERR_RATE_LIMITED:
            return "Rate limited"
        if self == SyncError.ERR_UNKNOWN:
            return "Unknown Error"


class NERResult:
    def __init__(self, twitter_link: str, ner_result: str):
        self.twitter_link = twitter_link
        self.ner_result = ner_result


class SyncValue(BaseModel):
    twitter_link: str
    book_title: str
    book_link: str
    book_image: Optional[str]


class JsonBodySyncValue(SyncValue):
    json_body: str


class SyncResult(BaseModel):
    result: List[SyncValue]
    error: Optional[SyncError]


def new(twitter: TwitterApi, ner: NER, book_api: BookApi):
    return Sync(twitter, ner, book_api)


def err_status(e: TweepError) -> Optional[SyncError]:
    if e.api_code == 88:
        return SyncError.ERR_RATE_LIMITED
    if e.api_code == 34:
        return SyncError.ERR_USER_NOT_FOUND
    return SyncError.ERR_UNKNOWN


class Sync:
    def __init__(self, twitter: TwitterApi, ner: NER, book_api: BookApi):
        self.twitter = twitter
        self.ner = ner
        self.book_api = book_api

    def _sync_ner(self, screen_name: str, num_iterations=None) -> Tuple[List[NERResult], SyncError]:
        res: List[NERResult] = []
        max_id = None
        error: Optional[SyncError] = None
        max_iterations = num_iterations or MAX_ITERATIONS
        iterations = 0
        progress = sync_progress()
        task = progress.add_task(description="Searching user {} tweets for keywords".format(screen_name),
                                 total=max_iterations)
        with progress:
            while iterations <= max_iterations - 1:
                progress.update(task, advance=1)
                try:
                    iterations = iterations + 1
                    timeline = self.twitter.user_timeline(screen_name, 20, max_id)
                    max_id = timeline.max_id
                    if len(timeline.tweets) == 0:
                        print("no more tweets, stopping sync")
                    for tweet in timeline.tweets:
                        twitter_link = "https://twitter.com/{}/status/{}".format(screen_name, tweet.id_str)
                        ner_result = self.ner.process(tweet.text)
                        if len(ner_result) == 0:
                            continue
                        res.append(NERResult(twitter_link, ner_result[0]))
                except TweepError as e:
                    error = err_status(e)
                    break
        return res, error

    # TODO: can be done in parallel
    def _sync_book(self, ner: List[NERResult]) -> List[SyncValue]:
        res: List[SyncValue] = []
        progress = sync_progress()
        task = progress.add_task(description="Searching Google Books for matches", total=len(ner))
        with progress:
            for item in ner:
                book_info = self.book_api.get_info(item.ner_result)
                progress.update(task, advance=1)
                if book_info is None:
                    continue
                res.append(SyncValue(
                    twitter_link=item.twitter_link,
                    book_title=book_info.title,
                    book_link=book_info.link,
                    book_image=book_info.image_link
                ))
        return res

    def sync(self, screen_name: str, num_iterations: int = None) -> SyncResult:
        ner_results, err = self._sync_ner(screen_name, num_iterations)
        if err is not None:
            return SyncResult(result=[], error=err)
        if len(ner_results) == 0:
            console.info("No keywords could be found for user {}".format(screen_name))
        else:
            console.info("Extracted {} tokens".format(len(ner_results)))
        book_res = self._sync_book(ner_results)
        return SyncResult(result=book_res, error=None)
