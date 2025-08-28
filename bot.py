import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота (замените на ваш токен)
BOT_TOKEN = "8407984620:AAGFjSxDdrEoq_-vq_UllVloTVKZxF3NVTY"

# ID администраторов
ADMIN_IDS = [982741411, 811152431, 1678290901]

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния для FSM
class OrderForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_telegram = State()

# Функция для создания главного меню
def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="📝 Оформить заявку на предзаказ",
        callback_data="order"
    ))
    builder.add(InlineKeyboardButton(
        text="❓ Задать вопрос",
        url="https://t.me/ylnaaaw"
    ))
    builder.adjust(1)
    return builder.as_markup()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in ADMIN_IDS:
        await message.answer(
            "👋 Добро пожаловать, администратор!\n\n"
            "Вы можете управлять ботом и получать уведомления о новых заявках."
        )
    else:
        welcome_text = (
            "🎓 <b>Добро пожаловать в AnyWay!</b>\n\n"
            "AnyWay - это образовательная платформа для школьников, которая поможет вам:\n\n"
            "📚 <b>Выбрать олимпиады и конкурсы</b> для поступления в вуз мечты\n"
            "📅 <b>Планировать подготовку</b> с персональным календарем дедлайнов\n"
            "👥 <b>Найти напарника</b> для совместной учебы\n"
            "💬 <b>Присоединиться к сообществу</b> олимпиадников\n"
            "🧠 <b>Сохранить ментальное здоровье</b> в процессе поступления\n\n"
            "💰 <b>Стоимость подписки:</b> 399р/месяц. но по предзаказу для Вас скидка 40%, что дает право пользоваться сервисом всего за 240 рублей! \n\n"
            "Проект разрабатывается в рамках Стартап Академии Сколково.\n"
            "Оформите предзаказ и получите доступ к платформе одними из первых!"
        )
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )

# Обработчик нажатия на кнопку "Оформить заявку"
@dp.callback_query(F.data == "order")
async def process_order_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📝 <b>Оформление заявки на предзаказ</b>\n\n"
        "Для оформления заявки нам потребуется несколько данных.\n"
        "Пожалуйста, введите ваше <b>имя</b>:",
        parse_mode="HTML"
    )
    await state.set_state(OrderForm.waiting_for_name)
    await callback.answer()

# Обработчик ввода имени
@dp.message(StateFilter(OrderForm.waiting_for_name))
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "📱 Отлично! Теперь введите ваш <b>номер телефона</b>:\n"
        "(в формате +7XXXXXXXXXX)",
        parse_mode="HTML"
    )
    await state.set_state(OrderForm.waiting_for_phone)

# Обработчик ввода телефона
@dp.message(StateFilter(OrderForm.waiting_for_phone))
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(
        "💬 Последний шаг! Введите ваш <b>аккаунт в Telegram</b>:\n"
        "(например: @username или просто username)",
        parse_mode="HTML"
    )
    await state.set_state(OrderForm.waiting_for_telegram)

# Обработчик ввода Telegram аккаунта
@dp.message(StateFilter(OrderForm.waiting_for_telegram))
async def process_telegram(message: types.Message, state: FSMContext):
    await state.update_data(telegram=message.text)
    
    # Получаем все данные
    data = await state.get_data()
    user = message.from_user
    
    # Формируем сообщение для администраторов
    admin_message = (
        "🆕 <b>Новая заявка на регистрацию</b>\n\n"
        f"👤 <b>Имя:</b> {data['name']}\n"
        f"📱 <b>Телефон:</b> {data['phone']}\n"
        f"💬 <b>Telegram:</b> {data['telegram']}\n\n"
        f"📊 <b>Данные пользователя:</b>\n"
        f"🆔 ID: {user.id}\n"
        f"👤 Username: @{user.username if user.username else 'не указан'}\n"
        f"📝 Полное имя: {user.full_name}\n\n"
        f"💰 <b>Стоимость:</b> 240р/месяц"
    )
    
    # Отправляем уведомления всем администраторам
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_message, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение администратору {admin_id}: {e}")
    
    # Подтверждение пользователю
    await message.answer(
        "✅ <b>Заявка успешно отправлена!</b>\n\n"
        "Спасибо за интерес к проекту AnyWay! 🎓\n"
        "Наши администраторы свяжутся с вами в ближайшее время.\n\n"
        "Следите за обновлениями - скоро запустим платформу!",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )
    
    # Очищаем состояние
    await state.clear()

# Обработчик для отмены (если пользователь отправит /cancel)
@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных операций для отмены.")
        return
    
    await state.clear()
    await message.answer(
        "❌ Оформление заявки отменено.\n"
        "Вы можете начать заново в любое время!",
        reply_markup=get_main_menu()
    )

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "🤖 <b>Помощь по боту AnyWay</b>\n\n"
        "📝 <b>Доступные команды:</b>\n"
        "/start - Главное меню\n"
        "/help - Эта справка\n"
        "/cancel - Отменить текущую операцию\n\n"
        "❓ <b>Нужна помощь?</b>\n"
        "Обратитесь к нашему администратору: @ylnaaaw"
    )
    await message.answer(help_text, parse_mode="HTML")

# Основная функция запуска бота
async def main():
    print("🤖 Бот AnyWay запущен!")
    print(f"📊 Администраторы: {ADMIN_IDS}")
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
