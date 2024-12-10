from db_config import connect_to_db
import logging

def fetch_all(query, params=None):
    conn = connect_to_db()
    if conn is None:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or [])
            results = cursor.fetchall()
            return results
    except Exception as e:
        logging.error(f"Ошибка при выполнении запроса: {e}")
        return []
    finally:
        conn.close()

def execute_query(query, params=None):
    conn = connect_to_db()
    if conn is None:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or [])
            conn.commit()
            return True
    except Exception as e:
        logging.error(f"Ошибка при выполнении запроса: {e}")
        return False
    finally:
        conn.close()
