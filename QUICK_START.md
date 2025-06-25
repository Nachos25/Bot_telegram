# 🚀 Быстрый запуск TikTok Analyzer Bot

## 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

## 2. Настройка
Создайте файл `.env` со следующим содержимым:
```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
RAPIDAPI_KEY=ваш_ключ_rapidapi
RAPIDAPI_HOST=ваш_хост_rapidapi
```

### Получение токенов:

**Telegram Bot Token:**
1. Напишите [@BotFather](https://t.me/BotFather)
2. Команда: `/newbot`
3. Скопируйте токен в `.env`

**RapidAPI Key и Host:**
1. Регистрация: [rapidapi.com](https://rapidapi.com/)
2. Найдите: "TikTok API" (например, "TikTok API v1" или "TikTok Scraper")
3. Подпишитесь на план
4. В Code Snippets найдите:
   - `X-RapidAPI-Key` → скопируйте в `RAPIDAPI_KEY`
   - `X-RapidAPI-Host` → скопируйте в `RAPIDAPI_HOST`

**Пример из RapidAPI:**
```
X-RapidAPI-Host: tiktok-api23.p.rapidapi.com
X-RapidAPI-Key: ваш_ключ_здесь
```

## 3. Запуск
```bash
python start.py
```

## 4. Использование
В Telegram боте:
- `/start` - главное меню
- `/analyze @username` - анализ фолловеров
- `/settings` - настройки критериев

## 🎯 Результат
Бот создаст Excel файл с микро-инфлюенсерами:
- Никнейм и контакты
- Статистика фолловеров
- Ссылки на профили

---

**Готово! Удачного поиска микро-инфлюенсеров! 🎉** 