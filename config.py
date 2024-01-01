import sqlite3

import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
# from main import*
TOKEN = '6668392385:AAEv2_ROZSkJFQjaVp29uEhfFPrG6xN_Bp4'
   # Словарь с кнопками для каждого типа пользователя
buttons_dict = {
        'user': [
            ['🛒 Заказать', '📋 История заказов'],
            ['🔄 Статус текущего заказа']
        ],
        'company_rep': [
            ['📊 Статус заказов', '💰 Баланс и предоплата'],
            ['📝 Шаблоны заказов', '🔐 Изменить данные профиля']
        ],
        'courier': [
            ['🚚 Информация о заказах', '📞 Контакты заказчиков'],
            ['💵 Оплата и счет-фактура', '✅ Подтвердить доставку']
        ],
        'admin': [
            ['🕵️‍♂️ Мониторинг курьеров', '📈 Статистика и анализ'],
            ['🔄 Подтвердить заказы', '🔒 Изменить статус пользователя']
        ],
        'owner': [
            ['🔄 Управление пользователями', '📊 Полная статистика'],
            ['🔐 Назначение администраторов', '⚙️ Дополнительные настройки']
        ]
    }

    


try:
    conn = sqlite3.connect('hleb.db', check_same_thread=False)
    cursor = conn.cursor()
    bot = telebot.TeleBot(TOKEN)

except Exception as e:
    print(f"Error during bot initialization: {e}")

def reg(message):
    global cid
    global full_name
    cid = message.chat.id

    full_name = f"{message.from_user.first_name} {message.from_user.last_name}" \
        if message.from_user.last_name \
        else message.from_user.first_name
    full_name = full_name.replace('None', '')
    try:
        if message.text == 'Да':
            cursor.execute('INSERT INTO Users (tg_id, Full_name, Username) VALUES (?, ?, ?)',
                           (message.from_user.id, full_name, message.from_user.username))
            conn.commit()
            bot.send_message(message.chat.id, 'Успешно', reply_markup=types.ReplyKeyboardRemove())
            main_button()

        elif message.text == 'Редактировать':
            bot.send_message(message.chat.id, 'Введите ваше имя бля')
            bot.register_next_step_handler(message, edit_name)
    except Exception as e:
        print(f"Error during bot initialization: {e}")

def edit_name(message):
    try:
        cursor.execute('INSERT INTO Users (tg_id, Full_name, Username) VALUES (?, ?, ?)',
                       (message.from_user.id, message.text, message.from_user.username))
        conn.commit()
        bot.send_message(cid, 'Успешно!', reply_markup=types.ReplyKeyboardRemove())
        main_button()
    except Exception as e:
        print(e)


# Функция для получения названия товара
def get_product_name(message):
    global product_name
    try:
        # Проверка, если пользователь нажал "Отмена"
        if message.text.lower() == 'отмена':
            add_catalog_cancel(message)
            return


        # Сохранение введенного названия товара
        product_name = message.text.strip()

        # Создание объекта ReplyKeyboardMarkup для создания кнопок
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_cancel = types.KeyboardButton('Отмена')
        keyboard.row(btn_cancel)

        # Отправка сообщения с запросом на ввод цены товара
        bot.send_message(message.chat.id, 'Введите цену нового товара:', reply_markup=keyboard)

        # Регистрация следующего шага обработки текстового сообщения
        bot.register_next_step_handler(message, get_product_price)
    except Exception as e:
        print(message.chat.id, f"Ошибка при добавлении товара: {e}")



# Функция для получения цены товара
def get_product_price(message):
    global price
    try:
        # Проверка, если пользователь нажал "Отмена"
        if message.text.lower() == 'отмена':
            add_catalog_cancel(message)
            return

        # Проверка, что введенное значение является числом
        if not message.text.replace('.', '').isdigit():
            bot.send_message(message.chat.id, 'Пожалуйста, введите корректное число для цены товара.', reply_markup=types.ReplyKeyboardRemove())
            return

        # Сохранение введенной цены товара
        price = message.text.strip()

        # Создание объекта ReplyKeyboardMarkup для создания кнопок
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_cancel = types.KeyboardButton('Отмена')
        keyboard.row(btn_cancel)

        # Отправка сообщения с запросом на ввод описания товара
        bot.send_message(message.chat.id, 'Введите описание нового товара:', reply_markup=keyboard)

        # Регистрация следующего шага обработки текстового сообщения
        bot.register_next_step_handler(message, get_product_description)
    except Exception as e:
        print(message.chat.id, f"Ошибка при добавлении товара: {e}")

