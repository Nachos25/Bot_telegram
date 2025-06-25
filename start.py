#!/usr/bin/env python3
"""
Скрипт запуска TikTok Analyzer Bot
"""

import os
import sys
from bot import main

def check_environment():
    """Проверяет наличие необходимых переменных окружения"""
    required_vars = ['TELEGRAM_BOT_TOKEN', 'RAPIDAPI_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Ошибка: Не найдены обязательные переменные окружения:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📋 Инструкции:")
        print("1. Создайте файл .env в корне проекта")
        print("2. Добавьте недостающие переменные:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        print("\n📖 Подробнее в README.md")
        return False
    
    return True

def main_with_checks():
    """Запуск с проверками"""
    print("🚀 Запуск TikTok Analyzer Bot...")
    
    if not check_environment():
        sys.exit(1)
    
    print("✅ Переменные окружения найдены")
    print("🤖 Запуск бота...")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main_with_checks() 