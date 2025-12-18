"""Создание временных признаков для анализа велопроката."""

import polars as pl
from typing import List, Optional
from datetime import datetime, date
import numpy as np


class TemporalFeatureExtractor:
    """Класс для создания временных признаков."""
    
    def __init__(self):
        """Инициализация с настройками."""
        # Определяем пиковые часы
        self.morning_peak = (7, 9)  # 7:00-9:00
        self.evening_peak = (16, 18)  # 16:00-18:00
        
        # Праздники США (основные)
        self.holidays = [
            # 2020
            date(2020, 1, 1), date(2020, 7, 4), date(2020, 11, 26), date(2020, 12, 25),
            # 2021
            date(2021, 1, 1), date(2021, 7, 4), date(2021, 11, 25), date(2021, 12, 25),
            # 2022
            date(2022, 1, 1), date(2022, 7, 4), date(2022, 11, 24), date(2022, 12, 25),
            # 2023
            date(2023, 1, 1), date(2023, 7, 4), date(2023, 11, 23), date(2023, 12, 25),
            # 2024
            date(2024, 1, 1), date(2024, 7, 4), date(2024, 11, 28), date(2024, 12, 25),
            # 2025
            date(2025, 1, 1), date(2025, 7, 4), date(2025, 11, 27), date(2025, 12, 25),
        ]
    
    def extract_time_features(self, df: pl.DataFrame, 
                             datetime_col: str = 'started_at') -> pl.DataFrame:
        """
        Извлечение базовых временных признаков.
        
        Args:
            df: DataFrame с данными
            datetime_col: Название колонки с datetime
            
        Returns:
            DataFrame с добавленными временными признаками
        """
        if datetime_col not in df.columns:
            raise ValueError(f"Колонка {datetime_col} не найдена")
        
        df_with_features = df.with_columns([
            # Базовые временные компоненты
            pl.col(datetime_col).dt.year().alias('year'),
            pl.col(datetime_col).dt.month().alias('month'),
            pl.col(datetime_col).dt.day().alias('day'),
            pl.col(datetime_col).dt.hour().alias('hour'),
            pl.col(datetime_col).dt.minute().alias('minute'),
            pl.col(datetime_col).dt.weekday().alias('weekday'),  # 1=Monday, 7=Sunday
            pl.col(datetime_col).dt.ordinal_day().alias('day_of_year'),
            pl.col(datetime_col).dt.week().alias('week_of_year'),
            
            # Дата без времени
            pl.col(datetime_col).dt.date().alias('date'),
            
            # Сезон (1=Winter, 2=Spring, 3=Summer, 4=Fall)
            pl.when(pl.col(datetime_col).dt.month().is_in([12, 1, 2]))
            .then(pl.lit(1))  # Winter
            .when(pl.col(datetime_col).dt.month().is_in([3, 4, 5]))
            .then(pl.lit(2))  # Spring
            .when(pl.col(datetime_col).dt.month().is_in([6, 7, 8]))
            .then(pl.lit(3))  # Summer
            .otherwise(pl.lit(4))  # Fall
            .alias('season'),
            
            # Выходной день (True для субботы и воскресенья)
            (pl.col(datetime_col).dt.weekday() >= 6).alias('is_weekend'),
            
            # Пиковые часы
            (
                (pl.col(datetime_col).dt.hour() >= self.morning_peak[0]) &
                (pl.col(datetime_col).dt.hour() < self.morning_peak[1])
            ).alias('is_morning_peak'),
            
            (
                (pl.col(datetime_col).dt.hour() >= self.evening_peak[0]) &
                (pl.col(datetime_col).dt.hour() < self.evening_peak[1])
            ).alias('is_evening_peak'),
        ])
        
        # Общий признак пикового времени
        df_with_features = df_with_features.with_columns([
            (pl.col('is_morning_peak') | pl.col('is_evening_peak')).alias('is_peak_hour')
        ])
        
        # Добавляем праздники
        df_with_features = self._add_holiday_features(df_with_features)
        
        return df_with_features
    
    def _add_holiday_features(self, df: pl.DataFrame) -> pl.DataFrame:
        """Добавляет признаки праздников."""
        # Конвертируем праздники в список строк для Polars
        holiday_dates = [h.strftime('%Y-%m-%d') for h in self.holidays]
        
        df_with_holidays = df.with_columns([
            pl.col('date').cast(pl.Utf8).is_in(holiday_dates).alias('is_holiday')
        ])
        
        return df_with_holidays
    
    def calculate_trip_duration_features(self, df: pl.DataFrame,
                                       start_col: str = 'started_at',
                                       end_col: str = 'ended_at') -> pl.DataFrame:
        """
        Создает признаки на основе длительности поездок.
        
        Args:
            df: DataFrame с данными
            start_col: Колонка начала поездки
            end_col: Колонка окончания поездки
            
        Returns:
            DataFrame с признаками длительности
        """
        if start_col not in df.columns or end_col not in df.columns:
            raise ValueError(f"Колонки {start_col} или {end_col} не найдены")
        
        df_with_duration = df.with_columns([
            # Длительность в минутах
            ((pl.col(end_col) - pl.col(start_col)).dt.total_seconds() / 60.0)
            .alias('duration_minutes'),
            
            # Длительность в секундах
            (pl.col(end_col) - pl.col(start_col)).dt.total_seconds()
            .alias('duration_seconds'),
        ])
        
        # Категории длительности
        df_with_duration = df_with_duration.with_columns([
            # Короткие поездки (до 15 минут)
            (pl.col('duration_minutes') <= 15).alias('is_short_trip'),
            
            # Средние поездки (15-45 минут)
            (
                (pl.col('duration_minutes') > 15) & 
                (pl.col('duration_minutes') <= 45)
            ).alias('is_medium_trip'),
            
            # Длинные поездки (более 45 минут)
            (pl.col('duration_minutes') > 45).alias('is_long_trip'),
            
            # Очень короткие поездки (до 5 минут) - возможно ошибки
            (pl.col('duration_minutes') <= 5).alias('is_very_short_trip'),
            
            # Категориальная переменная длительности
            pl.when(pl.col('duration_minutes') <= 5)
            .then(pl.lit('very_short'))
            .when(pl.col('duration_minutes') <= 15)
            .then(pl.lit('short'))
            .when(pl.col('duration_minutes') <= 45)
            .then(pl.lit('medium'))
            .when(pl.col('duration_minutes') <= 120)
            .then(pl.lit('long'))
            .otherwise(pl.lit('very_long'))
            .alias('duration_category'),
        ])
        
        return df_with_duration
    
    def create_cyclical_features(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Создает циклические признаки для временных компонентов.
        
        Args:
            df: DataFrame с временными признаками
            
        Returns:
            DataFrame с циклическими признаками
        """
        df_cyclical = df
        
        # Циклические признаки для часа (0-23)
        if 'hour' in df.columns:
            df_cyclical = df_cyclical.with_columns([
                (2 * np.pi * pl.col('hour') / 24).sin().alias('hour_sin'),
                (2 * np.pi * pl.col('hour') / 24).cos().alias('hour_cos'),
            ])
        
        # Циклические признаки для дня недели (1-7)
        if 'weekday' in df.columns:
            df_cyclical = df_cyclical.with_columns([
                (2 * np.pi * pl.col('weekday') / 7).sin().alias('weekday_sin'),
                (2 * np.pi * pl.col('weekday') / 7).cos().alias('weekday_cos'),
            ])
        
        # Циклические признаки для месяца (1-12)
        if 'month' in df.columns:
            df_cyclical = df_cyclical.with_columns([
                (2 * np.pi * pl.col('month') / 12).sin().alias('month_sin'),
                (2 * np.pi * pl.col('month') / 12).cos().alias('month_cos'),
            ])
        
        # Циклические признаки для дня года (1-365/366)
        if 'day_of_year' in df.columns:
            df_cyclical = df_cyclical.with_columns([
                (2 * np.pi * pl.col('day_of_year') / 365).sin().alias('day_of_year_sin'),
                (2 * np.pi * pl.col('day_of_year') / 365).cos().alias('day_of_year_cos'),
            ])
        
        return df_cyclical
    
    def create_lag_features(self, df: pl.DataFrame, 
                           value_col: str,
                           date_col: str = 'date',
                           periods: List[int] = [1, 7, 30]) -> pl.DataFrame:
        """
        Создает лаговые признаки для временных рядов.
        
        Args:
            df: DataFrame с данными (должен быть отсортирован по дате)
            value_col: Колонка со значениями для лагов
            date_col: Колонка с датой
            periods: Список периодов для лагов
            
        Returns:
            DataFrame с лаговыми признаками
        """
        if value_col not in df.columns or date_col not in df.columns:
            raise ValueError(f"Колонки {value_col} или {date_col} не найдены")
        
        # Сортируем по дате
        df_sorted = df.sort(date_col)
        
        # Создаем лаговые признаки
        lag_expressions = []
        for period in periods:
            lag_expressions.extend([
                pl.col(value_col).shift(period).alias(f'{value_col}_lag_{period}'),
                pl.col(value_col).shift(-period).alias(f'{value_col}_lead_{period}'),
            ])
        
        df_with_lags = df_sorted.with_columns(lag_expressions)
        
        # Скользящие средние
        rolling_expressions = []
        for period in periods:
            if period > 1:
                rolling_expressions.extend([
                    pl.col(value_col).rolling_mean(period).alias(f'{value_col}_ma_{period}'),
                    pl.col(value_col).rolling_std(period).alias(f'{value_col}_std_{period}'),
                ])
        
        if rolling_expressions:
            df_with_lags = df_with_lags.with_columns(rolling_expressions)
        
        return df_with_lags
    
    def create_interaction_features(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Создает признаки взаимодействия между временными компонентами.
        
        Args:
            df: DataFrame с временными признаками
            
        Returns:
            DataFrame с признаками взаимодействия
        """
        interaction_features = []
        
        # Взаимодействие часа и дня недели
        if 'hour' in df.columns and 'weekday' in df.columns:
            interaction_features.append(
                (pl.col('hour') * 10 + pl.col('weekday')).alias('hour_weekday_interaction')
            )
        
        # Взаимодействие сезона �� выходного дня
        if 'season' in df.columns and 'is_weekend' in df.columns:
            interaction_features.append(
                (pl.col('season') * 10 + pl.col('is_weekend').cast(pl.Int32))
                .alias('season_weekend_interaction')
            )
        
        # Взаимодействие месяца и часа
        if 'month' in df.columns and 'hour' in df.columns:
            interaction_features.append(
                (pl.col('month') * 100 + pl.col('hour')).alias('month_hour_interaction')
            )
        
        if interaction_features:
            df = df.with_columns(interaction_features)
        
        return df
    
    def create_all_temporal_features(self, df: pl.DataFrame,
                                   datetime_col: str = 'started_at',
                                   end_datetime_col: Optional[str] = 'ended_at',
                                   include_cyclical: bool = True,
                                   include_interactions: bool = True) -> pl.DataFrame:
        """
        Создает все временные признаки одним вызовом.
        
        Args:
            df: DataFrame с данными
            datetime_col: Колонка с начальным временем
            end_datetime_col: Колонка с конечным временем (для длительности)
            include_cyclical: Включать циклические признаки
            include_interactions: Включать признаки взаимодействия
            
        Returns:
            DataFrame со всеми временными признаками
        """
        # Базовые временные признаки
        df_features = self.extract_time_features(df, datetime_col)
        
        # Признаки длительности
        if end_datetime_col and end_datetime_col in df.columns:
            df_features = self.calculate_trip_duration_features(
                df_features, datetime_col, end_datetime_col
            )
        
        # Циклические признаки
        if include_cyclical:
            df_features = self.create_cyclical_features(df_features)
        
        # Признаки взаимодействия
        if include_interactions:
            df_features = self.create_interaction_features(df_features)
        
        return df_features


# Функции-обертки для быстрого использования
def extract_time_features(df: pl.DataFrame, 
                         datetime_col: str = 'started_at') -> pl.DataFrame:
    """
    Извлечение временных признаков.
    
    Args:
        df: DataFrame с данными
        datetime_col: Название колонки с datetime
        
    Returns:
        DataFrame с временными признаками
    """
    extractor = TemporalFeatureExtractor()
    return extractor.extract_time_features(df, datetime_col)


def calculate_trip_duration_features(df: pl.DataFrame,
                                   start_col: str = 'started_at',
                                   end_col: str = 'ended_at') -> pl.DataFrame:
    """
    Признаки на основе длительности поездок.
    
    Args:
        df: DataFrame с данными
        start_col: Колонка начала поездки
        end_col: Колонка окончания поездки
        
    Returns:
        DataFrame с признаками длительности
    """
    extractor = TemporalFeatureExtractor()
    return extractor.calculate_trip_duration_features(df, start_col, end_col)


def create_lag_features(df: pl.DataFrame, 
                       value_col: str,
                       date_col: str = 'date',
                       periods: List[int] = [1, 7, 30]) -> pl.DataFrame:
    """
    Создание лаговых признаков для временных рядов.
    
    Args:
        df: DataFrame с данными
        value_col: Колонка со значениями
        date_col: Колонка с датой
        periods: Периоды для лагов
        
    Returns:
        DataFrame с лаговыми признаками
    """
    extractor = TemporalFeatureExtractor()
    return extractor.create_lag_features(df, value_col, date_col, periods)


def create_all_temporal_features(df: pl.DataFrame,
                                datetime_col: str = 'started_at',
                                end_datetime_col: Optional[str] = 'ended_at') -> pl.DataFrame:
    """
    Создание всех временных признаков.
    
    Args:
        df: DataFrame с данными
        datetime_col: Колонка с начальным временем
        end_datetime_col: Колонка с конечным временем
        
    Returns:
        DataFrame со всеми временными признаками
    """
    extractor = TemporalFeatureExtractor()
    return extractor.create_all_temporal_features(df, datetime_col, end_datetime_col)
