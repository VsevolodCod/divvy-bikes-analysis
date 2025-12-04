#!/usr/bin/env python3
"""Тест визуализации данных."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.data.load_data import load_raw_data  # noqa: E402
from src.visualization import DataExplorer  # noqa: E402


def main() -> None:
    print("🧪 Тестирование визуализации\n")

    # Загружаем данные
    print("Загрузка данных за январь 2024...")
    trips = load_raw_data(year=2024, month=1)
    print(f"✓ Загружено: {trips.shape[0]:,} поездок\n")

    # Создаем исследователь
    explorer = DataExplorer(trips)

    print(f"Числовых колонок: {len(explorer.numeric_cols)}")
    print(f"Категориальных колонок: {len(explorer.categorical_cols)}")
    print(f"Временных колонок: {len(explorer.datetime_cols)}\n")

    # Тест временного ряда
    print("📊 Тест временного ряда...")
    try:
        explorer.plot_time_series('started_at', freq='1d')
        print("✓ Временной ряд (1d) работает!")
    except Exception as e:  # pragma: no cover - визуальные побочные эффекты
        print(f"❌ Ошибка: {e}")

    try:
        explorer.plot_time_series('started_at', freq='1w')
        print("✓ Временной ряд (1w) работает!")
    except Exception as e:  # pragma: no cover
        print(f"❌ Ошибка: {e}")

    print("\n✅ Тесты завершены!")


if __name__ == "__main__":
    main()


