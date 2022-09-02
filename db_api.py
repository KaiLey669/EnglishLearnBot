import sqlite3
from sqlite3 import Error

import re
import logging

from queries import create_users_table
from queries import create_dictionary_table
from queries import insert_record
from queries import delete_record
from queries import print_all_records
from queries import get_records_by_status
from queries import change_status_all_records
from queries import change_status_one_record
from queries import check_unique_record
from queries import check_record_existence
from queries import insert_user
from queries import check_user_existence
from queries import delete_all


db_path = "dictionary_db.sqlite"
logger = logging.getLogger("logger.db_api")


# Создать соединение с БД
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        logger.info("Connection to SQLite successful")
    except Error as e:
        logger.error(f"The connection error '{e}' occured")

    return connection


# Выполнить запроса к БД
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        logger.info("Query executed successfully")
    except Error as e:
        logger.error(f"The error '{e}' occurred")


# Выполнить запрос на извлечение из БД
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        logger.info("Read query executed successfully")
        return result
    except Error as e:
        logger.error(f"The error '{e}' occurred in read query")


# Создание таблиц
def create_tables():
    connection = create_connection(db_path)
    execute_query(connection, create_users_table)
    execute_query(connection, create_dictionary_table)


# Добавить в БД нового пользователя при первом запуске бота
def insert_new_user(id_tg):
    connection = create_connection(db_path)
    if not execute_read_query(connection, check_user_existence.format(id_tg)):
        execute_query(connection, insert_user.format(id_tg))
        logger.info("[insert_new_user] Command to add new user completed")
    else:
        logger.warning("[insert_new_user] New user has not been added")


# Вывести все записи из словаря
def print_dictionary(id_tg):
    connection = create_connection(db_path)
    records = execute_read_query(connection, print_all_records.format(id_tg))

    if not records:
        logger.info("[print_dictionary] No records in dictionary")
        return "Записей нет"

    message = ""
    for tup in records:
        record = list(tup)
        message += f"{record[0]} - {record[1]}\n"

    logger.info("[print_dictionary] Command to print all records completed")
    return message


# Добавить новую запись в словарь
def add_record_in_dict(id_tg, record):
    connection = create_connection(db_path)
    record = record.lower()

    if len(record) >= 100:
        logger.info(f"[add_record_in_dict] Record to add is to long")
        return "Запись слишком длинная. Максимум 100 символов, включая пробелы и знаки пунктуации"
    if not check_regex_coincidence(record):
        logger.info(f"[add_record_in_dict] Record to add is incorrect '{record}'")
        return "Запись введена неверно(разрешены символы '.', ',', ':', '(', ')', )"
    if not check_unique(connection, id_tg, record):
        logger.info(f"[add_record_in_dict] Record '{record}' is already in dictionary")
        return "Запись уже в словаре"

    record = record.replace('\n', ' ')
    dash_index = record.find("-")  # Поиск первого вхождения тире
    word = record[:dash_index - 1]  # -1 чтобы убрать пробел
    translation = record[dash_index + 2:]  # +2 чтобы убрать пробел

    execute_query(connection, insert_record.format(id_tg, word, translation, 0))
    logger.info("[add_record_in_dict] Command to add record completed")
    return "Запись добавлена"


# Удалить запись из словаря
def delete_record_from_dict(id_tg, word):
    connection = create_connection(db_path)
    word = word.lower()
    records = execute_read_query(connection, check_record_existence.format(id_tg, word))

    if not records:
        logger.info(f"[delete_record_from_dict] Word '{word}' not found in dictionary")
        return "Записи нет в словаре"

    execute_query(connection, delete_record.format(id_tg, word))
    logger.info(f"[delete_record_from_dict] Command to delete record '{word}' completed")

    return "Запись удалена"


# Вывести все "новые" записи
def print_new_records(id_tg):
    connection = create_connection(db_path)
    records = execute_read_query(connection, get_records_by_status.format(id_tg, 0))

    if not records:
        logger.info("[print_new_records] No records in dictionary")
        return "Новые слова отсутствуют"

    message = ""
    for tup in records:
        record = list(tup)
        message += f"{record[0]}|{record[1]}\n"


    logger.info("[print_new_records] Command to print new records completed")
    return message


# Вывести все изученные записи
def print_learned_records(id_tg):
    connection = create_connection(db_path)
    records = execute_read_query(connection, get_records_by_status.format(id_tg, 1))

    if not records:
        logger.info("[print_learned_records] No records in dictionary")
        return "Старые записи отсутствуют"

    message = ""
    for tup in records:
        record = list(tup)
        message += f"{record[0]} -  {record[1]}\n"

    logger.info("[print_learned_records] Command to print learned records completed")
    return message


# Измененить статус записи на "изученный"
def change_one_status(id_tg, word):
    print(word)
    connection = create_connection(db_path)
    records = execute_read_query(connection, check_record_existence.format(id_tg, word))

    if not records:
        logger.info(f"[change_one_status] Word '{word}' not found in dictionary")
        return "Записи нет в словаре"

    execute_query(connection, change_status_one_record.format(id_tg, word))
    logger.info("[change_one_status] Command to change record status completed")
    return "Статус изменен"


# Измененить статус всех записей на "изученный"
def change_all_status(id_tg):
    connection = create_connection(db_path)
    execute_query(connection, change_status_all_records.format(id_tg))

    logger.info("[change_all_status] Command to change all status completed")
    return "Статус всех записей изменен"


# Удалить все записи
def delete_all_records(id_tg):
    connection = create_connection(db_path)
    execute_query(connection, delete_all.format(id_tg))

    logger.info("[delete_all_records] Command to delete all records complete")
    return "Все записи удалены"


# Проверить новую запись по паттерну
def check_regex_coincidence(record):
    regex = "[a-z]+[ ][-][ ][а-я][а-я,.()-: ]+"
    return True if re.match(regex, record) else False


# Проверить уникальность новой записи
def check_unique(connection, id_tg, record):
    word = record[:record.find('-') - 1]
    records = execute_read_query(connection, check_unique_record.format(id_tg, word))

    return True if len(records) == 0 else False
