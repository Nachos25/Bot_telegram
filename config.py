import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # RapidAPI - хост можна налаштувати через .env
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'tiktok-api23.p.rapidapi.com')
    
    # Налаштування аналізу за замовчуванням
    DEFAULT_MAX_FOLLOWERS = int(os.getenv('DEFAULT_MAX_FOLLOWERS', 3000))
    DEFAULT_MIN_VIEWS = int(os.getenv('DEFAULT_MIN_VIEWS', 7000))
    DEFAULT_MIN_VIDEOS = int(os.getenv('DEFAULT_MIN_VIDEOS', 2))
    
    # Обмеження
    MAX_FOLLOWERS_PER_SEARCH = int(os.getenv('MAX_FOLLOWERS_PER_SEARCH', 50))
    
    # TikTok API endpoints
    TIKTOK_USER_INFO_URL = f"https://{RAPIDAPI_HOST}/api/user/info"
    TIKTOK_USER_FOLLOWERS_URL = f"https://{RAPIDAPI_HOST}/user/followers"
    TIKTOK_USER_VIDEOS_URL = f"https://{RAPIDAPI_HOST}/user/videos"
