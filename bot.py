import asyncio
import logging
import json
import os
import csv
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, InputFile
from aiogram.enums import ParseMode
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

# ID админа (ваш Telegram ID)
ADMIN_ID = 101189677

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Загрузка вопросов из JSON файла
def load_questions():
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('questions', [])
    except FileNotFoundError:
        logger.error("Файл questions.json не найден!")
        return []
    except json.JSONDecodeError:
        logger.error("Ошибка чтения questions.json!")
        return []


# Сохранение ответов в CSV
def save_to_csv(user_id, username, answers):
    csv_file = "test_results.csv"
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["user_id", "username", "timestamp", "Q1", "Q2", "Q3"])
        row = [user_id, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        for q_id in range(1, 4):
            row.append(answers.get(str(q_id), ""))
        writer.writerow(row)
    
    logger.info(f"Результат сохранен для user_id: {user_id}")


# Сохранение всех ответов в JSON для админ-панели
def save_all_answers(user_id, username, answers):
    json_file = "all_answers.json"
    data = {}
    
    if os.path.isfile(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    
    if str(user_id) not in data:
        data[str(user_id)] = []
    
    data[str(user_id)].append({
        "username": username,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "answers": answers,
        "admin_response": None
    })
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Определение состояний для Теста
class Test(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()


# Состояния для админа
class Admin(StatesGroup):
    viewing_answers = State()
    waiting_for_response = State()


# Загружаем вопросы
QUESTIONS = load_questions()


# Главное меню (Reply Keyboard)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📋 Меню"),
            KeyboardButton(text="ℹ️ О боте")
        ],
        [
            KeyboardButton(text="🧪 Начать тестирование")
        ]
    ],
    resize_keyboard=True
)


# Админ-меню
admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Все ответы", callback_data="admin_all"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_refresh")
        ]
    ]
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


# Генерация клавиатуры для вопроса
def get_question_keyboard(question_num):
    if not QUESTIONS:
        return None
    
    q = QUESTIONS[question_num - 1]
    if q['type'] == 'choice':
        keyboard = []
        for i, option in enumerate(q.get('options', [])):
            keyboard.append([InlineKeyboardButton(
                text=option, 
                callback_data=f"answer_{question_num}_{i}"
            )])
        keyboard.append([InlineKeyboardButton(
            text="❌ Отмена", 
            callback_data="cancel_test"
        )])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    else:
        # Для текстовых вопросов - только отмена
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text="❌ Отмена", 
                callback_data="cancel_test"
            )]]
        )


# Обработчик команды /start
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я Telegram бот с тестированием.\n\n"
        "Нажмите «🧪 Начать тестирование», чтобы пройти опрос.",
        reply_markup=main_menu
    )


# Обработчик команды /admin
@dp.message(Command(commands=["admin"]))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return
    
    await message.answer(
        "🔧 **Админ-панель**\n\n"
        "Выберите действие:",
        reply_markup=admin_menu,
        parse_mode=ParseMode.MARKDOWN
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
        "🤖 **Telegram Quiz Bot**\n\n"
        "Функционал:\n"
        "• 🧪 Тестирование с вопросами\n"
        "• 💾 Сохранение ответов\n"
        "• 🔧 Админ-панель для просмотра ответов\n\n"
        "Нажмите «🧪 Начать тестирование», чтобы начать!"
    )


# Обработчик кнопки "🧪 Начать тестирование"
@dp.message(F.text == "🧪 Начать тестирование")
async def start_test(message: types.Message, state: FSMContext):
    if not QUESTIONS:
        await message.answer(
            "❌ Вопросы не загружены. Обратитесь к администратору."
        )
        return
    
    await message.answer(
        "🧪 **Тестирование началось!**\n\n"
        f"Всего вопросов: {len(QUESTIONS)}\n"
        "Отвечайте на вопросы.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отмена теста")]],
            resize_keyboard=True
        ),
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Сбрасываем состояние и начинаем с первого вопроса
    await state.update_data(test_answers={})
    await ask_question(message, state, 1)


