import re

TIKTOK_LINK_PATTERN = re.compile(
    r"https?://" r"(?:www|m|vt|vm)\." r"(?:tiktok\.com)\/" r"(?:[\w/?=@.&]+)?"
)


def extract_tiktok_link(text: str) -> str | None:
    """
    Extract TikTok link from text.

    :param text: Some text
    :return: Extracted TikTok link
    """
    match = re.search(TIKTOK_LINK_PATTERN, text)
    if not match:
        return None
    link = match.group(0)
    return link
