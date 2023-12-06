import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3

TOKEN = '6668392385:AAEv2_ROZSkJFQjaVp29uEhfFPrG6xN_Bp4'

# Глобальные переменные для хранения информации о товаре
product_name = ""
price = ""
description = ""
photo_data = None  # Здесь можно сохранить данные о фото, если необходимо



try:
    conn = sqlite3.connect('hleb.db', check_same_thread=False)
    cursor = conn.cursor()
    bot = telebot.TeleBot(TOKEN)

except Exception as e:
    print(f"Error during bot initialization: {e}")

def reg(message):
    global full_name
    try:
        if message.text == 'Да':
            cursor.execute('INSERT INTO user (tg_id, full_name, username) VALUES (?, ?, ?)',
                           (message.from_user.id, full_name, message.from_user.username))
            conn.commit()
            bot.send_message(message.chat.id, 'Успешно', reply_markup=types.ReplyKeyboardRemove())

        elif message.text == 'Редактировать':
            bot.send_message(message.chat.id, 'Введите ваше имя бля')
            bot.register_next_step_handler(message,edit_name)
    except Exception as e:
        print(f"Error during bot initialization: {e}")


# Функция для получения названия товара
def get_product_name(message):
    global product_name
    try:
        # Проверка, если пользователь нажал "Отмена"
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Добавление товара отменено.', reply_markup=types.ReplyKeyboardRemove())
            return

        # Сохранение введенного названия товара
        product_name = message.text.strip()

        # Создание объекта ReplyKeyboardMarkup для создания кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_cancel = types.KeyboardButton('Отмена')
        markup.row(btn_cancel)

        # Отправка сообщения с запросом на ввод цены товара
        bot.send_message(message.chat.id, 'Введите цену нового товара:', reply_markup=markup)

        # Регистрация следующего шага обработки текстового сообщения
        bot.register_next_step_handler(message, get_product_price)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении товара: {e}")


# Функция для получения цены товара
def get_product_price(message):
    global price
    try:
        # Проверка, если пользователь нажал "Отмена"
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Добавление товара отменено.', reply_markup=types.ReplyKeyboardRemove())
            return

        # Проверка, что введенное значение является числом
        if not message.text.replace('.', '').isdigit():
            bot.send_message(message.chat.id, 'Пожалуйста, введите корректное число для цены товара.', reply_markup=types.ReplyKeyboardRemove())
            return

        # Сохранение введенной цены товара
        price = message.text.strip()

        # Создание объекта ReplyKeyboardMarkup для создания кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_cancel = types.KeyboardButton('Отмена')
        markup.row(btn_cancel)

        # Отправка сообщения с запросом на ввод описания товара
        bot.send_message(message.chat.id, 'Введите описание нового товара:', reply_markup=markup)

        # Регистрация следующего шага обработки текстового сообщения
        bot.register_next_step_handler(message, get_product_description)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении товара: {e}")

# Функция для получения описания товара
def get_product_description(message):
    global description
    try:
        # Проверка, если пользователь нажал "Отмена"
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Добавление товара отменено.', reply_markup=types.ReplyKeyboardRemove())
            return

        # Сохранение введенного описания товара
        description = message.text.strip()

        # Создание объекта ReplyKeyboardMarkup для создания кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_cancel = types.KeyboardButton('Отмена')
        markup.row(btn_cancel)

        # Отправка сообщения с запросом на ввод фото товара (по желанию пользователя)
        bot.send_message(message.chat.id, 'Хотите добавить фото товара? (Да/Нет)', reply_markup=markup)

        # Регистрация следующего шага обработки текстового сообщения
        bot.register_next_step_handler(message, ask_for_photo)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении товара: {e}")

# Функция для обработки ответа на вопрос о фото товара
def ask_for_photo(message):
    global photo_data
    try:
        # Проверка, если пользователь нажал "Отмена"
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Добавление товара отменено.', reply_markup=types.ReplyKeyboardRemove())
            return

        # Проверка ответа на вопрос о фото товара
        if message.text.lower() == 'да':
            # Здесь можно добавить логику для загрузки и обработки фото
            bot.send_message(message.chat.id, 'Пожалуйста, загрузите фото товара.')

            # Регистрация следующего шага обработки фото
            bot.register_next_step_handler(message, get_product_photo)
        elif message.text.lower() == 'нет':
            # Здесь можно обработать ситуацию, когда фото не требуется
            add_product_to_catalog(message)
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, ответьте "Да" или "Нет".', reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении товара: {e}")

# Функция для получения фото товара
def get_product_photo(message):
    global photo_data
    try:
        # Проверка, если пользователь нажал "Отмена"
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Добавление товара отменено.', reply_markup=types.ReplyKeyboardRemove())
            return

        # Проверка, что сообщение содержит фото
        if message.photo:
            # Получение данных о фото
            photo_data = message.photo[-1].file_id

            # Здесь можно добавить логику для сохранения и обработки данных о фото
            bot.send_message(message.chat.id, 'Фото товара успешно добавлено.')
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, загрузите фото товара.')

        # Добавление товара в каталог
        add_product_to_catalog(message)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении товара: {e}")

# Функция для добавления товара в каталог
def add_product_to_catalog(message):
    global product_name, price, description, photo_data
    try:
        # Выполнение SQL-запроса для добавления товара в базу данных
        cursor.execute('INSERT INTO products (product_name, price, description, photo_data) VALUES (?, ?, ?, ?)',
                       (product_name, price, description, photo_data))
        conn.commit()

        # Очистка глобальных переменных после добавления товара
        product_name = ""
        price = ""
        description = ""
        photo_data = None

        bot.send_message(message.chat.id, 'Товар успешно добавлен в каталог.', reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении товара: {e}")



