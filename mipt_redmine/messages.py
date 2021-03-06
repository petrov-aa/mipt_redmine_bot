BOT_START = """
Бот для трекера задач redmine.mipt.ru

/help - Список команд

Contact - @AlexanderPetrov
Github - https://git.io/vpC22
"""

BOT_HELP = """
/help - Список команд
/list - Список лент
/add - Добавить новую ленты
/remove - Удалить ленту задач
/cancel - Отмена текущей команды
"""

BOT_ADD = """
Введите имя для новой ленты или нажмите /cancel для отмены
"""

BOT_ADD_URL = """
Введите URL или нажмите /cancel для отмены
"""

BOT_ADD_ERROR_NAME_EMPTY = """
Имя не может быть пустым
"""

BOT_ADD_ERROR_NAME_EXISTS = """
Лента с таким именем уже существует, выберите новое имя
"""

BOT_ADD_ERROR_URL_EMPTY = """
URL не может быть пустым
"""

BOT_ADD_ERROR_URL_FORMAT = """
Можно добавить только ссылку на список задач c сайта redmine.mipt.ru. Попробуйте другую ссылку
"""

BOT_ADD_ERROR_URL_EXISTS = """
Одна из созданных ранее лент уже использует этот URL
"""

BOT_ADD_SUCCESS = """
Лента *"%s"* добавлена. Вы будете получать уведомления при добавлении новых задач в ленту
"""

BOT_CHAT_STATE_NOT_EMPTY = """
Завершите выполнение предыдущей команды или нажмите /cancel для отмены
"""

BOT_CANCEL = """
Отменено
"""

BOT_LIST = """
%s
"""

BOT_LIST_EMPTY = """
Список лент пуст. Для добавление новой ленты нажмите /add
"""

BOT_REMOVE = """
Введите ленту, которую необходимо удалить или нажмите /cancel для отмены
"""

BOT_REMOVE_SUCCESS = """
Лента *"%s"* успешно удалена
"""
