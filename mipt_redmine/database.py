from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser


config = ConfigParser()
config.read('./config.ini')


if 'Database' not in config:
    raise IndexError('Не заданы параметры подключения к базе данных')

if 'driver' not in config['Database'] or len(config['Database']['driver'].strip()) == 0:
    raise IndexError('Не задан вид базы данных')
if 'host' not in config['Database'] or len(config['Database']['host'].strip()) == 0:
    raise IndexError('Не задан хост базы данных')
if 'username' not in config['Database'] or len(config['Database']['username'].strip()) == 0:
    raise IndexError('Не задан пользователь базы данных')
if 'password' not in config['Database']:
    raise IndexError('Не задан пароль базы данных')
if 'name' not in config['Database'] or len(config['Database']['name'].strip()) == 0:
    raise IndexError('Не задано имя базы данных')

__url = URL(config['Database']['driver'])
__url.host = config['Database']['host']
__url.username = config['Database']['username']
__url.password = config['Database']['password'] if config['Database']['password'] else None
__url.database = config['Database']['name']

engine = create_engine(str(__url) + '?charset=utf8')

engine_url = str(__url)

Session = sessionmaker(bind=engine)
