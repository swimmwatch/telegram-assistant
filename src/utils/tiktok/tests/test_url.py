from typing import Optional

import pytest

from utils.tiktok.url import extract_tiktok_link


@pytest.mark.parametrize(
    ("msg", "expected"),
    [
        # Basic testcases
        (
            "https://www.tiktok.com/@user/video/some_id",
            "https://www.tiktok.com/@user/video/some_id",
        ),
        (
            "i sent https://www.tiktok.com/@user/video/some_id",
            "https://www.tiktok.com/@user/video/some_id",
        ),
        (
            "do i https://www.tiktok.com/@user/video/some_id like",
            "https://www.tiktok.com/@user/video/some_id",
        ),
        (
            "https://www.tiktok.com/@user/video/some_id like",
            "https://www.tiktok.com/@user/video/some_id",
        ),
        # Mobile version testcases
        ("https://vm.tiktok.com/some_id", "https://vm.tiktok.com/some_id"),
        ("i like https://vm.tiktok.com/some_id", "https://vm.tiktok.com/some_id"),
        ("https://vm.tiktok.com/some_id like", "https://vm.tiktok.com/some_id"),
        ("i like https://vm.tiktok.com/some_id do", "https://vm.tiktok.com/some_id"),
        # Negative testcases
        ("", None),
        ("i see you", None),
    ],
)
def test_extract_tiktok_link(msg: str, expected: Optional[str]):
    actual = extract_tiktok_link(msg)
    assert actual == expected
