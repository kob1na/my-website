

import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Функция для подключения к базе данных
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="chatbot_db",  # Замените на имя вашей базы данных
            user="chatbot_user",        # Ваше имя пользователя PostgreSQL
            password="qaz2525",    # Ваш пароль PostgreSQL
            host="localhost",            # Хост (обычно localhost)
            port="5432"                  # Порт PostgreSQL
        )
        return conn
    except psycopg2.Error as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None

