from tweepy.error import TweepError
import twitbooks.sync as sync
from unittest.mock import Mock
from twitbooks.twitter import TimelineResult, Tweet
from twitbooks.book.api import BookInfo


def test_user_not_found_is_handled():
    t_api = Mock()
    t_api.user_timeline = Mock(side_effect=TweepError(None, None, 34))

    s = sync.new(t_api, None, None)
    assert s.sync('someuser').error == sync.SyncError.ERR_USER_NOT_FOUND


def test_rate_limit_error_is_handled():
    t_api = Mock()
    t_api.user_timeline = Mock(side_effect=TweepError(None, None, 88))

    s = sync.new(t_api, None, None)
    assert s.sync('someuser').error == sync.SyncError.ERR_RATE_LIMITED


def test_unknown_twitter_error_is_handled():
    t_api = Mock()
    t_api.user_timeline = Mock(side_effect=TweepError(None, None, 144))

    s = sync.new(t_api, None, None)
    assert s.sync('someuser').error == sync.SyncError.ERR_UNKNOWN


def test_twitter_link_is_valid():
    t_api = Mock()
    t_result: TimelineResult = TimelineResult(max_id=123, tweets=[Tweet(id_str="123", text="")])
    t_api.user_timeline = Mock(return_value=t_result)

    ner = Mock()
    ner.process = Mock(return_value="Harry")

    book_api = Mock()
    book_api.get_info = Mock(return_value=BookInfo(title="", link="", image_link=""))

    s = sync.new(t_api, ner, book_api)
    res = s.sync("someuser", num_iterations=1)
    assert len(res.result) == 1
    assert res.result[0].twitter_link == "https://twitter.com/someuser/status/123"


def test_sync_should_stop_on_error():
    t_api = Mock()
    t_api.user_timeline = Mock(side_effect=TweepError(None, None, 88))

    s = sync.new(t_api, None, None)
    s.sync("someuser", num_iterations=5)
    t_api.user_timeline.assert_called_once()
