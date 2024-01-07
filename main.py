from config import *

# Глобальные переменные для хранения информации о товаре
# product_name = ""
prod_name = ""
# price = ""
# description = ""
# photo_data = None  # Здесь можно сохранить данные о фото, если необходимо
user_cart ={}

# Глобальные переменные для отслеживания текущего отображаемого товара
current_product_index = 0
catalog_products = []  # Список товаров из каталога
current_message_id = None  # Идентификатор текущего сообщения с товаром

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_cart[user_id] = []
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_yes = KeyboardButton('Да')
    bnt_edit = KeyboardButton('Редактировать')
    markup.row(btn_yes, bnt_edit)
    try:
        cursor.execute('SELECT Full_name FROM Users WHERE tg_id = ?', (user_id,))
        existing_user = cursor.fetchone()
        existing_user = existing_user[0]
        if existing_user:
            bot.send_message(message.chat.id, f'Добро пожаловать {existing_user}! Вы уже зарегистрированы.', reply_markup=types.ReplyKeyboardRemove())
            main_button(message)

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
        user_type = get_user_type(message)

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


def get_data_from_db():
    try:
        data = cursor.execute('SELECT ProductName FROM Products')
        return data
    except Exception as e:
        print(f"Error from get data {e}")



@bot.message_handler(commands=['zakaz2'])
def handle_start(message):
    
    # Получаем данные из базы данных
    data_from_db = get_data_from_db()
    
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)

    buttons = [telebot.types.InlineKeyboardButton(str(text), callback_data=str(text)) for row in data_from_db for text in row]
    keyboard.add(*buttons)

    keyboard.add(telebot.types.InlineKeyboardButton('На Зад', callback_data='Cancle'))
                 
    bot.send_message(message.chat.id, f"Выберите товар", reply_markup=keyboard)

# Обработчик для инлайн-кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_inline_buttons(call):
    user_id = call.message.chat.id
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
            add_to_cart(prod_name, user_id)
            bot.answer_callback_query(call.message.chat.id, f'Товар добавлен в корзину {prod_name}')
        
        elif call.data == 'Cancle':
                # Обработка нажатия на кнопку 'На Зад'
                bot.answer_callback_query(call.message.chat.id, "Вы нажали 'На Зад'")
        elif call.data:
            start_order(call.message, call.data)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка при обработке инлайн-кнопок: {e}")

def start_order(message, name):
    try:
        global current_product_index, catalog_products, current_message_id
        current_product_index = 0
        current_message_id = None

        # Выполнение SQL-запроса для получения списка товаров из каталога
        cursor.execute('SELECT ProductName, Price, Description, Photo_data, ProductId FROM Products where ProductName = ?',(name,))
        catalog_products = cursor.fetchall()

        # Проверка наличия товаров в каталоге
        if not catalog_products:
            bot.send_message(message.chat.id, 'Каталог пуст.')
            return
        send_product_message(message.chat.id, catalog_products[current_product_index])
        # Отправка сообщения с информацией о первом товаре
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при отображении каталога: {e}")

def send_product_message(chat_id, product):
    try:
        global current_message_id
        product_name, price, description, photo_data, produc_id = product
        message_text = f"**Название:** {product_name}\n**Цена:** {price}\n**Описание:** {description}\nid: {produc_id}"
        # Создание объекта ReplyKeyboardMarkup для создания кнопок
        markup = inline_keyboard()

        # Если есть текущее сообщение, обновим его, иначе отправим новое
        if current_message_id:
            bot.edit_message_media(media=types.InputMediaPhoto(photo_data, caption=message_text, parse_mode='Markdown'),
                                   chat_id=chat_id, message_id=current_message_id, reply_markup=markup)
            
        else:
            msg = bot.send_photo(chat_id, photo_data, caption=message_text, parse_mode='Markdown', reply_markup=markup)
            current_message_id = msg.message_id

    except Exception as e:
        print(chat_id, f"Ошибка при отправке сообщения о товаре: {e}")


def add_to_cart(prod_name, user_id):
    try:
        user_cart[user_id].append(prod_name)
        print(type(user_cart))
        print(user_cart)
    except Exception as e:
        print(e)

print('bot started')
bot.polling(none_stop=True)
print('bot stropped')