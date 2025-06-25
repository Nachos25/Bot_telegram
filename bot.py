import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          CallbackQueryHandler, filters, ContextTypes)
from telegram.constants import ParseMode
from analyzer import TikTokAnalyzer
from config import Config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальный анализатор
analyzer = TikTokAnalyzer()

# Словарь для хранения состояний пользователей
user_states = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
🎯 Добро пожаловать в TikTok Analyzer Bot!

Этот бот поможет вам найти микро-инфлюенсеров в TikTok.

🔥 Что я умею:
• Искать аккаунты по критериям (новое!)
• Анализировать фолловеров конкретного аккаунта
• Находить пользователей с небольшим количеством фолловеров
• Фильтровать по количеству просмотров видео
• Извлекать email адреса из био
• Создавать Excel отчеты

📋 Доступные команды:
/search - поиск новых аккаунтов по критериям (рекомендуется)
/analyze @username - анализ фолловеров аккаунта
/settings - настройки фильтров
/help - справка

🚀 Для начала работы отправьте:
/search - для поиска новых аккаунтов
/analyze @username - для анализа фолловеров
    """
    
    keyboard = [
        [InlineKeyboardButton("🔍 Поиск новых аккаунтов", 
                             callback_data="search")],
        [InlineKeyboardButton("📊 Анализ фолловеров", 
                             callback_data="analyze")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📚 Справка по использованию TikTok Analyzer Bot

🔍 Команды:
• `/start` - запуск бота
• `/search` - поиск новых аккаунтов по критериям (рекомендуется)
• `/analyze @username` - анализ фолловеров аккаунта
• `/settings` - настройки критериев поиска
• `/help` - эта справка

⚙️ Текущие настройки поиска:
• Максимум фолловеров: {max_followers:,}
• Минимум просмотров видео: {min_views:,}
• Минимум подходящих видео: {min_videos}

📊 Формат результата:
Бот создаст Excel файл с данными:
• Никнейм пользователя
• Email (если найден в био)
• Количество фолловеров
• Полная биография
• Ссылка на профиль
• Статистика по видео

⏱️ Время анализа:
Зависит от количества фолловеров. Примерно 1-2 секунды на каждого фолловера.

❗ Важно:
• Используйте точный никнейм без символа @
• Бот анализирует публичные аккаунты
• Максимум 50 фолловеров за раз

💡 Для начала работы отправьте:
/search - для поиска новых аккаунтов
/analyze @username - для анализа фолловеров
    """.format(
        max_followers=analyzer.search_settings['max_followers'],
        min_views=analyzer.search_settings['min_views'],
        min_videos=analyzer.search_settings['min_videos']
    )
    
    await update.message.reply_text(help_text)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /settings"""
    settings_text = analyzer.get_current_settings()
    
    keyboard = [
        [InlineKeyboardButton("👥 Изменить макс. фолловеров", 
                              callback_data="set_followers")],
        [InlineKeyboardButton("👀 Изменить мин. просмотры", 
                              callback_data="set_views")],
        [InlineKeyboardButton("🎬 Изменить мин. видео", 
                              callback_data="set_videos")],
        [InlineKeyboardButton("🔄 Сбросить по умолчанию", 
                              callback_data="reset_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(settings_text, reply_markup=reply_markup)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /search - поиск новых аккаунтов"""
    search_text = """
🔍 Поиск аккаунтов по критериям

Введите поисковый запрос для поиска TikTok аккаунтов.

Примеры запросов:
• `food blogger` - поиск фуд-блогеров
• `fitness` - поиск фитнес аккаунтов  
• `beauty` - поиск бьюти контента
• `travel` - поиск тревел блогеров

⚙️ Текущие критерии фильтра:
• Максимум фолловеров: {max_followers:,}
• Минимум просмотров видео: {min_views:,}
• Минимум подходящих видео: {min_videos}

Отправьте ваш поисковый запрос:
    """.format(
        max_followers=analyzer.search_settings['max_followers'],
        min_views=analyzer.search_settings['min_views'],
        min_videos=analyzer.search_settings['min_videos']
    )
    
    # Устанавливаем состояние пользователя
    user_states[update.effective_user.id] = 'waiting_search_query'
    
    await update.message.reply_text(search_text, parse_mode=ParseMode.MARKDOWN)


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /analyze"""
    if context.args:
        username = ' '.join(context.args)
        await start_analysis(update, username)
    else:
        await update.message.reply_text(
            "❗ Укажите username для анализа.\n\n"
            "Пример: `/analyze food_lover_mike`\n"
            "Или отправьте ссылку на TikTok аккаунт",
            parse_mode=ParseMode.MARKDOWN
        )


async def start_analysis(update: Update, username: str):
    """Запускает анализ аккаунта"""
    progress_message = await update.message.reply_text(
        f"🔄 Начинаем анализ аккаунта @{username}...\n"
        "Это может занять несколько минут."
    )
    
    async def update_progress(text: str):
        try:
            await progress_message.edit_text(text)
        except Exception:
            pass  # Игнорируем ошибки редактирования
    
    try:
        # Запускаем анализ
        result = await analyzer.analyze_account(username, update_progress)
        
        if result['success']:
            # Отправляем сводку результатов
            summary_text = f"""
