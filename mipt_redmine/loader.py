from mipt_redmine.database import Session
from mipt_redmine.models import Feed, Chat


def check_updates():
    session = Session()
    feeds = session.query(Feed).all()
    for feed in feeds:
        current_entries = feed.get_entries()
        fetched_entries = feed.fetch_entries()
        new_entries = list()
        deleted_entries = list()
        for url, entry in fetched_entries.items():
            if url not in current_entries:
                new_entries.append(entry)
                continue
        for url, entry in current_entries.items():
            if url not in fetched_entries:
                deleted_entries.append(entry)
        session.add_all(new_entries)
        for entry in deleted_entries:
            session.delete(entry)
    session.commit()


def add_new_chat(id):
    session = Session()
    chat = Chat()
    chat.id = id
    session.add(chat)
    session.commit()


def add_new_feed(chat_id, url):
    """

    :param chat_id: int
    :param url: str
    :rtype: bool
    """
    session = Session()
    feed = __create_feed(chat_id, url)
    if not __check_feed_exists(feed):
        session.add(feed)
        fetched_entries = feed.fetch_entries()
        session.add_all(fetched_entries)
        session.commit()
        return True
    return False


def __create_feed(chat_id, url):
    """

    :type url: str
    :type chat_id: int
    :rtype: Feed
    """
    feed = Feed()
    feed.chat_id = chat_id
    feed.url = url
    return feed


def __check_feed_exists(feed):
    """

    :type feed: Feed
    :rtype: bool
    """
    session = Session()
    return session.query(Feed).filter(Feed.chat_id == feed.chat_id,
                                      Feed.url == feed.url).first() is not None
