from config import *

# Глобальные переменные для хранения информации о товаре
product_name = ""
price = ""
description = ""
photo_data = None  # Здесь можно сохранить данные о фото, если необходимо

# Глобальные переменные для отслеживания текущего отображаемого товара
current_product_index = 0
catalog_products = []  # Список товаров из каталога
current_message_id = None  # Идентификатор текущего сообщения с товаром

@bot.message_handler(commands=['start'])
def start(message):
    cid = message.from_user.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_yes = KeyboardButton('Да')
    bnt_edit = KeyboardButton('Редактировать')
    markup.row(btn_yes, bnt_edit)
    try:
        cursor.execute('SELECT Full_name FROM Users WHERE tg_id = ?', (cid,))
        existing_user = cursor.fetchone()
        existing_user = existing_user[0]
        if existing_user:
            bot.send_message(message.chat.id, f'Добро пожаловать {existing_user}! Вы уже зарегистрированы.', reply_markup=types.ReplyKeyboardRemove())
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            btn = KeyboardButton('открыть меню')
            markup.row(btn)
            bot.send_message(cid, 'Нажмите чтобы открыть меню', reply_markup=markup)
            bot.register_next_step_handler(message, create_keyboard)

        else:
            full_name = f"{message.from_user.first_name} {message.from_user.last_name}" \
                if message.from_user.last_name\
                else message.from_user.first_name
            full_name = full_name.replace('None', '')
            bot.send_message(message.chat.id, f'Добро пожаловать {full_name}\nПравильное ли ваше имя для регистрации?', reply_markup=markup)
            bot.register_next_step_handler(message, reg)

    except Exception as e:
        print(f"Error during bot initialization: {e}")

# Функция для обработки команды /add_to_katalog
@bot.message_handler(commands=['add_to_katalog'])
def start_adding_product(message):
    try:
        global product_name, price, description, photo_data, cid
        cid = message.chat.id
        product_name = ""
        price = ""
        description = ""
        photo_data = None
        cursor.execute('SELECT UserType FROM Users WHERE tg_id = ? ', (cid,))
        user_type = cursor.fetchone()
        user_type = user_type[0]

        if user_type == "admin" or user_type == "owner":

            # Создание объекта ReplyKeyboardMarkup для создания кнопок
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_cancel = types.KeyboardButton('Отмена')
            markup.row(btn_cancel)

            # Отправка сообщения с запросом на ввод названия товара
            bot.send_message(cid, 'Введите название нового товара:', reply_markup=markup)

            # Регистрация следующего шага обработки текстового сообщения
            bot.register_next_step_handler(message, get_product_name)
        else:
            bot.send_message(cid, 'У вас нет прав для добавления товара в каталог.')
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении товара: {e}")



# Функция для обработки команды /show_catalog
@bot.message_handler(commands=['show_catalog'])
def start_show_catalog(message):
    try:
        global current_product_index, catalog_products, current_message_id
        current_product_index = 0
        current_message_id = None

        # Выполнение SQL-запроса для получения списка товаров из каталога
        cursor.execute('SELECT ProductName, Price, Description, Photo_data FROM Products')
        catalog_products = cursor.fetchall()

        # Проверка наличия товаров в каталоге
        if not catalog_products:
            bot.send_message(message.chat.id, 'Каталог пуст.')
            return

        # Отправка сообщения с информацией о первом товаре
        send_product_message(message.chat.id, catalog_products[current_product_index])

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при отображении каталога: {e}")


# Обработчик для инлайн-кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_inline_buttons(call):
    try:
        global current_product_index, catalog_products

        # Обработка нажатия на кнопку "Предыдущий"
        if call.data == 'previous_product':
            current_product_index = (current_product_index - 1) % len(catalog_products)
            send_product_message(call.message.chat.id, catalog_products[current_product_index])

        # Обработка нажатия на кнопку "Следующий"
        elif call.data == 'next_product':
            current_product_index = (current_product_index + 1) % len(catalog_products)
            send_product_message(call.message.chat.id, catalog_products[current_product_index])

        # Обработка нажатия на кнопку "Добавить в корзину"
        elif call.data == 'add_to_cart':
            bot.send_message(call.message.chat.id, 'Товар добавлен в корзину')
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка при обработке инлайн-кнопок: {e}")


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


print('bot started')
bot.polling(none_stop=True)
print('bot stropped')