✅ Анализ завершен!

📊 Статистика:
• Проанализировано фолловеров: {result['total_followers_analyzed']}
• Найдено микро-инфлюенсеров: {result['micro_influencers_found']}

{result['summary']}
            """
            
            await progress_message.edit_text(summary_text)
            
            # Отправляем Excel файл
            if result['excel_file']:
                try:
                    with open(result['excel_file'], 'rb') as file:
                        await update.message.reply_document(
                            document=file,
                            filename=result['excel_file'],
                            caption="📋 Excel файл с результатами."
                        )
                except Exception as e:
                    logger.error(f"Ошибка отправки файла: {e}")
                    await update.message.reply_text(
                        f"❗ Файл создан ({result['excel_file']}), "
                        "но произошла ошибка при отправке."
                    )
        else:
            await progress_message.edit_text(
                f"❌ Ошибка анализа: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Ошибка в анализе: {e}")
        await progress_message.edit_text(
            f"❌ Произошла ошибка при анализе: {str(e)}"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Проверяем состояние пользователя
    if user_id in user_states:
        state = user_states[user_id]
        
        if state == 'waiting_search_query':
            # Пользователь ввел поисковый запрос
            del user_states[user_id]
            await update.message.reply_text(
                "🔍 Поиск по критериям пока не реализован.\n"
                "Используйте команду /analyze для анализа аккаунта.\n\n"
                "Пример: /analyze food_lover_mike"
            )
            return
        
        elif state.startswith('setting_'):
            # Пользователь изменяет настройки
            await handle_setting_input(update, context, state, text)
            return
    
    # Проверяем, является ли сообщение TikTok ссылкой или username
    if 'tiktok.com' in text or text.startswith('@'):
        username = text
        if username.startswith('@'):
            username = username[1:]
        await start_analysis(update, username)
    else:
        await update.message.reply_text(
            "❓ Не понимаю команду.\n\n"
            "Отправьте:\n"
            "• /start - для начала работы\n"
            "• /help - для справки\n"
            "• /analyze @username - для анализа аккаунта\n"
            "• Ссылку на TikTok аккаунт"
        )


async def handle_setting_input(update: Update, 
                               context: ContextTypes.DEFAULT_TYPE, 
                               state: str, text: str):
    """Обработчик ввода настроек"""
    try:
        value = int(text)
        user_id = update.effective_user.id
        
        if state == 'setting_followers':
            analyzer.update_settings(max_followers=value)
            await update.message.reply_text(
                f"✅ Максимум фолловеров обновлен: {value:,}"
            )
        elif state == 'setting_views':
            analyzer.update_settings(min_views=value)
            await update.message.reply_text(
                f"✅ Минимум просмотров обновлен: {value:,}"
            )
        elif state == 'setting_videos':
            analyzer.update_settings(min_videos=value)
            await update.message.reply_text(
                f"✅ Минимум видео обновлено: {value}"
            )
        
        del user_states[user_id]
        
    except ValueError:
        await update.message.reply_text(
            "❗ Введите корректное число."
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "search":
        await search_command(update, context)
    
    elif data == "analyze":
        await query.message.reply_text(
            "📊 Введите username или ссылку на TikTok аккаунт для анализа:\n\n"
            "Примеры:\n"
            "• `food_lover_mike`\n"
            "• `@pet_lover_emma`\n"
            "• `https://www.tiktok.com/@username`",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "settings":
        await settings_command(update, context)
    
    elif data == "set_followers":
        user_states[user_id] = 'setting_followers'
        await query.message.reply_text(
            "👥 Введите максимальное количество фолловеров:"
        )
    
    elif data == "set_views":
        user_states[user_id] = 'setting_views'
        await query.message.reply_text(
            "👀 Введите минимальное количество просмотров для видео:"
        )
    
    elif data == "set_videos":
        user_states[user_id] = 'setting_videos'
        await query.message.reply_text(
            "🎬 Введите минимальное количество видео с высокими просмотрами:"
        )
    
    elif data == "reset_settings":
        analyzer.update_settings(
            max_followers=Config.DEFAULT_MAX_FOLLOWERS,
            min_views=Config.DEFAULT_MIN_VIEWS,
            min_videos=Config.DEFAULT_MIN_VIDEOS
        )
        await query.message.reply_text(
            "🔄 Настройки сброшены к значениям по умолчанию.\n\n" +
            analyzer.get_current_settings()
        )


def main():
    """Запуск бота"""
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
        return
    
    if not Config.RAPIDAPI_KEY:
        logger.error("RAPIDAPI_KEY не найден в переменных окружения!")
        return
    
    # Создаем приложение
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("analyze", analyze_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                   handle_message))
    
    # Запускаем бота
    logger.info("Запускаем TikTok Analyzer Bot...")
    app.run_polling()


if __name__ == '__main__':
    main() 