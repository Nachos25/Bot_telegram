import asyncio
import logging
from typing import Dict
from tiktok_api import TikTokAPI
from data_processor import DataProcessor
from config import Config

logger = logging.getLogger(__name__)


class TikTokAnalyzer:
    def __init__(self):
        self.api = TikTokAPI()
        self.processor = DataProcessor()
        self.search_settings = {
            'max_followers': Config.DEFAULT_MAX_FOLLOWERS,
            'min_views': Config.DEFAULT_MIN_VIEWS,
            'min_videos': Config.DEFAULT_MIN_VIDEOS
        }
    
    def update_settings(self, max_followers: int = None,
                        min_views: int = None,
                        min_videos: int = None):
        """Обновляет настройки поиска"""
        if max_followers is not None:
            self.search_settings['max_followers'] = max_followers
        if min_views is not None:
            self.search_settings['min_views'] = min_views
        if min_videos is not None:
            self.search_settings['min_videos'] = min_videos
        
        logger.info(f"Настройки обновлены: {self.search_settings}")
    
    def get_current_settings(self) -> str:
        """Возвращает текущие настройки в читаемом виде"""
        return f"""
🔧 Текущие настройки поиска:

• Максимум фолловеров: {self.search_settings['max_followers']:,}
• Минимум просмотров видео: {self.search_settings['min_views']:,}
• Минимум подходящих видео: {self.search_settings['min_videos']}

Для изменения используйте команду /settings
        """.strip()
    
    async def analyze_account(self, url_or_username: str,
                              progress_callback=None) -> Dict:
        """Анализирует один аккаунт и его фолловеров"""
        # Очищаем предыдущие результаты
        self.processor.clear_results()
        
        # Извлекаем username из URL
        username = self.api.extract_username_from_url(url_or_username)
        if not username:
            username = url_or_username.replace('@', '')
        
        logger.info(f"Начинаем анализ аккаунта: {username}")
        
        # Получаем информацию об аккаунте
        if progress_callback:
            await progress_callback("📋 Получаем информацию об аккаунте...")
        
        user_info = self.api.get_user_info(username)
        if not user_info:
            return {
                'success': False,
                'error': f'Не удалось получить информацию об аккаунте {username}'
            }
        
        # Получаем список фолловеров
        if progress_callback:
            await progress_callback("👥 Получаем список фолловеров...")
        
        followers = self.api.get_user_followers(
            username, 
            Config.MAX_FOLLOWERS_PER_SEARCH
        )
        
        if not followers:
            return {
                'success': False,
                'error': f'Не удалось получить фолловеров для {username}'
            }
        
        logger.info(f"Найдено {len(followers)} фолловеров для анализа")
        
        # Анализируем каждого фолловера
        total_followers = len(followers)
        analyzed_count = 0
        micro_influencers_found = 0
        
        for i, follower in enumerate(followers):
            follower_username = follower.get('uniqueId')
            if not follower_username:
                continue
            
            analyzed_count += 1
            
            if progress_callback:
                progress_text = (
                    f"🔍 Анализируем фолловера {analyzed_count}/{total_followers}\n"
                    f"👤 @{follower_username}\n"
                    f"✅ Найдено микро-инфлюенсеров: {micro_influencers_found}"
                )
                await progress_callback(progress_text)
            
            # Получаем подробную информацию о фолловере
            follower_info = self.api.get_user_info(follower_username)
            if not follower_info:
                continue
            
            # Получаем видео фолловера
            follower_videos = self.api.get_user_videos(follower_username, 20)
            
            # Проверяем критерии микро-инфлюенсера
            is_micro_influencer = self.api.check_micro_influencer_criteria(
                follower_info,
                follower_videos,
                self.search_settings['max_followers'],
                self.search_settings['min_views'],
                self.search_settings['min_videos']
            )
            
            if is_micro_influencer:
                # Извлекаем email из био
                bio = follower_info.get('signature', '')
                email = self.api.extract_email_from_bio(bio)
                
                # Подсчитываем видео с высокими просмотрами
                high_view_videos = sum(
                    1 for video in follower_videos
                    if video.get('playCount', 0) >= self.search_settings['min_views']
                )
                
                # Добавляем в результаты
                self.processor.add_micro_influencer(follower_info, email)
                self.processor.update_video_stats(follower_username, high_view_videos)
                
                micro_influencers_found += 1
                
                logger.info(
                    f"Найден микро-инфлюенсер: @{follower_username} "
                    f"({follower_info.get('followerCount', 0)} фолловеров, "
                    f"{high_view_videos} видео с высокими просмотрами)"
                )
            
            # Небольшая задержка между запросами
            await asyncio.sleep(0.5)
        
        # Создаем Excel файл
        if progress_callback:
            await progress_callback("📊 Создаем Excel файл с результатами...")
        
        excel_file = self.processor.create_excel_file()
        
        return {
            'success': True,
            'total_followers_analyzed': analyzed_count,
            'micro_influencers_found': micro_influencers_found,
            'excel_file': excel_file,
            'summary': self.processor.get_results_summary()
        } 