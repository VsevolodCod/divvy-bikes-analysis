#!/usr/bin/env python3
"""Тест профайлера данных."""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data.load_data import load_raw_data
from src.data.data_profiler import check_data, quick_check

print("Тестирование DataProfiler\n")

# Загружаем данные
print("Загрузка данных за январь 2024...")
trips = load_raw_data(year=2024, month=1)
print(f"Загружено: {trips.shape[0]:,} поездок\n")

# Полный анализ
check_data(trips, show_samples=True, sample_size=3)

print("\n" + "="*60)
print("Тест завершен успешно!")
print("="*60)
