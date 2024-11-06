import re

YOUTUBE_LINK_PATTERN = re.compile(
    r"((?:https?:)?\/\/)?((?:www|m)\.)?"
    r"((?:youtube(-nocookie)?\.com|youtu.be))"
    r"(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?"
)


def extract_youtube_link(msg: str) -> str | None:
    """
    Extract link from text message.
    :param msg: Some message
    :return: Link
    """
    match = YOUTUBE_LINK_PATTERN.search(msg)
    if not match:
        return None
    link = match.group(0)
    return link
