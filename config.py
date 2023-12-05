import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3

conn = sqlite3.connect('hleb.db', check_same_thread=False)

# cursor.execute('''
#         CREATE TABLE IF NOT EXISTS user (
#             id        INTEGER      PRIMARY KEY AUTOINCREMENT
#                                 NOT NULL,
#             tg_id     INTEGER      UNIQUE
#                                 NOT NULL,
#             full_name TEXT         NOT NULL,
#             username  TEXT         UNIQUE,
#             tel_num   TEXT         UNIQUE,
#             state     TEXT (0, 20) NOT NULL
#                                DEFAULT [Не активен]
#     );
#                ''')
TOKEN = '6668392385:AAEv2_ROZSkJFQjaVp29uEhfFPrG6xN_Bp4'


