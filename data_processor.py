import pandas as pd
import openpyxl
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self):
        self.results = []
    
    def add_micro_influencer(self, user_data: Dict, email: str = None):
        """Добавляет микро-инфлюенсера в результаты"""
        result = {
            'Никнейм': user_data.get('uniqueId', ''),
            'Email': email or '',
            'Количество фолловеров': user_data.get('followerCount', 0),
            'Биография': user_data.get('signature', ''),
            'Ссылка на профиль': f"https://www.tiktok.com/@{user_data.get('uniqueId', '')}",
            'Всего видео': user_data.get('videoCount', 0),
            'Видео с высоким просмотром': 0  # Будет обновлено при анализе
        }
        self.results.append(result)
        logger.info(f"Добавлен микро-инфлюенсер: {result['Никнейм']}")
    
    def update_video_stats(self, username: str, high_view_videos: int):
        """Обновляет статистику видео для пользователя"""
        for result in self.results:
            if result['Никнейм'] == username:
                result['Видео с высоким просмотром'] = high_view_videos
                break
    
    def create_excel_file(self, filename: str = None) -> str:
        """Создает Excel файл с результатами"""
        if not self.results:
            logger.warning("Нет данных для создания Excel файла")
            return None
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tiktok_analysis_search_results_{timestamp}.xlsx"
        
        try:
            df = pd.DataFrame(self.results)
            
            # Сортируем по количеству фолловеров (по убыванию)
            df = df.sort_values('Количество фолловеров', ascending=False)
            
            # Создаем Excel файл с форматированием
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Результаты поиска', index=False)
                
                # Получаем workbook и worksheet для форматирования
                workbook = writer.book
                worksheet = writer.sheets['Результаты поиска']
                
                # Автоподбор ширины колонок
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Добавляем заголовок
                worksheet.insert_rows(1)
                worksheet['A1'] = f"Результаты поиска микро-инфлюенсеров TikTok"
                worksheet['A1'].font = openpyxl.styles.Font(size=14, bold=True)
                worksheet.merge_cells('A1:G1')
                
                # Добавляем информацию о поиске
                worksheet.insert_rows(2)
                search_info = f"Дата поиска: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                worksheet['A2'] = search_info
                worksheet.merge_cells('A2:G2')
                
                worksheet.insert_rows(3)  # Пустая строка
            
            logger.info(f"Excel файл создан: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Ошибка при создании Excel файла: {str(e)}")
            return None
    
    def get_results_summary(self) -> str:
        """Возвращает краткую сводку результатов"""
        if not self.results:
            return "❌ Микро-инфлюенсеры не найдены"
        
        total_found = len(self.results)
        with_email = len([r for r in self.results if r['Email']])
        
        summary = f"""
📊 Результаты поиска микро-инфлюенсеров TikTok

✅ Найдено подходящих аккаунтов: {total_found}
📧 Аккаунтов с email: {with_email}
🎯 Процент с контактами: {(with_email/total_found*100):.1f}%

📱 Топ-3 по фолловерам:
"""
        
        # Сортируем и показываем топ-3
        sorted_results = sorted(self.results, 
                              key=lambda x: x['Количество фолловеров'], 
                              reverse=True)[:3]
        
        for i, result in enumerate(sorted_results, 1):
            summary += f"{i}. @{result['Никнейм']} - {result['Количество фолловеров']} фолловеров\n"
        
        return summary.strip()
    
    def clear_results(self):
        """Очищает результаты"""
        self.results = []
        logger.info("Результаты очищены") 