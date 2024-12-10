from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from db_functions.users import add_user
import logging

# Состояния для регистрации
class RegistrationStates(StatesGroup):
    name = State()
    phone = State()
    email = State()
    address = State()

# Ввод имени
async def start_registration(message: types.Message):
    await message.answer("Введите ваше имя:")
    await RegistrationStates.name.set()

# Ввод имени
async def enter_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш номер телефона:")
    await RegistrationStates.phone.set()

# Ввод телефона
async def enter_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введите вашу электронную почту:")
    await RegistrationStates.email.set()

# Ввод почты
async def enter_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите ваш адрес доставки:")
    await RegistrationStates.address.set()

# Завершение регистрации
async def enter_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    user_data = await state.get_data()

    # Сохранение данных пользователя в базу
    try:
        if add_user(
            telegram_id=message.from_user.id,
            username=user_data.get("name"),
            phone=user_data.get("phone"),
            email=user_data.get("email"),
            address=user_data.get("address"),
        ):
            await message.answer("Регистрация завершена! Спасибо!")
        else:
            await message.answer("Ошибка при сохранении данных. Попробуйте позже.")
    except Exception as e:
        logging.error(f"Ошибка при регистрации пользователя: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
    finally:
        await state.finish()

# Регистрация хендлеров
def register_handlers_registration(dp):
    dp.register_message_handler(start_registration, text="Регистрация")
    dp.register_message_handler(enter_name, state=RegistrationStates.name)
    dp.register_message_handler(enter_phone, state=RegistrationStates.phone)
    dp.register_message_handler(enter_email, state=RegistrationStates.email)
    dp.register_message_handler(enter_address, state=RegistrationStates.address)
