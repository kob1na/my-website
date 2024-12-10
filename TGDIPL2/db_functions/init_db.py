import psycopg2
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Функция для подключения к базе данных
def db_connect():
    try:
        return psycopg2.connect(
            dbname="chatbot_db",
            user="chatbot_user",
            password="qaz2525",
            host="localhost",
            port="5432"
        )
    except psycopg2.Error as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None

# Функция для инициализации базы данных
def init_db():
    conn = db_connect()
    if conn is None:
        logging.error("Не удалось подключиться к базе данных.")
        return

    try:
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE,
                username TEXT[],
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Таблица для отслеживания доставки
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS delivery_tracking (
                delivery_id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
            )
        """)

        # Таблица настроек бота
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_settings (
                id SERIAL PRIMARY KEY,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL
            )
        """)

        # Таблица истории чатов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                chat_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # Таблица для отзывов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # Таблица файлов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                file_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # Таблица логов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                log_id SERIAL PRIMARY KEY,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Таблица программы лояльности
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_program (
                loyalty_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                points INTEGER DEFAULT 0 CHECK (points >= 0),
                level TEXT DEFAULT 'Новичок',
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # Таблица уведомлений
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # Таблица операторов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operators (
                operator_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # Таблица заказов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount > 0),
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # Таблица платежей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL,
                amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
                payment_method TEXT NOT NULL,
                payment_date TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
            )
        """)

        # Таблица товаров
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
                stock INTEGER DEFAULT 0 CHECK (stock >= 0)
            )
        """)

        # Таблица акций
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS promotions (
                promotion_id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL
            )
        """)

        # Таблица напоминаний
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                reminder_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                remind_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # Таблица услуг
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                service_id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price NUMERIC(10, 2) NOT NULL CHECK (price > 0)
            )
        """)

        # Таблица статистики
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                stats_id SERIAL PRIMARY KEY,
                metric_name TEXT NOT NULL,
                value NUMERIC NOT NULL,
                recorded_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Таблица поддерживаемых языков
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supported_languages (
                lang_id SERIAL PRIMARY KEY,
                language_code TEXT NOT NULL UNIQUE,
                language_name TEXT NOT NULL
            )
        """)

        # Таблица опросов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS surveys (
                survey_id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                options TEXT[] NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Таблица предпочтений пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                pref_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        logging.info("База данных успешно инициализирована!")

    except psycopg2.Error as e:
        conn.rollback()
        logging.error(f"Ошибка при создании базы данных: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_db()
