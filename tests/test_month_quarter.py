#!/usr/bin/env python3
"""Тест загрузки данных по месяцам и кварталам."""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data.load_data import load_raw_data, DataLoader

print("Тестирование загрузки по месяцам и кварталам\n")

# Тест 1: Загрузка конкретного месяца
print("Тест 1: Загрузка января 2024")
try:
    trips_jan = load_raw_data(year=2024, month=1)
    print(f"Январь 2024: {trips_jan.shape[0]:,} поездок")
except Exception as e:
    print(f"Ошибка: {e}")

# Тест 2: Загрузка нескольких месяцев
print("\nТест 2: Загрузка нескольких месяцев 2024")
try:
    loader = DataLoader()
    months_data = []
    for month in [1, 2, 3]:
        df = load_raw_data(year=2024, month=month)
        months_data.append((month, df.shape[0]))
        print(f"Месяц {month}: {df.shape[0]:,} поездок")
except Exception as e:
    print(f"Ошибка: {e}")

# Тест 3: Загрузка квартала (старый формат)
print("\nТест 3: Загрузка Q1 2018 (квартальный файл)")
try:
    trips_q1 = load_raw_data(year=2018, quarter=1)
    print(f"Q1 2018: {trips_q1.shape[0]:,} поездок")
except Exception as e:
    print(f"Ошибка: {e}")

# Тест 4: Загрузка квартала через месяцы (новый формат)
print("\nТест 4: Загрузка Q1 2024 (через месяцы)")
try:
    trips_q1_2024 = load_raw_data(year=2024, quarter=1)
    print(f"Q1 2024: {trips_q1_2024.shape[0]:,} поездок")
    print(f"  (Это сумма января, февраля и марта)")
except Exception as e:
    print(f"Ошибка: {e}")

# Тест 5: Загрузка всего года
print("\nТест 5: Загрузка всего 2024 года")
try:
    trips_year = load_raw_data(year=2024)
    print(f"Весь 2024: {trips_year.shape[0]:,} поездок")
    print(f"  (Все 12 месяцев)")
except Exception as e:
    print(f"Ошибка: {e}")

# Тест 6: Сравнение
print("\nТест 6: Проверка что год = сумма месяцев")
try:
    loader = DataLoader()
    
    # Загружаем весь год
    year_total = load_raw_data(year=2024).shape[0]
    
    # Загружаем по месяцам и суммируем
    month_total = 0
    for month in range(1, 13):
        try:
            df = load_raw_data(year=2024, month=month)
            month_total += df.shape[0]
        except:
            pass
    
    print(f"Весь год: {year_total:,} поездок")
    print(f"Сумма месяцев: {month_total:,} поездок")
    print(f"Совпадает: {year_total == month_total}")
except Exception as e:
    print(f"Ошибка: {e}")

print("\nТесты завершены!")
print("\nПримеры использования:")
print("   # Весь год")
print("   trips = load_raw_data(year=2024)")
print()
print("   # Конкретный месяц")
print("   trips_jan = load_raw_data(year=2024, month=1)")
print()
print("   # Квартал")
print("   trips_q1 = load_raw_data(year=2024, quarter=1)")
