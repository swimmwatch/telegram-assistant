import pytest

from utils.instagram.url import extract_instagram_link


@pytest.mark.parametrize(
    ("msg", "expected"),
    [
        # Basic testcases
        (
            "http://www.instagram.com/p/some_id/",
            "http://www.instagram.com/p/some_id/",
        ),
        (
            "https://www.instagram.com/p/some_id/",
            "https://www.instagram.com/p/some_id/",
        ),
        (
            "i sent http://www.instagram.com/p/some_id/",
            "http://www.instagram.com/p/some_id/",
        ),
        (
            "do i https://www.instagram.com/p/some_id/ like",
            "https://www.instagram.com/p/some_id/",
        ),
        (
            "https://www.instagram.com/p/some_id/ like",
            "https://www.instagram.com/p/some_id/",
        ),
        # Negative testcases
        ("", None),
        ("i see you", None),
    ],
)
def test_extract_instagram_link(msg: str, expected: str | None):
    actual = extract_instagram_link(msg)
    assert actual == expected
