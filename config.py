import os

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'tiktok-api23.p.rapidapi.com')
    DEFAULT_MAX_FOLLOWERS = int(os.getenv('DEFAULT_MAX_FOLLOWERS', 3000))
    DEFAULT_MIN_VIEWS = int(os.getenv('DEFAULT_MIN_VIEWS', 7000))
    DEFAULT_MIN_VIDEOS = int(os.getenv('DEFAULT_MIN_VIDEOS', 2))
    MAX_FOLLOWERS_PER_SEARCH = int(os.getenv('MAX_FOLLOWERS_PER_SEARCH', 50))
    TIKTOK_USER_INFO_URL = f"https://{RAPIDAPI_HOST}/user/info"
    TIKTOK_USER_FOLLOWERS_URL = f"https://{RAPIDAPI_HOST}/user/followers"
    TIKTOK_USER_VIDEOS_URL = f"https://{RAPIDAPI_HOST}/user/videos"
