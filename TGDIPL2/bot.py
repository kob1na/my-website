from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from db_functions.users import add_user, get_user_by_telegram_id, update_user_data
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_functions.products import get_all_products
from aiogram.types import WebAppInfo
from aiogram import F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import phonenumbers
import logging
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
TOKEN = "7820463854:AAH-2DDapeZzrKH-hTXGjzPTUgEvcXgnhcM"
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния для регистрации и обновления данных
class RegistrationStates(StatesGroup):
    name = State()
    phone = State()
    email = State()
    address = State()

class UpdateStates(StatesGroup):
    name = State()
    phone = State()
    email = State()
    address = State()
    confirm = State()

# Клавиатуры
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Регистрация")],
        [KeyboardButton(text="🔄 Обновить данные")],
        [KeyboardButton(text="📦 Посмотреть продукты")],
        [KeyboardButton(text="🛒 Посмотреть корзину")],
    ],
    resize_keyboard=True
)


skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏭️ Пропустить")],
    ],
    resize_keyboard=True
)

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Подтвердить"), KeyboardButton(text="❌ Отменить")],
    ],
    resize_keyboard=True
)

# Команда /start
@dp.message(Command(commands=["start"]))
async def start_handler(message: Message):
    logging.info("Обработка команды /start")
    try:
        telegram_id = message.from_user.id
        username = message.from_user.username

        logging.info(f"ID пользователя: {telegram_id}, username: {username}")
        user = get_user_by_telegram_id(telegram_id)

        if user:
            await message.answer(
                f"👋 Добро пожаловать, {username or 'пользователь'}!\n"
                f"Вы уже зарегистрированы в системе.\n"
                f"Если хотите, вы можете обновить свои данные через меню.",
                reply_markup=main_keyboard
            )
            logging.info(f"Пользователь {telegram_id} уже зарегистрирован.")
        else:
            add_user(telegram_id, username)
            await message.answer(
                f"👋 Добро пожаловать, {username or 'пользователь'}!\n"
                f"Для начала регистрации выберите '📝 Регистрация' в меню.",
                reply_markup=main_keyboard
            )
            logging.info(f"Пользователь {telegram_id} добавлен.")
    except Exception as e:
        logging.error(f"Ошибка в обработчике /start: {e}")

