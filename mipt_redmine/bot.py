import re
import logging
import telebot
from configparser import ConfigParser
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from mipt_redmine.database import database
from mipt_redmine.models import Chat, \
    CHAT_STATE_WAIT_FEED_NAME, \
    CHAT_STATE_WAIT_FEED_URL, \
    CHAT_STATE_WAIT_FEED_DELETE, Feed
from mipt_redmine.messages import *

config = ConfigParser()
config.read('./config.ini')

if 'Bot' not in config:
    raise IndexError('Не заданы параметры бота')
if 'token' not in config['Bot'] or len(config['Bot']['token'].strip()) == 0:
    raise IndexError('Не задан токен бота')

telebot.logger.setLevel(logging.DEBUG)
bot = telebot.TeleBot(config['Bot']['token'])


@bot.message_handler(commands=['start'])
def send_welcome(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        chat = Chat()
        chat.id = message.chat.id
        session.add(chat)
        session.flush()
    bot.send_message(message.chat.id,
                     BOT_START,
                     disable_web_page_preview=True)
    session.commit()
    session.close()


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, BOT_HELP)


@bot.message_handler(commands=['add'])
def send_enter_feed_name(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat.state is not None:
        bot.send_message(message.chat.id, BOT_CHAT_STATE_NOT_EMPTY)
        return
    feed = Feed()
    feed.chat_id = chat.id
    session.add(feed)
    session.flush()
    chat.state = CHAT_STATE_WAIT_FEED_NAME
    chat.editing_feed_id = feed.id
    bot.send_message(message.chat.id, BOT_ADD)
    session.commit()
    session.close()


@bot.message_handler(commands=['remove'])
def send_remove_feed(message):
    markup = ReplyKeyboardMarkup(row_width=2)
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat.state is not None:
        bot.send_message(message.chat.id, BOT_CHAT_STATE_NOT_EMPTY)
        return
    feeds = chat.feeds
    chat.state = CHAT_STATE_WAIT_FEED_DELETE
    session.flush()
    for feed in feeds:
        markup.add(KeyboardButton(feed.name))
    bot.send_message(message.chat.id, BOT_REMOVE, reply_markup=markup)
    session.commit()
    session.close()


@bot.message_handler(commands=['cancel'])
def send_cancel(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat.editing_feed_id is not None:
        editing_feed = session.query(Feed).get(chat.editing_feed_id)
        session.delete(editing_feed)
        session.flush()
    chat.editing_feed_id = None
    chat.state = None
    bot.send_message(message.chat.id, BOT_CANCEL, reply_markup=ReplyKeyboardRemove())
    session.commit()
    session.close()


@bot.message_handler(commands=['list'])
def send_list(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat.state is not None:
        bot.send_message(message.chat.id, BOT_CHAT_STATE_NOT_EMPTY)
        return
    feeds = chat.feeds
    if len(feeds) != 0:
        items_text = '\n'.join(['%d. %s' % (i+1, feed.name) for i, feed in enumerate(feeds)])
        bot.send_message(message.chat.id, BOT_LIST % (len(feeds), items_text))
    else:
        bot.send_message(message.chat.id, BOT_LIST_EMPTY)
    session.commit()
    session.close()


@bot.message_handler()
def send_enter_feed_url(message):
    session = database.get_session()
    chat = session.query(Chat).get(message.chat.id)
    if chat.state == CHAT_STATE_WAIT_FEED_NAME:
        feed = session.query(Feed).get(chat.editing_feed_id)
        name = message.text.strip()
        if len(name) == 0:
            bot.send_message(message.chat.id, BOT_ADD_ERROR_NAME_EMPTY)
            return
        if session.query(Feed).filter(Feed.chat_id == chat.id, Feed.name == name).first() is not None:
            bot.send_message(message.chat.id, BOT_ADD_ERROR_NAME_EXISTS)
            return
        feed.name = message.text
        chat.state = CHAT_STATE_WAIT_FEED_URL
        bot.send_message(message.chat.id, BOT_ADD_URL)
    elif chat.state == CHAT_STATE_WAIT_FEED_URL:
        feed = session.query(Feed).get(chat.editing_feed_id)
        url_pattern = re.compile('https?://redmine\.mipt\.ru/.*issues\.atom.+')
        url = message.text.strip()
        if len(url) == 0:
            bot.send_message(message.chat.id, BOT_ADD_ERROR_URL_EMPTY)
            return
        elif url_pattern.match(url) is None:
            bot.send_message(message.chat.id, BOT_ADD_ERROR_URL_FORMAT)
            return
        if session.query(Feed).filter(Feed.chat_id == chat.id, Feed.url == url).first() is not None:
            bot.send_message(message.chat.id, BOT_ADD_ERROR_URL_EMPTY)
            return
        feed.url = url
        chat.state = None
        chat.editing_feed_id = None
        entries = list(feed.fetch_entries().values())
        session.add_all(entries)
        session.flush()
        bot.send_message(message.chat.id, BOT_ADD_SUCCESS % feed.name, parse_mode='Markdown')
    elif chat.state == CHAT_STATE_WAIT_FEED_DELETE:
        name = message.text.strip()
        feed = session.query(Feed).filter(Feed.chat_id == chat.id, Feed.name == name).first()
        session.delete(feed)
        session.flush()
        # TODO add remove of entries
        chat.state = None
        markup = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, BOT_REMOVE_SUCCESS % feed.name, reply_markup=markup, parse_mode='Markdown')
    elif chat.state is not None:
            bot.send_message(message.chat.id, BOT_CHAT_STATE_NOT_EMPTY)
            return
    session.commit()
    session.close()
