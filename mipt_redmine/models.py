import feedparser
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import relationship, backref

CHAT_STATE_WAIT_FEED_NAME = 'wait_feed_name'
CHAT_STATE_WAIT_FEED_URL = 'wait_feed_url'
CHAT_STATE_WAIT_FEED_DELETE = 'wait_delete'


@as_declarative()
class Base(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()
    id = Column(Integer(), primary_key=True)


class Chat(Base):
    state = Column(String(32))
    editing_feed_id = Column(String(32))  # TODO add foreign key
    editing_feed = relationship("Feed", uselist=False)


class Feed(Base):
    chat_id = Column(Integer, ForeignKey('chat.id'))
    name = Column(String(255))
    url = Column(Text)
    chat = relationship("Chat", back_populates="feeds")

    def get_entries(self):
        return {entry.url: entry for entry in self.entries}

    def fetch_entries(self):
        """

        :rtype: list
        """
        atom = feedparser.parse(self.url)
        if 'entries' in atom:
            return {entry.link: Entry.create_from_atom_entry(self, entry) for entry in atom.entries}
        return {}


Chat.feeds = relationship("Feed", order_by=Feed.id, back_populates="chat")


class Entry(Base):

    feed_id = Column(Integer, ForeignKey('feed.id'))
    url = Column(String(255))
    title = Column(String(255))
    author = Column(String(255))
    feed = relationship("Feed", back_populates="entries")

    @staticmethod
    def create_from_atom_entry(feed, atom_entry):
        """

        :type feed: Feed
        :type atom_entry: feedparser.FeedParserDict
        :rtype: Entry
        """
        entry = Entry()
        entry.feed_id = feed.id
        entry.url = atom_entry.link
        entry.author = atom_entry.author
        title = atom_entry.title
        if len(title) > 255:
            title = title[:252] + '...'
        entry.title = title
        return entry


Feed.entries = relationship("Entry", order_by=Entry.id, back_populates="feed")