# Функция для получения описания товара
def get_product_description(message):
    global description
    try:
        # Проверка, если пользователь нажал "Отмена"
        if message.text.lower() == 'отмена':
            add_catalog_cancel(message)
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
        print(message.chat.id, f"Ошибка при добавлении товара: {e}")

# Функция для обработки ответа на вопрос о фото товара
def ask_for_photo(message):
    global photo_data
    try:
        # Проверка, если пользователь нажал "Отмена"
        if message.text and message.text.lower() == 'отмена':
            add_catalog_cancel(message)
            return

        # Проверка ответа на вопрос о фото товара
        if message.text and message.text.lower() == 'да':
            # Здесь можно добавить логику для загрузки и обработки фото
            bot.send_message(message.chat.id, 'Пожалуйста, загрузите фото товара.')

            # Регистрация следующего шага обработки фото
            bot.register_next_step_handler(message, get_product_photo)
        elif message.text and message.text.lower() == 'нет':
            # Здесь можно обработать ситуацию, когда фото не требуется
            add_product_to_catalog(message)
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, ответьте "Да" или "Нет".', reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        print(message.chat.id, f"Ошибка при добавлении товара: {e}")

# Функция для получения фото товара
def get_product_photo(message):
    global photo_data
    try:
        # Проверка, если пользователь нажал "Отмена"
        if message.text and message.text.lower() == 'отмена':
            add_catalog_cancel(message)
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
        print(e)

# Функция для добавления товара в каталог
def add_product_to_catalog(message):
    global product_name, price, description, photo_data
    try:
        # Выполнение SQL-запроса для добавления товара в базу данных
        cursor.execute('INSERT INTO Products (ProductName, Price, Description, Photo_data) VALUES (?, ?, ?, ?)',
                       (product_name, price, description, photo_data))
        conn.commit()

        # Очистка глобальных переменных после добавления товара
        product_name = ""
        price = ""
        description = ""
        photo_data = None

        bot.send_message(message.chat.id, 'Товар успешно добавлен в каталог.', reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        print(f"Ошибка при добавлении товара: {e} В чате {message.chat.id}")


def add_catalog_cancel(message):
    bot.send_message(message.chat.id, 'Добавление товара отменено.', main_button(message))


def main_button(message):
    global cid
    cid = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    try:
        user_type = get_user_type(message)
    except Exception as e:
        print(message.chat.id, f"Ошибка при отправке сообщения о товаре: {e}")

 # Создание кнопок на основе словаря для определенного типа пользователя
    button_text = buttons_dict.get(user_type, [])
    for row in button_text:
        keyboard.row(*row)
    if message.text == "/start":
        bot.send_message(message.chat.id,'Меню открыто ', reply_markup=keyboard)
    bot.register_next_step_handler(message, handler_main_button)


def handler_main_button(message):
    
    if message.text == '🛒 Заказать':
        bot.send_message(message.chat.id, 'ti pidor')



# Функция для создания инлайн-клавиатуры
def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_previous = types.InlineKeyboardButton('Предыдущий', callback_data='previous_product')
    btn_next = types.InlineKeyboardButton('Следующий', callback_data='next_product')
    btn_add_to_cart = types.InlineKeyboardButton('Добавить в корзину', callback_data='add_to_cart')
    markup.add(btn_previous, btn_add_to_cart, btn_next)
    return markup

def get_user_type(message):
    try:
        cursor.execute('SELECT UserType FROM Users WHERE tg_id = ? ', (message.chat.id,))
        user_type = cursor.fetchone()
        user_type = user_type[0]
        return user_type
    except Exception as e:
        print(f"Ошибка при получении типа пользователя: {e}")




