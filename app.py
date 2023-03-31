import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN


bot = telebot.TeleBot(TOKEN)

# buttons
conversion_buttons = InlineKeyboardMarkup(row_width=2)
conversion_buttons.row(InlineKeyboardButton('USD/RUB', callback_data='USD_RUB'),
                       InlineKeyboardButton('USD/EUR', callback_data='USD_EUR'),
                       InlineKeyboardButton('USD/TRY', callback_data='USD_TRY'))


# function  user's choice
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.send_message(call.message.chat.id, 'Введите сумму для конвертации:')
    bot.register_next_step_handler(call.message, process_amount, call.data)


def process_amount(message, conversion_rate):
    try:
        amount = float(message.text)
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка пользователя, введите число (сумму для конвертации):')
        return
    # Get  currency from the conversion rate
    from_currency, to_currency = conversion_rate.split('_')
    # Define the URL for the API
    url = f"https://api.apilayer.com/exchangerates_data/convert?from={from_currency}&to={to_currency}&amount={amount}"
    headers = {
        "apikey": "bImHDys29RaiQLYvkEeUnzKHysnhkzKa"
    }

    response = requests.get(url, headers=headers)

    status_code = response.status_code
    result = response.json()

    # Check if the API call was successful
    if status_code != 200 or not result.get('success', False):
        bot.send_message(message.chat.id, 'Ошибка пользователя, попробуйте снова')
        bot.send_message(message.chat.id, 'Выберите валюту для обмена:', reply_markup=conversion_buttons)
        return
    # Get the exchange rate from the API response
    exchange_rate = result.get('result')
    # Send the exchange rate to the user
    bot.send_message(message.chat.id, f'{amount} {from_currency} = {exchange_rate} {to_currency}')
    # Prompt the user to choose another conversion rate
    bot.send_message(message.chat.id, 'Выберите валюту для обмена:', reply_markup=conversion_buttons)


# Define the function for handling incoming messages
@bot.message_handler(commands=['start'])
def start_handler(message):
    # Send the available conversion buttons to the user
    bot.send_message(message.chat.id, 'Выберите валюту для обмена:', reply_markup=conversion_buttons)


# Run the bot
bot.polling()
