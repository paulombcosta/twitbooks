import twitbooks.ner as ner
import twitbooks.sync as sync
import twitbooks.twitter as twitter
import twitbooks.book.api as book_api
import twitbooks.console as console
from twitbooks.renderer import render
from typing import List
from twitbooks.sync import SyncValue, JsonBodySyncValue
import json
import click
from twitbooks.sync import SyncError
from twitbooks.config import get_config, init
from twitbooks.ner import is_model_downloaded
from rich.prompt import Confirm
import sys


def _run(user: str) -> sync.SyncResult:

    init()
    config = get_config()

    if not is_model_downloaded(lang=config.lang, size=config.size):
        proceed = Confirm.ask("Language model is not downloaded. Download now ?")
        if proceed:
            ner.download_and_extract_model(lang=config.lang, size=config.size)
        else:
            sys.exit(1)

    ner_extractor = ner.new(lang=config.lang, size=config.size)

    twitter_api, err = twitter.new()
    if err is not None:
        console.error(err.msg)

    books_api = book_api.new()
    book_sync = sync.new(twitter_api, ner_extractor, books_api)
    return book_sync.sync(user)


def _write_results(template: str):
    with open("./books.html", "w", newline="\n") as doc:
        doc.write(template)
    console.info("results saved in ./books.html")


def _to_json_body(value: SyncValue) -> str:
    res = {'twitter_link': value.twitter_link, 'book_title': value.book_title, 'book_link': value.book_link}
    if value.book_title is not None:
        res['book_image'] = value.book_image
    return json.dumps(res)


def _add_json_body(res: List[SyncValue]) -> List[JsonBodySyncValue]:
    return list(map(lambda x: JsonBodySyncValue(
        twitter_link=x.twitter_link,
        book_title=x.book_title,
        book_link=x.book_link,
        book_image=x.book_image,
        json_body=_to_json_body(x)
    ), res))


def _handle_error(user: str, err: SyncError):
    if err == SyncError.ERR_RATE_LIMITED:
        console.error("Rate limit reached when requesting timeline")
    elif err == SyncError.ERR_USER_NOT_FOUND:
        console.error("User {} not found".format(user))
    else:
        console.error("Unknown error")


@click.command()
@click.option('-u', '--user', required=True, type=str)
def start_sync(user: str):
    """ searches for books in the user twitter timeline
    """
    res = _run(user)
    if res.error is not None:
        _handle_error(user, res.error)
        return
    res = render(_add_json_body(res.result))
    _write_results(res)


if __name__ == '__main__':
    start_sync()
