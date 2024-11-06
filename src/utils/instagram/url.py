import re

INSTAGRAM_LINK_PATTERN = re.compile(
    r"(?:https?://)?(?:www.)?instagram.com/?([a-zA-Z0-9._\-]+)?"
    r"/(p+)?([reel]+)?([tv]+)?([stories]+)?/([a-zA-Z0-9\-_.]+)/?([0-9]+)?"
)


def extract_instagram_link(msg: str) -> str | None:
    """
    Extract Instagram post link from text message.

    :param msg: Some message
    :return: Link
    """
    match = INSTAGRAM_LINK_PATTERN.search(msg)
    if not match:
        return None
    link = match.group(0)
    return link
