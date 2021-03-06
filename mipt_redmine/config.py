from configparser import ConfigParser


class ConfigError(Exception):
    pass


config_file = './config.ini'

config = ConfigParser()
config.read(config_file)

if 'Database' not in config:
    raise ConfigError('Не заданы параметры базы данных')
if 'driver' not in config['Database']:
    raise ConfigError('Не задан тип базы данных')
if 'host' not in config['Database']:
    raise ConfigError('Не задан хост базы данных')
if 'user' not in config['Database']:
    raise ConfigError('Не задан пользователь базы данных')
if 'password' not in config['Database']:
    raise ConfigError('Не задан пароль базы данных')
if 'name' not in config['Database']:
    raise ConfigError('Не задано имя базы данных')

database_config = {
    'driver': config['Database']['driver'],
    'host': config['Database']['host'],
    'user': config['Database']['user'],
    'password': config['Database']['password'] if config['Database']['password'] else None,
    'name': config['Database']['name']
}

if 'Bot' not in config:
    raise ConfigError('Не заданы параметры бота')

if 'token' not in config['Bot']:
    raise ConfigError('Не задан API TOKEN')

if 'update_method' not in config['Bot']:
    raise ConfigError('Не задан метод получения сообщений')

if 'use_proxy' not in config['Bot']:
    raise ConfigError('Не задан параметр использования прокси')

bot_config = {
    'token': config['Bot']['token'],
    'use_proxy': config['Bot']['use_proxy'] != 'no',
    'update_method': config['Bot']['update_method'],
    'webhook_host': '',
    'webhook_port': '',
    'socket_path': '',
    'public_cert_path': ''
}

if bot_config['update_method'] == 'webhook':
    if 'webhook_host' not in config['Bot']:
        raise ConfigError('Не задан webhook-хост')
    if 'webhook_port' not in config['Bot']:
        raise ConfigError('Не задан webhook-порт')
    if 'socket_path' not in config['Bot']:
        raise ConfigError('Не задан путь к сокету')
    if 'public_cert_path' not in config['Bot']:
        raise ConfigError('Не задан путь к публичному SSL сертификату')
    bot_config['webhook_host'] = config['Bot']['webhook_host']
    bot_config['webhook_port'] = config['Bot']['webhook_port']
    bot_config['socket_path'] = config['Bot']['socket_path']
    bot_config['public_cert_path'] = config['Bot']['public_cert_path']

proxy_config = {
    'protocol': '',
    'host': '',
    'port': '',
    'user': '',
    'password': '',
}

if bot_config['use_proxy']:
    if 'Proxy' not in config:
        raise ConfigError('Не заданы параметры прокси')
    if 'protocol' not in config['Proxy']:
        raise ConfigError('Не задан протокол прокси')
    if 'host' not in config['Proxy']:
        raise ConfigError('Не задан хост прокси')
    if 'port' not in config['Proxy']:
        raise ConfigError('Не задан порт прокси')
    if 'user' not in config['Proxy']:
        raise ConfigError('Не задан пользователь прокси')
    if 'password' not in config['Proxy']:
        raise ConfigError('Не задан пароль прокси')
    proxy_config = {
        'protocol': config['Proxy']['protocol'],
        'host': config['Proxy']['host'],
        'port': config['Proxy']['port'],
        'user': config['Proxy']['user'],
        'password': config['Proxy']['password'],
    }
