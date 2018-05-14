import re

from mipt_redmine.database import commit_session
from mipt_redmine.models import Feed
from mipt_redmine.bot import bot


def check_updates():
    with commit_session() as session:
        author_pattern = re.compile('(.+)(\s\(.+\))?')
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
            session.flush()
            for entry in deleted_entries:
                session.delete(entry)
            session.flush()
            for entry in new_entries:
                author_name_email = entry.author
                groups = author_pattern.search(author_name_email).groups()
                author_name = groups[0] if len(groups) > 0 else ''
                bot.send_message(feed.chat.id,
                                 'Новая задача - *%s*\n\nАвтор: %s\n\n%s\n\n%s' % (feed.name,
                                                                                   author_name,
                                                                                   entry.title,
                                                                                   entry.url),
                                 parse_mode='Markdown')
