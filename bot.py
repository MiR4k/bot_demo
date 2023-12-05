from config import *

try:
    cursor = conn.cursor()
    bot = telebot.TeleBot(TOKEN)
except Exception as e:
    print(f"Error during bot initialization: {e}")

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
    except Exception as e:
        print(f"Error during bot initialization: {e}")


@bot.message_handler(content_types='text')
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

def edit_name(message):
    try:
        cursor.execute('UPDATE user SET full_name = ? WHERE tg_id = ?', (message.text, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, 'Успешно!', reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        print(e)



print('bot started')
bot.polling(none_stop=True)
print('bot stropped')