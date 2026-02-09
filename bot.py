import asyncio
import logging
import csv
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Определение состояний для FSM (Обратная связь)
class Form(StatesGroup):
    name = State()
    age = State()


# Определение состояний для Теста
class Test(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()
    Q4 = State()
    Q5 = State()


# Вопросы теста
QUESTIONS = {
    Test.Q1: {
        "question": "Вопрос 1 из 5\n\nКак часто вы занимаетесь физическими упражнениями?",
        "options": ["Ежедневно", "2-3 раза в неделю", "1 раз в неделю", "Реже"]
    },
    Test.Q2: {
        "question": "Вопрос 2 из 5\n\nСколько часов в день вы спите?",
        "options": ["Менее 6 часов", "6-7 часов", "7-8 часов", "Более 8 часов"]
    },
    Test.Q3: {
        "question": "Вопрос 3 из 5\n\nКак часто вы едите fast food?",
        "options": ["Ежедневно", "2-3 раза в неделю", "1 раз в неделю", "Практически никогда"]
    },
    Test.Q4: {
        "question": "Вопрос 4 из 5\n\nВы курите?",
        "options": ["Да, регулярно", "Иногда", "Нет, никогда не курил(а)", "Бросил(а)"]
    },
    Test.Q5: {
        "question": "Вопрос 5 из 5\n\nКак часто вы чувствуете стресс?",
        "options": ["Постоянно", "Часто", "Редко", "Практически никогда"]
    }
}


# Главное меню (Reply Keyboard)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📋 Меню"),
            KeyboardButton(text="ℹ️ О боте")
        ],
        [
            KeyboardButton(text="📝 Обратная связь"),
            KeyboardButton(text="🧪 Начать тестирование")
        ]
    ],
    resize_keyboard=True
)


# Inline клавиатура для меню
inline_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📌 Команда 1", callback_data="cmd1"),
            InlineKeyboardButton(text="📌 Команда 2", callback_data="cmd2")
        ],
        [
            InlineKeyboardButton(text="🔗 Ссылка", url="https://telegram.org")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
        ]
    ]
)


# Inline клавиатура для вопросов теста
def get_test_keyboard(options):
    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([InlineKeyboardButton(text=option, callback_data=f"test_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Функция для сохранения результатов в CSV
def save_to_csv(user_id, username, answers):
    csv_file = "test_results.csv"
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["user_id", "username", "timestamp", "Q1", "Q2", "Q3", "Q4", "Q5"])
        writer.writerow([
            user_id,
            username,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            answers.get("Q1", ""),
            answers.get("Q2", ""),
            answers.get("Q3", ""),
            answers.get("Q4", ""),
            answers.get("Q5", "")
        ])
    logger.info(f"Результат сохранен для user_id: {user_id}")


# Обработчик команды /start
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я Telegram бот с кнопками.\n\nВыберите действие из меню ниже или используйте inline-кнопки:",
        reply_markup=main_menu
    )


# Обработчик команды /help
@dp.message(Command(commands=["help"]))
async def cmd_help(message: types.Message):
    await message.answer(
        "📚 Список доступных команд:\n\n"
        "/start - Запуск бота\n"
        "/help - Помощь\n"
        "/menu - Открыть меню\n\n"
        "Также вы можете использовать кнопки меню."
    )


# Обработчик команды /menu
@dp.message(Command(commands=["menu"]))
async def cmd_menu(message: types.Message):
    await message.answer(
        "📋 Главное меню:",
        reply_markup=inline_menu
    )


# Обработчик кнопки "📋 Меню"
@dp.message(F.text == "📋 Меню")
async def show_menu(message: types.Message):
    await message.answer(
        "📋 Выберите действие:",
        reply_markup=inline_menu
    )


# Обработчик кнопки "ℹ️ О боте"
@dp.message(F.text == "ℹ️ О боте")
async def about_bot(message: types.Message):
    await message.answer(
        "🤖 Это демонстрационный Telegram бот, созданный на aiogram 3.x.\n\n"
        "Функционал:\n"
        "• Команды /start, /help, /menu\n"
        "• Reply-кнопки\n"
        "• Inline-кнопки\n"
        "• FSM состояния\n"
        "• Тестирование с сохранением в CSV"
    )


# Обработчик кнопки "📝 Обратная связь"
@dp.message(F.text == "📝 Обратная связь")
async def feedback(message: types.Message, state: FSMContext):
    await message.answer("📝 Введите ваше имя:")
    await state.set_state(Form.name)


# Обработчик ввода имени (FSM)
@dp.message(StateFilter(Form.name))
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Отлично! Теперь введите ваш возраст:")
    await state.set_state(Form.age)


# Обработчик ввода возраста (FSM)
@dp.message(StateFilter(Form.age))
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    data = await state.get_data()
    await message.answer(
        f"✅ Спасибо!\n\n"
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}\n\n"
        f"Мы свяжемся с вами позже.",
        reply_markup=main_menu
    )
    await state.clear()


