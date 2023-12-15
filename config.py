import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3

TOKEN = '6668392385:AAEv2_ROZSkJFQjaVp29uEhfFPrG6xN_Bp4'
cid = ""
# Глобальные переменные для хранения информации о товаре
product_name = ""
price = ""
description = ""
photo_data = None  # Здесь можно сохранить данные о фото, если необходимо

# Глобальные переменные для отслеживания текущего отображаемого товара
current_product_index = 0
catalog_products = []  # Список товаров из каталога
current_message_id = None  # Идентификатор текущего сообщения с товаром


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

        elif message.text == 'Редактировать':
            bot.send_message(message.chat.id, 'Введите ваше имя бля')
            bot.register_next_step_handler(message, edit_name)
    except Exception as e:
        print(f"Error during bot initialization: {e}")

def edit_name(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn = KeyboardButton('открыть меню')
    markup.row(btn)
    try:
        cursor.execute('INSERT INTO Users (tg_id, Full_name, Username) VALUES (?, ?, ?)',
                       (message.from_user.id, message.text, message.from_user.username))
        conn.commit()
        bot.send_message(cid, 'Успешно!', reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(cid, 'Нажмите чтобы открыть меню', reply_markup=markup)
        bot.register_next_step_handler(message, create_keyboard)
    except Exception as e:
        print(e)


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
        print(message.chat.id, f"Ошибка при добавлении товара: {e}")


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
        print(message.chat.id, f"Ошибка при добавлении товара: {e}")

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
        print(message.chat.id, f"Ошибка при добавлении товара: {e}")

# Функция для обработки ответа на вопрос о фото товара
def ask_for_photo(message):
    global photo_data
    try:
        # Проверка, если пользователь нажал "Отмена"
        if message.text and message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Добавление товара отменено.', reply_markup=types.ReplyKeyboardRemove())
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


# Функция для отправки сообщения с информацией о товаре
def send_product_message(chat_id, product):
    try:
        global current_message_id
        product_name, price, description, photo_data = product
        message_text = f"**Название:** {product_name}\n**Цена:** {price}\n**Описание:** {description}"

        # Создание объекта ReplyKeyboardMarkup для создания кнопок
        markup = create_inline_keyboard()

        # Если есть текущее сообщение, обновим его, иначе отправим новое
        if current_message_id:
            bot.edit_message_media(media=types.InputMediaPhoto(photo_data, caption=message_text, parse_mode='Markdown'),
                                   chat_id=chat_id, message_id=current_message_id, reply_markup=markup)
        else:
            msg = bot.send_photo(chat_id, photo_data, caption=message_text, parse_mode='Markdown', reply_markup=markup)
            current_message_id = msg.message_id

    except Exception as e:
        print(chat_id, f"Ошибка при отправке сообщения о товаре: {e}")

# Не нужный код
# def get_user_type(message):
#     try:
#         cursor.execute('SELECT UserType FROM Users WHERE tg_id = ? ', message.from_user.id)
#         user_type = cursor.fetchone()
#         return user_type[0]
#     except Exception as e:
#         print(message.chat.id, f"Ошибка при отправке сообщения о товаре: {e}")

def create_keyboard(message):
    global user_type
    global cid
    cid = message.chat.id
    try:
        cursor.execute('SELECT UserType FROM Users WHERE tg_id = ? ', (cid,))
        user_type = cursor.fetchone()
    except Exception as e:
        print(message.chat.id, f"Ошибка при отправке сообщения о товаре: {e}")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    user_type = user_type[0]
    if user_type == 'User':
        # print(user_type)
        keyboard.row('🛒 Заказать', '📋 История заказов')
        keyboard.row('🔄 Статус текущего заказа')
        bot.register_next_step_handler(message, order)

    elif user_type == 'company_rep':
        keyboard.row('📊 Статус заказов', '💰 Баланс и предоплата')
        keyboard.row('📝 Шаблоны заказов', '🔐 Изменить данные профиля')

    elif user_type == 'courier':
        keyboard.row('🚚 Информация о заказах', '📞 Контакты заказчиков')
        keyboard.row('💵 Оплата и счет-фактура', '✅ Подтвердить доставку')

    elif user_type == 'admin':
        keyboard.row('🕵️‍♂️ Мониторинг курьеров', '📈 Статистика и анализ')
        keyboard.row('🔄 Подтвердить заказы', '🔒 Изменить статус пользователя')

    elif user_type == 'owner':
        keyboard.row('🔄 Управление пользователями', '📊 Полная статистика')
        keyboard.row('🔐 Назначение администраторов', '⚙️ Дополнительные настройки')
    bot.send_message(message.chat.id,'Меню открыто ', reply_markup=keyboard)

def order(message):
    global cid





# Функция для создания инлайн-клавиатуры
def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_previous = types.InlineKeyboardButton('Предыдущий', callback_data='previous_product')
    btn_next = types.InlineKeyboardButton('Следующий', callback_data='next_product')
    btn_add_to_cart = types.InlineKeyboardButton('Добавить в корзину', callback_data='add_to_cart')
    markup.add(btn_previous, btn_add_to_cart, btn_next)
    return markup

def send_error_message(chat_id, error_message):
    print(chat_id, f"Ошибка: {error_message}")

