"""Конфигурация путей проекта."""
from pathlib import Path

# Определяем корень проекта (3 уровня вверх от этого файла)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Основные пути к данным
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
INTERIM_DATA_DIR = DATA_DIR / 'interim'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
EXTERNAL_DATA_DIR = DATA_DIR / 'external'

# Пути к моделям и отчетам
MODELS_DIR = PROJECT_ROOT / 'models'
REPORTS_DIR = PROJECT_ROOT / 'reports'
FIGURES_DIR = REPORTS_DIR / 'figures'

# Конкретные файлы в interim/
TRIPS_CLEANED = INTERIM_DATA_DIR / 'trips_cleaned.parquet'
STATIONS_UNIFIED = INTERIM_DATA_DIR / 'stations_unified.parquet'
TRIPS_WITH_FEATURES = INTERIM_DATA_DIR / 'trips_with_features.parquet'

# Конкретные файлы в processed/
TRIPS_FINAL = PROCESSED_DATA_DIR / 'trips_final.parquet'
DAILY_AGGREGATES = PROCESSED_DATA_DIR / 'daily_aggregates.parquet'
STATION_METRICS = PROCESSED_DATA_DIR / 'station_metrics.parquet'
ROUTE_POPULARITY = PROCESSED_DATA_DIR / 'route_popularity.parquet'
UNIT_ECONOMICS = PROCESSED_DATA_DIR / 'unit_economics.parquet'

# Внешние данные
WEATHER_DIR = EXTERNAL_DATA_DIR / 'weather'
HOLIDAYS_DIR = EXTERNAL_DATA_DIR / 'holidays'
DEMOGRAPHICS_DIR = EXTERNAL_DATA_DIR / 'demographics'

WEATHER_DATA = WEATHER_DIR / 'weather.parquet'
HOLIDAYS_DATA = HOLIDAYS_DIR / 'holidays.parquet'