# Регистрация
@dp.message(lambda message: message.text == "📝 Регистрация")
async def start_registration(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    user = get_user_by_telegram_id(telegram_id)

    if user:
        await message.answer(
            "⚠ Вы уже зарегистрированы в системе. Если нужно, вы можете обновить свои данные через меню.",
            reply_markup=main_keyboard
        )
        logging.info(f"Попытка повторной регистрации пользователя {telegram_id}.")
        return

    logging.info("Начало регистрации: Устанавливаю состояние name.")
    await message.answer("👤 Введите ваше имя:")
    await state.set_state(RegistrationStates.name)

@dp.message(RegistrationStates.name)
async def register_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("⚠ Пожалуйста, введите корректное имя.")
        return
    await state.update_data(name=name)
    await message.answer("📱 Введите ваш номер телефона (например: +1234567890):")
    await state.set_state(RegistrationStates.phone)

@dp.message(RegistrationStates.phone)
async def register_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    try:
        parsed_phone = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(parsed_phone):
            raise ValueError("Invalid phone number")
    except:
        await message.answer("⚠ Пожалуйста, введите корректный номер телефона в формате +1234567890.")
        return
    await state.update_data(phone=phone)
    await message.answer("✉️ Введите вашу электронную почту:")
    await state.set_state(RegistrationStates.email)

@dp.message(RegistrationStates.email)
async def register_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if "@" not in email or "." not in email:
        await message.answer("⚠ Пожалуйста, введите корректный адрес электронной почты.")
        return
    await state.update_data(email=email)
    await message.answer("🏠 Укажите ваш адрес доставки (например: Москва, ул. Ленина, д. 1):")
    await state.set_state(RegistrationStates.address)

@dp.message(RegistrationStates.address)
async def register_address(message: types.Message, state: FSMContext):
    address = message.text.strip()
    if "," not in address or len(address.split(",")) < 2:
        await message.answer("⚠ Пожалуйста, укажите город в адресе (например: Москва, ул. Ленина, д. 1).")
        return
    await state.update_data(address=address)
    user_data = await state.get_data()

    try:
        if add_user(
            telegram_id=message.from_user.id,
            username=user_data.get("name"),
            phone=user_data.get("phone"),
            email=user_data.get("email"),
            address=user_data.get("address"),
        ):
            await message.answer("✅ Регистрация завершена! Спасибо!", reply_markup=main_keyboard)
        else:
            await message.answer("⚠ Ошибка при сохранении данных. Попробуйте позже.", reply_markup=main_keyboard)
    except Exception as e:
        logging.error(f"Ошибка при регистрации пользователя: {e}")
        await message.answer("⚠ Произошла ошибка. Попробуйте позже.", reply_markup=main_keyboard)
    finally:
        await state.clear()

# Обновление данных
@dp.message(lambda message: message.text == "🔄 Обновить данные")
async def update_data(message: types.Message, state: FSMContext):
    user = get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("❌ Вы не зарегистрированы. Сначала выполните регистрацию.")
        return
    await message.answer("👤 Введите новое имя (или нажмите «⏭️ Пропустить»):", reply_markup=skip_keyboard)
    await state.set_state(UpdateStates.name)

@dp.message(UpdateStates.name)
async def update_name(message: types.Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        await state.update_data(name=None)
    else:
        await state.update_data(name=message.text.strip())
    await message.answer("📱 Введите новый номер телефона (или нажмите «⏭️ Пропустить»):", reply_markup=skip_keyboard)
    await state.set_state(UpdateStates.phone)

@dp.message(UpdateStates.phone)
async def update_phone(message: types.Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        await state.update_data(phone=None)
    else:
        phone = message.text.strip()
        try:
            parsed_phone = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValueError("Invalid phone number")
            await state.update_data(phone=phone)
        except:
            await message.answer("⚠ Пожалуйста, введите корректный номер телефона в формате +1234567890.")
            return
    await message.answer("✉️ Введите новую электронную почту (или нажмите «⏭️ Пропустить»):", reply_markup=skip_keyboard)
    await state.set_state(UpdateStates.email)

@dp.message(UpdateStates.email)
async def update_email(message: types.Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        await state.update_data(email=None)
    else:
        email = message.text.strip()
        if "@" not in email or "." not in email:
            await message.answer("⚠ Пожалуйста, введите корректный адрес электронной почты.")
            return
        await state.update_data(email=email)
    await message.answer("🏠 Укажите новый адрес доставки (или нажмите «⏭️ Пропустить»):", reply_markup=skip_keyboard)
    await state.set_state(UpdateStates.address)

@dp.message(UpdateStates.address)
async def update_address(message: types.Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        await state.update_data(address=None)
    else:
        address = message.text.strip()
        if "," not in address or len(address.split(",")) < 2:
            await message.answer("⚠ Пожалуйста, укажите город в адресе (например: Москва, ул. Ленина, д. 1).")
            return
        await state.update_data(address=address)
    user_data = await state.get_data()

    await message.answer(
        f"Проверьте ваши изменения:\n"
        f"👤 Имя: {user_data.get('name') or 'Без изменений'}\n"
        f"📱 Телефон: {user_data.get('phone') or 'Без изменений'}\n"
        f"✉️ Почта: {user_data.get('email') or 'Без изменений'}\n"
        f"🏠 Адрес: {user_data.get('address') or 'Без изменений'}\n\n"
        f"Нажмите '✅ Подтвердить', чтобы сохранить изменения, или '❌ Отменить', чтобы отменить обновление.",
        reply_markup=confirm_keyboard
    )
    await state.set_state(UpdateStates.confirm)

@dp.message(UpdateStates.confirm)
async def confirm_update(message: types.Message, state: FSMContext):
    if message.text == "✅ Подтвердить":
        user_data = await state.get_data()
        try:
            success = update_user_data(
                telegram_id=message.from_user.id,
                username=user_data.get("name"),
                phone=user_data.get("phone"),
                email=user_data.get("email"),
                address=user_data.get("address"),
            )
            if success:
                await message.answer("✅ Данные успешно обновлены!", reply_markup=main_keyboard)
            else:
                await message.answer("⚠ Не удалось обновить данные. Попробуйте позже.", reply_markup=main_keyboard)
        except Exception as e:
            logging.error(f"Ошибка при подтверждении обновления данных: {e}")
            await message.answer("⚠ Произошла ошибка. Попробуйте позже.", reply_markup=main_keyboard)
        finally:
            await state.clear()
    elif message.text == "❌ Отменить":
        await message.answer("🚫 Обновление данных отменено.", reply_markup=main_keyboard)
        await state.clear()
    else:
        await message.answer("⚠ Неверный выбор. Пожалуйста, подтвердите или отмените изменения.")

        #Покупка
        # Обработчик кнопки "📦 Посмотреть продукты"
        @dp.message(lambda message: message.text == "📦 Посмотреть продукты")
        async def show_products(message: types.Message):
            web_app_url = "https://mellifluous-chaja-2ed306.netlify.app/"  # Замените на ваш URL
            keyboard = InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="🛒 Открыть каталог", web_app=WebAppInfo(url=web_app_url))
            )
            await message.answer("🛍️ Нажмите на кнопку ниже, чтобы открыть каталог продуктов:", reply_markup=keyboard)

        # Обработчик данных из WebApp
        @dp.message(lambda message: "web_app_data" in message.json)
        async def handle_web_app_data(message: types.Message):
            data = message.web_app_data.data  # Получение данных из WebApp
            await message.answer(f"Корзина успешно получена: {data}")

        # Логирование всех входящих сообщений
        @dp.message()
        async def log_all_messages(message: types.Message):
            logging.info(f"Получено сообщение: {message}")

        # Обработчик для просмотра корзины
        @dp.message(lambda message: message.text == "🛒 Посмотреть корзину")
        async def view_cart(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                cart = data.get("cart", [])
            if not cart:
                await message.answer("🛒 Ваша корзина пуста.")
                return

            # Получение деталей продуктов
            products = get_all_products()
            cart_details = [prod for prod in products if str(prod["product_id"]) in cart]

            if not cart_details:
                await message.answer("🛒 Ваша корзина пуста.")
                return

            text = "🛒 Ваша корзина:\n\n"
            for product in cart_details:
                text += f"🔹 <b>{product['name']}</b>\n"
                text += f"Цена: {product['price']} ₽\n"
                text += f"Описание: {product['description']}\n\n"

            await message.answer(text, parse_mode="HTML")





async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
