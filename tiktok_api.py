import requests
import re
import logging
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger(__name__)


class TikTokAPI:
    def __init__(self):
        self.headers = {
            "X-RapidAPI-Key": Config.RAPIDAPI_KEY,
            "X-RapidAPI-Host": Config.RAPIDAPI_HOST
        }
    
    def extract_username_from_url(self, url: str) -> Optional[str]:
        """Извлекает username из TikTok URL"""
        patterns = [
            r'tiktok\.com/@([^/?]+)',
            r'tiktok\.com/([^/@][^/?]+)',
            r'vm\.tiktok\.com/([^/?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Получает информацию о пользователе"""
        try:
            url = Config.TIKTOK_USER_INFO_URL
            params = {"uniqueId": username}
            logger.info(f"[TikTokAPI] get_user_info: URL={url}, headers={self.headers}, params={params}")
            response = requests.get(url, headers=self.headers, params=params)
            logger.info(f"[TikTokAPI] get_user_info: status={response.status_code}, text={response.text}")
            response.raise_for_status()
            
            data = response.json()
            if (data.get('statusCode', data.get('status_code', 1)) == 0 and 'userInfo' in data):
                return data['userInfo']
            else:
                logger.error(f"API error for user {username}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user info for {username}: {str(e)}")
            return None
    
    def get_user_followers(self, sec_uid: str, max_count: int = 50, min_cursor: int = 0) -> List[Dict]:
        """Получает список фолловеров пользователя по secUid"""
        try:
            url = f"https://{Config.RAPIDAPI_HOST}/api/user/followers"
            params = {
                "secUid": sec_uid,
                "count": min(max_count, Config.MAX_FOLLOWERS_PER_SEARCH),
                "minCursor": str(min_cursor)
            }
            logger.info(
                f"[TikTokAPI] get_user_followers: URL={url}, headers={self.headers}, params={params}"
            )
            response = requests.get(url, headers=self.headers, params=params)
            logger.info(
                f"[TikTokAPI] get_user_followers: status={response.status_code}, "
                f"text={response.text}"
            )
            response.raise_for_status()
            data = response.json()
            print('DEBUG followers API response:', data)
            logger.info(f'DEBUG followers API response: {data}')
            # В зависимости от структуры ответа API
            if data.get('statusCode', data.get('status_code', 1)) == 0:
                if 'userList' in data:
                    return data['userList']
                if 'followers' in data:
                    return data['followers']
                elif data.get('data') and 'followers' in data['data']:
                    return data['data']['followers']
                elif data.get('data') and isinstance(data['data'], list):
                    return data['data']
                elif data.get('data') and 'users' in data['data']:
                    return data['data']['users']
                else:
                    logger.error(
                        f"Не удалось найти список фолловеров в ответе: {data}"
                    )
                    return []
            else:
                logger.error(
                    f"API error getting followers for secUid {sec_uid}: {data}"
                )
                return []
        except Exception as e:
            logger.error(
                f"Error getting followers for secUid {sec_uid}: {str(e)}"
            )
            return []
    
    def get_user_videos(self, username: str, count: int = 10) -> List[Dict]:
        """Получает список видео пользователя"""
        try:
            url = Config.TIKTOK_USER_VIDEOS_URL
            params = {
                "username": username,
                "count": count
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                return data.get('data', {}).get('videos', [])
            else:
                logger.error(f"API error getting videos for {username}: {data.get('message')}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting videos for {username}: {str(e)}")
            return []
    
    def extract_email_from_bio(self, bio: str) -> Optional[str]:
        """Извлекает email из биографии"""
        if not bio:
            return None
            
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, bio)
        return match.group(0) if match else None
    
    def check_micro_influencer_criteria(self, user_data: Dict, videos: List[Dict], 
                                      max_followers: int = None, 
                                      min_views: int = None, 
                                      min_videos: int = None) -> bool:
        """Проверяет соответствие критериям микро-инфлюенсера"""
        max_followers = max_followers or Config.DEFAULT_MAX_FOLLOWERS
        min_views = min_views or Config.DEFAULT_MIN_VIEWS
        min_videos = min_videos or Config.DEFAULT_MIN_VIDEOS
        
        # Проверяем количество фолловеров
        followers_count = user_data.get('followerCount', 0)
        if followers_count > max_followers:
            return False
        
        # Проверяем количество видео с нужными просмотрами
        valid_videos = 0
        for video in videos:
            view_count = video.get('playCount', 0)
            if view_count >= min_views:
                valid_videos += 1
        
        return valid_videos >= min_videos 