import psycopg2
from db_config import connect_to_db

import logging

# Добавление пользователя
def add_user(telegram_id, username=None, phone=None, email=None, address=None):
    conn = connect_to_db()
    if conn is None:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (telegram_id, username, phone, email, address)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (telegram_id) DO NOTHING;
            """, (telegram_id, username, phone, email, address))
            conn.commit()
            logging.info(f"Пользователь с ID {telegram_id} успешно добавлен.")
            return True
    except Exception as e:
        logging.error(f"Ошибка при добавлении пользователя: {e}")
        return False
    finally:
        conn.close()

# Получение пользователя по Telegram ID
def get_user_by_telegram_id(telegram_id):
    conn = connect_to_db()
    if conn is None:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users WHERE telegram_id = %s;
            """, (telegram_id,))
            user = cursor.fetchone()
            if user:
                return {
                    "user_id": user[0],
                    "telegram_id": user[1],
                    "username": user[2],
                    "phone": user[3],
                    "email": user[4],
                    "address": user[5],
                }
            return None
    except Exception as e:
        logging.error(f"Ошибка при получении пользователя: {e}")
        return None
    finally:
        conn.close()

# Обновление данных пользователя
def update_user_data(telegram_id, username=None, phone=None, email=None, address=None):
    conn = connect_to_db()
    if conn is None:
        logging.error("Не удалось подключиться к базе данных.")
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET 
                    username = COALESCE(%s, username),
                    phone = COALESCE(%s, phone),
                    email = COALESCE(%s, email),
                    address = COALESCE(%s, address)
                WHERE telegram_id = %s;
            """, (username, phone, email, address, telegram_id))
            conn.commit()
            logging.info(f"Данные пользователя с ID {telegram_id} успешно обновлены.")
            return True
    except Exception as e:
        logging.error(f"Ошибка при обновлении данных пользователя с ID {telegram_id}: {e}")
        return False
    finally:
        conn.close()
