import logging
from db_config import connect_to_db

def get_all_products():
    conn = connect_to_db()  # Функция подключения к БД
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT product_id, name, description, price, stock FROM products")
            rows = cursor.fetchall()
            products = [
                {
                    "product_id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "price": float(row[3]),
                    "stock": row[4],
                }
                for row in rows
            ]
            return products
    except Exception as e:
        logging.error(f"Ошибка при получении продуктов: {e}")
        return []
    finally:
        conn.close()
if __name__ == "__main__":
    products = get_all_products()
    if products:
        print("Продукты успешно получены:")
        for product in products:
            print(product)
    else:
        print("Нет доступных продуктов или произошла ошибка.")
