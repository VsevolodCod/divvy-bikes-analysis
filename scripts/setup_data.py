#!/usr/bin/env python3
"""
Скрипт для инициализации и проверки структуры данных.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.config.paths import (
    RAW_DATA_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR, EXTERNAL_DATA_DIR,
    WEATHER_DIR, HOLIDAYS_DIR, DEMOGRAPHICS_DIR, MODELS_DIR, REPORTS_DIR, FIGURES_DIR
)


def setup_data_structure():
    """Создать структуру папок если её нет."""
    directories = [
        RAW_DATA_DIR,
        INTERIM_DATA_DIR,
        PROCESSED_DATA_DIR,
        EXTERNAL_DATA_DIR,
        WEATHER_DIR,
        HOLIDAYS_DIR,
        DEMOGRAPHICS_DIR,
        MODELS_DIR,
        REPORTS_DIR,
        FIGURES_DIR,
    ]
    
    print("Настройка структуры данных...\n")
    
    for directory in directories:
        if directory.exists():
            print(f"Существует: {directory.relative_to(PROJECT_ROOT)}")
        else:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Создана: {directory.relative_to(PROJECT_ROOT)}")
    
    print("\nСтруктура данных готова!")


def check_data_availability():
    """Проверить наличие данных."""
    print("\nПроверка наличия данных...\n")
    
    # Проверяем сырые данные
    years = range(2013, 2026)
    available_years = []
    
    for year in years:
        year_dir = RAW_DATA_DIR / str(year)
        if year_dir.exists() and list(year_dir.glob('*.csv')):
            available_years.append(year)
            print(f"Данные за {year} год найдены")
    
    if not available_years:
        print("Сырые данные не найдены")
        print("   Скачайте данные с помощью: ./scripts/download_from_yandex_s3.sh")
    else:
        print(f"\nНайдены данные за {len(available_years)} лет: {min(available_years)}-{max(available_years)}")


if __name__ == "__main__":
    setup_data_structure()
    check_data_availability()
