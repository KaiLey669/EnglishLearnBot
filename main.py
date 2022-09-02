import logging
import re

import telebot
from telebot import types

from config import TOKEN

from db_api import create_tables
from db_api import add_record_in_dict
from db_api import delete_record_from_dict
from db_api import print_dictionary
from db_api import print_new_records
from db_api import print_learned_records
from db_api import change_all_status
from db_api import change_one_status
from db_api import insert_new_user
from db_api import delete_all_records

from logger import init_logger


HELP = """
Это бот, который поможет тебе запомнить английские слова и их перевод.
Принцип работы:
1. Вводишь запись следующего формата: [англ слово] - [перевод на рус];
2. Она сохраняется со статусом "новая", с клавиатуры можно вывести все такие записи, при этом их перевод будет скрыт, чтобы была возможность его вспомнить;
3. После того, как слово выучено, можно отметить его как "выученное" следующей командой /change [англ слово].
После чего оно уже не будет появляться в списке "новых"


Все команды:
/start - запустить бота
/help - справка
/change [англ слово] - изменить статус записи на "выученный"
/del [англ слово]  - удалить запись

Добавление слово
Сообщение вида: [англ слово] - [рус перевод] 
"""


bot = telebot.TeleBot(TOKEN)
init_logger("logger")
logger = logging.getLogger("logger.main")


btn_names = [
    "Вывести все записи",
    "Вывести новые записи",
    "Вывести изученные записи",
    "Изменить статус всех новых записей",
    "Удалить все записи"
]


def create_start_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    print_all_btn = types.KeyboardButton(btn_names[0])
    print_new_btn = types.KeyboardButton(btn_names[1])
    print_old_btn = types.KeyboardButton(btn_names[2])
    change_all_btn = types.KeyboardButton(btn_names[3])
    delete_all_btn = types.KeyboardButton(btn_names[4])
    markup.add(print_all_btn, print_new_btn, print_old_btn, change_all_btn, delete_all_btn)
    return markup


if __name__ == '__main__':

    @bot.message_handler(commands=["start"])
    def start_customization(message):
        logger.info("Enter command '/start'")
        markup = create_start_keyboard()
        create_tables()
        insert_new_user(message.chat.id)
        bot.send_message(message.chat.id, "Бот запущен", reply_markup=markup)


    @bot.message_handler(commands=["help"])
    def print_help(message):
        logger.info("Enter command '/help'")
        bot.send_message(message.chat.id, HELP)


    # Удилить одну запись(/del [english_word])
    @bot.message_handler(commands=["del"])
    def delete_record(message):
        logger.info(f"Enter command '/del' with message {message.text}")
        words = message.text.split(" ", 1)  # Передаем все, что следует после команды
        if len(words) <= 1:
            logger.warning(f"Command '/del' was entered without parameter({words})")
            bot.send_message(message.chat.id, "Для этой команды требуется параметр")
        else:
            mes_api = delete_record_from_dict(message.chat.id, words[1])
            bot.send_message(message.chat.id, mes_api)


    # Изменить статус одной записи на "изучено"(/change [english_word])
    @bot.message_handler(commands=["change"])
    def change_status(message):
        logger.info(f"Enter command '/change' with message {message.text}")
        words = message.text.split(" ", 1)  # Передаем все, что следует после команды
        if len(words) == 1:
            logger.warning(f"Command '/change' was entered without parameter({words})")
            bot.send_message(message.chat.id, "Для этой команды требуется параметр")
        else:
            mes_api = change_one_status(message.chat.id, words[1])
            bot.send_message(message.chat.id, mes_api)


    @bot.message_handler(content_types=["text"])
    def execute_text_commands(message):

        # Вывести все записи
        if message.text == btn_names[0]:
            logger.info(f"Enter message '{message.text}'")
            mes_api = print_dictionary(message.chat.id)
            bot.send_message(message.chat.id, mes_api)

        # Вывести новые записи
        elif message.text == btn_names[1]:
            logger.info(f"Enter message '{message.text}'")
            mes_api = print_new_records(message.chat.id).rstrip("\n")

            if mes_api == "Новые слова отсутствуют":
                bot.send_message(message.chat.id, mes_api)
            else:
                records = mes_api.split("\n")
                for record in records:
                    words = record.split("|")
                    words[1] = re.escape(words[1])
                    bot.send_message(message.chat.id, f"{words[0].strip()} \- ||{words[1].strip()}||",
                                     parse_mode="MarkdownV2")

        # Вывести изученные записи
        elif message.text == btn_names[2]:
            logger.info(f"Enter message '{message.text}'")
            mes_api = print_learned_records(message.chat.id)
            bot.send_message(message.chat.id, mes_api)

        # Изменить статус всех записей на "изученные"
        elif message.text == btn_names[3]:
            logger.info(f"Enter message '{message.text}'")
            mes_api = change_all_status(message.chat.id)
            bot.send_message(message.chat.id, mes_api)

        # Удалить все записи
        elif message.text == btn_names[4]:
            logger.info(f"Enter message '{message.text}'")
            mes_api = delete_all_records(message.chat.id)
            bot.send_message(message.chat.id, mes_api)

        # Добавление записей с проверкой по паттерну
        else:
            logger.info(f"Enter message {message.text}")
            mes_api = add_record_in_dict(message.chat.id, message.text)
            bot.send_message(message.chat.id, mes_api)


    bot.polling(none_stop=True)
