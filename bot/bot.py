import telebot
import requests

TOKEN = ''
API_URL = 'http://localhost:5000'
g
bot = telebot.TeleBot(TOKEN)

keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.row('⬅️', '⬆️', '⬇️', '➡️')

# id igroka = chat id
user_id_map = {}

@bot.message_handler(commands=['start', 'join'])
def join_game(message):
    username = message.from_user.username or f'user{message.from_user.id}'
    print(f'Username {username} joined')

    response = requests.post(f'{API_URL}/join', json={'name': username})
    if response.status_code in (200, 201):
        player_id = response.json().get('id')
        user_id_map[message.chat.id] = player_id
        bot.send_message(message.chat.id, f"Привет, {username}! Управляй котом:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Ошибка при подключении к серверру")


@bot.message_handler(func=lambda m: m.text in ['⬆️', '⬇️', '⬅️', '➡️'])
def move(message):
    direction_map = {'⬆️': 'up', '⬇️': 'down', '⬅️': 'left', '➡️': 'right'}
    direction = direction_map[message.text]

    player_id = user_id_map.get(message.chat.id)
    if not player_id:
        bot.send_message(message.chat.id, "Сначала введи /join, чтобы подключиться.")
        return

    res = requests.post(f'{API_URL}/move', json={'id': player_id, 'direction': direction})
    if res.status_code != 200:
        bot.send_message(message.chat.id, "Ошибка. Неверно передано движение")

bot.infinity_polling()
