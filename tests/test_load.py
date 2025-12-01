#!/usr/bin/env python3
"""Быстрый тест загрузки данных."""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Тестирование загрузки данных...\n")

try:
    from src.data.load_data import load_raw_data, DataLoader
    print("Импорты успешны")
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    sys.exit(1)

try:
    # Тест 1: Загрузка данных за 2024 год
    print("\nТест 1: Загрузка данных за 2024 год...")
    trips_2024 = load_raw_data(year=2024)
    print(f"Загружено поездок: {trips_2024.shape[0]:,}")
    print(f"Колонок: {trips_2024.shape[1]}")
    print(f"Колонки: {', '.join(trips_2024.columns[:5])}...")
    
except FileNotFoundError as e:
    print(f"Файлы не найдены: {e}")
    print("\nСкачайте данные: ./scripts/download_from_yandex_s3.sh")
    sys.exit(1)
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    # Тест 2: Загрузка диапазона лет
    print("\nТест 2: Загрузка данных за 2023-2024...")
    loader = DataLoader()
    trips_range = loader.load_raw_trips_range(2023, 2024)
    print(f"Загружено поездок: {trips_range.shape[0]:,}")
    
    # Статистика по годам
    import polars as pl
    yearly = trips_range.group_by('year').agg(
        pl.count().alias('trips')
    ).sort('year')
    print("\nРаспределение по годам:")
    for row in yearly.iter_rows(named=True):
        print(f"   {row['year']}: {row['trips']:,} поездок")
    
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nВсе тесты пройдены успешно!")
print("\nТеперь можете использовать в Jupyter:")
print("   from src.data.load_data import load_raw_data")
print("   trips = load_raw_data(year=2024)")
