import pytest

from utils.youtube.url import extract_youtube_link


@pytest.mark.parametrize(
    ("msg", "expected"),
    [
        # Basic testcases
        (
            "https://www.youtube.com/watch?v=some_id",
            "https://www.youtube.com/watch?v=some_id",
        ),
        (
            "i sent https://www.youtube.com/watch?v=some_id",
            "https://www.youtube.com/watch?v=some_id",
        ),
        (
            "do i https://www.youtube.com/watch?v=some_id like",
            "https://www.youtube.com/watch?v=some_id",
        ),
        (
            "https://www.youtube.com/watch?v=some_id like",
            "https://www.youtube.com/watch?v=some_id",
        ),
        # Mobile version testcases
        ("https://youtu.be/some_id", "https://youtu.be/some_id"),
        ("https://youtu.be/some_id/", "https://youtu.be/some_id/"),
        # YouTube Short links testcases
        ("https://youtube.com/shorts/some_id", "https://youtube.com/shorts/some_id"),
        ("https://youtube.com/shorts/some_id/", "https://youtube.com/shorts/some_id/"),
        (
            "i like https://youtube.com/shorts/some_id",
            "https://youtube.com/shorts/some_id",
        ),
        (
            "https://youtube.com/shorts/some_id like",
            "https://youtube.com/shorts/some_id",
        ),
        (
            "i like https://youtube.com/shorts/some_id do",
            "https://youtube.com/shorts/some_id",
        ),
        # Negative testcases
        ("", None),
        ("i see you", None),
    ],
)
def test_extract_youtube_link(msg: str, expected: str | None):
    actual = extract_youtube_link(msg)
    assert actual == expected