# Обработчик кнопки "🧪 Начать тестирование"
@dp.message(F.text == "🧪 Начать тестирование")
async def start_test(message: types.Message, state: FSMContext):
    await message.answer(
        "🧪 Тестирование началось!\n\n"
        "Вам будет предложено 5 вопросов. "
        "Выберите один из вариантов ответа на каждый вопрос.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отмена теста")]],
            resize_keyboard=True
        )
    )
    # Сброс состояния теста
    await state.update_data(test_answers={})
    # Переход к первому вопросу
    await ask_question(message, state, Test.Q1)


# Функция для отправки вопроса
async def ask_question(message: types.Message, state: FSMContext, current_state):
    q_data = QUESTIONS.get(current_state)
    if q_data:
        keyboard = get_test_keyboard(q_data["options"])
        await message.answer(q_data["question"], reply_markup=keyboard)
        await state.set_state(current_state)


# Обработчик ответов на вопросы теста
@dp.callback_query(StateFilter(Test.Q1, Test.Q2, Test.Q3, Test.Q4, Test.Q5))
async def process_test_answer(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    answer = callback.data
    
    # Получаем текст варианта ответа
    if current_state == Test.Q1:
        answer_text = QUESTIONS[Test.Q1]["options"][int(answer.split("_")[1])]
    elif current_state == Test.Q2:
        answer_text = QUESTIONS[Test.Q2]["options"][int(answer.split("_")[1])]
    elif current_state == Test.Q3:
        answer_text = QUESTIONS[Test.Q3]["options"][int(answer.split("_")[1])]
    elif current_state == Test.Q4:
        answer_text = QUESTIONS[Test.Q4]["options"][int(answer.split("_")[1])]
    elif current_state == Test.Q5:
        answer_text = QUESTIONS[Test.Q5]["options"][int(answer.split("_")[1])]
    
    # Сохраняем ответ
    data = await state.get_data()
    answers = data.get("test_answers", {})
    answers[current_state] = answer_text
    await state.update_data(test_answers=answers)
    
    # Переход к следующему вопросу или завершение теста
    if current_state == Test.Q1:
        await ask_question(callback.message, state, Test.Q2)
    elif current_state == Test.Q2:
        await ask_question(callback.message, state, Test.Q3)
    elif current_state == Test.Q3:
        await ask_question(callback.message, state, Test.Q4)
    elif current_state == Test.Q4:
        await ask_question(callback.message, state, Test.Q5)
    elif current_state == Test.Q5:
        # Завершение теста и сохранение результатов
        data = await state.get_data()
        answers = data.get("test_answers", {})
        
        # Сохраняем в CSV
        save_to_csv(
            user_id=callback.from_user.id,
            username=callback.from_user.username or f"user_{callback.from_user.id}",
            answers=answers
        )
        
        await callback.message.edit_text(
            "✅ Тест завершен!\n\n"
            "Ваши ответы сохранены. Спасибо за участие!"
        )
        await callback.message.answer(
            "Вернуться в главное меню:",
            reply_markup=main_menu
        )
        await state.clear()
    
    await callback.answer()


# Обработчик отмены теста
@dp.message(F.text == "❌ Отмена теста")
async def cancel_test(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state in [Test.Q1, Test.Q2, Test.Q3, Test.Q4, Test.Q5]:
        await message.answer(
            "Тест отменен.",
            reply_markup=main_menu
        )
        await state.clear()


# Обработчик inline-кнопок
@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    if callback.data == "cmd1":
        await callback.message.edit_text(
            "📌 Вы выбрали Команду 1!",
            reply_markup=inline_menu
        )
    elif callback.data == "cmd2":
        await callback.message.edit_text(
            "📌 Вы выбрали Команду 2!",
            reply_markup=inline_menu
        )
    elif callback.data == "back":
        await callback.message.edit_text(
            "📋 Главное меню:",
            reply_markup=inline_menu
        )
    await callback.answer()


# Обработчик любых других сообщений
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(
        "Я не понял ваше сообщение.\n"
        "Используйте команды из меню или нажмите /menu",
        reply_markup=main_menu
    )


# Главная функция
async def main():
    logger.info("Запуск бота...")
    # Удаляем webhook, если он установлен
    await bot.delete_webhook()
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
