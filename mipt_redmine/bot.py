import re
import telebot
from configparser import ConfigParser

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from mipt_redmine.database import Session
from mipt_redmine.models import Chat, \
    CHAT_STATE_WAIT_FEED_NAME, \
    CHAT_STATE_WAIT_FEED_URL, \
    CHAT_STATE_WAIT_FEED_DELETE, Feed

config = ConfigParser()
config.read('./config.ini')

if 'Bot' not in config:
    raise IndexError('Не заданы параметры бота')
if 'token' not in config['Bot'] or len(config['Bot']['token'].strip()) == 0:
    raise IndexError('Не задан токен бота')

bot = telebot.TeleBot(config['Bot']['token'])


@bot.message_handler(commands=['start'])
def send_welcome(message):
    session = Session()
    chat = session.query(Chat).get(message.chat.id)
    if chat is None:
        chat = Chat()
        chat.id = message.chat.id
        session.add(chat)
        session.commit()
    bot.send_message(message.chat.id, """
Бот для трекера задач redmine.mipt.ru

/help - Список команд

Contact - @AlexanderPetrov
Github - https://git.io/vpC22

""", disable_web_page_preview=True)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, """
/help - Список команд
/list - Список лент задач
/add - Добавить новую ленты
/remove - Удалить ленту задач
/cancel - Отмена текущей команды
""")


@bot.message_handler(commands=['add'])
def send_enter_feed_name(message):
    session = Session()
    chat = session.query(Chat).get(message.chat.id)
    if chat.state is not None:
        bot.send_message(message.chat.id, 'Завершите выполнение предыдущей команды или нажмите /cancel для отмены')
        return
    feed = Feed()
    feed.chat_id = chat.id
    session.add(feed)
    session.flush()
    chat.state = CHAT_STATE_WAIT_FEED_NAME
    chat.editing_feed_id = feed.id
    session.commit()
    bot.send_message(message.chat.id, 'Введите имя для новой ленты или нажмите /cancel для отмены')


@bot.message_handler(commands=['remove'])
def send_remove_feed(message):
    markup = ReplyKeyboardMarkup(row_width=2)
    session = Session()
    chat = session.query(Chat).get(message.chat.id)
    if chat.state is not None:
        bot.send_message(message.chat.id, 'Завершите выполнение предыдущей команды или нажмите /cancel для отмены')
        return
    feeds = chat.feeds
    chat.state = CHAT_STATE_WAIT_FEED_DELETE
    session.commit()
    for feed in feeds:
        markup.add(KeyboardButton(feed.name))
    bot.send_message(message.chat.id, 'Введите имя ленты, которую необходимо удалить или нажмите /cancel для отмены', reply_markup=markup)


@bot.message_handler(commands=['cancel'])
def send_cancel(message):
    session = Session()
    chat = session.query(Chat).get(message.chat.id)
    if chat.editing_feed_id is not None:
        editing_feed = session.query(Feed).get(chat.editing_feed_id)
        session.delete(editing_feed)
    chat.editing_feed_id = None
    chat.state = None
    session.commit()
    bot.send_message(message.chat.id, 'Отменено', reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=['list'])
def send_list(message):
    session = Session()
    chat = session.query(Chat).get(message.chat.id)
    if chat.state is not None:
        bot.send_message(message.chat.id, 'Завершите выполнение предыдущей команды или нажмите /cancel для отмены')
        return
    feeds = chat.feeds
    if len(feeds) != 0:
        items_text = '\n'.join(['%d. %s' % (i+1, feed.name) for i, feed in enumerate(feeds)])
        bot.send_message(message.chat.id, 'Количество: %d\n\n%s' % (len(feeds), items_text))
    else:
        bot.send_message(message.chat.id, 'Список лент пуст. Для добавление новой ленты нажмите /add')


@bot.message_handler()
def send_enter_feed_url(message):
    session = Session()
    chat = session.query(Chat).get(message.chat.id)
    if chat.state == CHAT_STATE_WAIT_FEED_NAME:
        feed = session.query(Feed).get(chat.editing_feed_id)
        name = message.text.strip()
        if len(name) == 0:
            bot.send_message(message.chat.id, 'Имя не может быть пустым')
            return
        if session.query(Feed).filter(Feed.chat_id == chat.id, Feed.name == name).first() is not None:
            bot.send_message(message.chat.id, 'Лента с таким именем уже существует, выберите новое имя')
            return
        feed.name = message.text
        chat.state = CHAT_STATE_WAIT_FEED_URL
        bot.send_message(message.chat.id, 'Введите URL или нажмите /cancel для отмены')
    elif chat.state == CHAT_STATE_WAIT_FEED_URL:
        feed = session.query(Feed).get(chat.editing_feed_id)
        url_pattern = re.compile('https?://redmine\.mipt\.ru/.*issues\.atom.+')
        url = message.text.strip()
        if len(url) == 0:
            bot.send_message(message.chat.id, 'URL не может быть пустым')
            return
        elif url_pattern.match(url) is None:
            bot.send_message(message.chat.id, 'Можно добавить только ссылку на список задач c сайта redmine.mipt.ru. Попробуйте другую ссылку')
            return
        if session.query(Feed).filter(Feed.chat_id == chat.id, Feed.url == url).first() is not None:
            bot.send_message(message.chat.id, 'Одна из созданных ранее лент уже использует этот URL')
            return
        feed.url = url
        chat.state = None
        chat.editing_feed_id = None
        entries = list(feed.fetch_entries().values())
        session.add_all(entries)
        bot.send_message(message.chat.id, 'Лента *"%s"* добавлена. Вы будете получать уведомления при добавлении новых '
                                          'задач в ленту' % feed.name, parse_mode='Markdown')
    elif chat.state == CHAT_STATE_WAIT_FEED_DELETE:
        name = message.text.strip()
        feed = session.query(Feed).filter(Feed.chat_id == chat.id, Feed.name == name).first()
        session.delete(feed)
        # TODO add remove of entries
        chat.state = None
        markup = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Лента *"%s"* успешно удалена' % feed.name, reply_markup=markup, parse_mode='Markdown')
    elif chat.state is not None:
            bot.send_message(message.chat.id, 'Завершите выполнение предыдущей команды или нажмите /cancel для отмены')
            return
    session.commit()
