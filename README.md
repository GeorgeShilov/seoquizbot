# Telegram Bot на aiogram 3.x

Демонстрационный Telegram бот с поддержкой кнопок и меню.

## Функционал

- Команды: /start, /help, /menu
- Reply-кнопки (нижнее меню)
- Inline-кнопки
- FSM (Finite State Machine) для последовательного ввода данных

## Установка

1. Клонируйте репозиторий:
```bash
git clone <ваш-репозиторий>
cd telegram_bot
```

2. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка

1. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

2. Добавьте токен вашего бота в `.env`:
```
BOT_TOKEN=ваш_токен_бота
```

## Запуск

```bash
python bot.py
```

## Деплой на Railway

### Предварительные требования

1. Аккаунт на [Railway](https://railway.app)
2. Установленный [Railway CLI](https://docs.railway.app/cli/install) или используйте веб-интерфейс

### Шаги деплоя через веб-интерфейс

1. Загрузите проект на GitHub (без папки `venv` и файла `.env`)

2. Войдите в [Railway](https://railway.app)

3. Нажмите "New Project" → "Deploy from GitHub repo"

4. Выберите ваш репозиторий

5. В разделе "Variables" добавьте переменную:
   - Key: `BOT_TOKEN`
   - Value: `токен_вашего_бота`

6. Нажмите "Deploy"

### Шаги деплоя через CLI

```bash
# Войдите в Railway
railway login

# Инициализируйте проект
railway init

# Установите переменные окружения
railway variables set BOT_TOKEN=ваш_токен_бота

# Задеплоите
railway up
```

### Проверка работы

После деплоя бот автоматически запустится и начнет принимать сообщения.

## Структура проекта

```
telegram_bot/
├── bot.py          # Основной файл бота
├── requirements.txt   # Зависимости
├── Procfile         # Конфигурация для Railway
├── .env.example     # Пример переменных окружения
├── .env             # Переменные окружения (не коммитить!)
├── .gitignore       # Игнорируемые файлы
└── README.md        # Этот файл
```