# Функция для отправки вопроса
async def ask_question(message: types.Message, state: FSMContext, question_num):
    if question_num > len(QUESTIONS):
        # Тест завершен
        data = await state.get_data()
        answers = data.get('test_answers', {})
        
        # Сохраняем ответы
        save_to_csv(
            user_id=message.from_user.id,
            username=message.from_user.username or f"user_{message.from_user.id}",
            answers=answers
        )
        save_all_answers(
            user_id=message.from_user.id,
            username=message.from_user.username or f"user_{message.from_user.id}",
            answers=answers
        )
        
        # Уведомляем админа
        try:
            await bot.send_message(
                ADMIN_ID,
                f"🔔 **Новый ответ на тест!**\n\n"
                f"Пользователь: @{message.from_user.username or message.from_user.id}\n"
                f"ID: {message.from_user.id}\n\n"
                f"📊 Ответы сохранены. Проверьте в админ-панели.",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу: {e}")
        
        await message.answer(
            "✅ **Тест завершен!**\n\n"
            "Спасибо за участие! Ваши ответы сохранены.",
            reply_markup=main_menu,
            parse_mode=ParseMode.MARKDOWN
        )
        await state.clear()
        return
    
    q = QUESTIONS[question_num - 1]
    keyboard = get_question_keyboard(question_num)
    
    # Формируем текст сообщения
    text = f"**Вопрос {question_num} из {len(QUESTIONS)}**\n\n{q['text']}"
    
    # Проверяем наличие картинки
    image_path = q.get('image', '')
    if image_path and os.path.isfile(image_path):
        try:
            await message.answer_photo(
                photo=InputFile(image_path),
                caption=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        except Exception as e:
            logger.error(f"Ошибка отправки картинки: {e}")
    
    await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


# Обработчик ответов на вопросы (выбор)
@dp.callback_query(StateFilter(Test.Q1, Test.Q2, Test.Q3))
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "cancel_test":
        await callback.message.edit_text("Тест отменён.")
        await callback.message.answer(
            "Вернуться в главное меню:",
            reply_markup=main_menu
        )
        await state.clear()
        await callback.answer()
        return
    
    # Парсим ответ: answer_номер_вариант
    parts = callback.data.split('_')
    question_num = int(parts[1])
    answer_num = int(parts[2])
    
    q = QUESTIONS[question_num - 1]
    answer_text = q['options'][answer_num]
    
    data = await state.get_data()
    answers = data.get('test_answers', {})
    answers[str(question_num)] = answer_text
    await state.update_data(test_answers=answers)
    
    await callback.message.edit_text(
        f"✅ Ответ принят: **{answer_text}**"
    )
    
    await ask_question(callback.message, state, question_num + 1)
    await callback.answer()


# Обработчик ТЕКСТОВЫХ ответов на вопросы
@dp.message(StateFilter(Test.Q1, Test.Q2, Test.Q3))
async def process_text_answer(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    # Определяем номер вопроса из состояния
    state_map = {
        Test.Q1: 1,
        Test.Q2: 2,
        Test.Q3: 3
    }
    question_num = state_map.get(current_state)
    
    if not question_num:
        return
    
    # Сохраняем текстовый ответ
    data = await state.get_data()
    answers = data.get('test_answers', {})
    answers[str(question_num)] = message.text
    await state.update_data(test_answers=answers)
    
    await message.answer(f"✅ Ответ принят: **{message.text}**", parse_mode=ParseMode.MARKDOWN)
    
    await ask_question(message, state, question_num + 1)


# Обработчик отмены теста
@dp.message(F.text == "❌ Отмена теста")
async def cancel_test(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state and 'Test:' in str(current_state):
        await message.answer("Тест отменён.", reply_markup=main_menu)
        await state.clear()


# Обработчик админ-кнопок
@dp.callback_query()
async def admin_callback(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ У вас нет доступа!")
        return
    
    if callback.data == "admin_all":
        await show_all_answers(callback.message, callback.from_user.id)
    elif callback.data == "admin_stats":
        await show_stats(callback.message)
    elif callback.data == "admin_refresh":
        await cmd_admin(callback.message)
    
    await callback.answer()


# Показать все ответы
async def show_all_answers(message: types.Message, admin_id):
    try:
        with open('all_answers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        await message.answer("📋 Пока нет ответов.")
        return
    
    if not data:
        await message.answer("📋 Пока нет ответов.")
        return
    
    for user_id, answers_list in data.items():
        latest = answers_list[-1]
        username = latest['username']
        timestamp = latest['timestamp']
        
        text = f"**📋 Ответ пользователя {user_id}**\n\n"
        text += f"**Пользователь:** @{username}\n"
        text += f"**Время:** {timestamp}\n\n"
        
        for q_num, answer in latest['answers'].items():
            text += f"**Вопрос {q_num}:** {answer}\n\n"
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="💬 Ответить",
                    callback_data=f"respond_{user_id}"
                )]
            ]
        )
        
        await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


# Показать статистику
async def show_stats(message: types.Message):
    try:
        with open('all_answers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        await message.answer("📊 Нет данных.")
        return
    
    total_users = len(data)
    answered = sum(1 for answers in data.values() if answers[-1].get('admin_response'))
    
    text = f"**📊 Статистика**\n\n"
    text += f"👥 Всего пользователей: {total_users}\n"
    text += f"💬 Ответов админа: {answered}\n"
    text += f"⏳ Ожидают ответа: {total_users - answered}\n"
    
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)


# Обработчик любых других сообщений
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(
        "Я не понял ваше сообщение.\n"
        "Нажмите «🧪 Начать тестирование» или «/start»"
    )


# Главная функция
async def main():
    logger.info("Запуск бота...")
    logger.info(f"Загружено вопросов: {len(QUESTIONS)}")
    
    try:
        await bot.delete_webhook()
    except Exception as e:
        logger.warning(f"Не удалось удалить webhook: {e}")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
