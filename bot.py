from config import *


@bot.message_handler(commands=['start'])
def start(message):
    global full_name
    full_name = f"{message.from_user.first_name} {message.from_user.last_name}" \
        if message.from_user.last_name \
        else message.from_user.first_name
    full_name = full_name.replace('None', '')

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_yes = KeyboardButton('Да')
    bnt_edit = KeyboardButton('Редактировать')
    markup.row(btn_yes, bnt_edit)
    try:
        cursor.execute('SELECT full_name FROM user WHERE tg_id = ?', (message.from_user.id,))
        existing_user = cursor.fetchone()
        if existing_user:
            bot.send_message(message.chat.id, f'Добро пожаловать {existing_user[0]}! Вы уже зарегистрированы.', reply_markup=types.ReplyKeyboardRemove())

        else:
            bot.send_message(message.chat.id, f'Добро пожаловать {full_name}\nПравильное ли ваше имя для регистрации?', reply_markup=markup)
            bot.register_next_step_handler(message, reg)

    except Exception as e:
        print(f"Error during bot initialization: {e}")

# Функция для обработки команды /add_to_katalog
@bot.message_handler(commands=['add_to_katalog'])
def start_adding_product(message):
    try:
        global product_name, price, description, photo_data
        product_name = ""
        price = ""
        description = ""
        photo_data = None

        # Создание объекта ReplyKeyboardMarkup для создания кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_cancel = types.KeyboardButton('Отмена')
        markup.row(btn_cancel)

        # Отправка сообщения с запросом на ввод названия товара
        bot.send_message(message.chat.id, 'Введите название нового товара:', reply_markup=markup)

        # Регистрация следующего шага обработки текстового сообщения
        bot.register_next_step_handler(message, get_product_name)
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
        cursor.execute('SELECT product_name, price, description, photo_data FROM products')
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
            # Добавьте здесь логику для добавления товара в корзину
            bot.send_message(call.message.chat.id, 'Товар добавлен в корзину.')

        # Завершение обработки запроса
        bot.answer_callback_query(call.id, text="")

    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка при обработке инлайн-кнопок: {e}")




print('bot started')
bot.polling(none_stop=True)
print('bot stropped')