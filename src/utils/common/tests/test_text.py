import pytest

from utils.common.text import remove_hashtags


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", ""),
        ("#", "#"),
        ("test", "test"),
        ("#some_hashtag", ""),
        ("#010", ""),
        ("#нетвойне", ""),
        ("#do i send", " i send"),
        ("i #send video", "i  video"),
        ("i send #video", "i send "),
    ],
)
def test_remove_hashtags(text: str, expected: str):
    assert remove_hashtags(text) == expected
