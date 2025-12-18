"""Очистка и валидация данных велопроката Divvy."""

import polars as pl
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataCleaner:
    """Класс для очистки данных велопроката."""
    
    def __init__(self):
        """Инициализация с параметрами очистки."""
        # Границы Чикаго для фильтрации координат
        self.chicago_bounds = {
            'lat_min': 41.5,
            'lat_max': 42.5,
            'lng_min': -88.0,
            'lng_max': -87.0
        }
        
        # Разумные пределы для длительности поездок (в минутах)
        self.duration_limits = {
            'min': 1,      # Минимум 1 минута
            'max': 1440    # Максимум 24 часа
        }
    
    def clean_trip_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Комплексная очистка данных о поездках.
        
        Args:
            df: Исходный DataFrame
            
        Returns:
            Очищенный DataFrame
        """
        logger.info(f"Начало очистки данных. Исходный размер: {df.height:,} строк")
        
        # 1. Удаление дубликатов
        df_clean = self._remove_duplicates(df)
        
        # 2. Очистка временных меток
        df_clean = self._clean_timestamps(df_clean)
        
        # 3. Фильтрация географических аномалий
        df_clean = self._filter_geographic_outliers(df_clean)
        
        # 4. Очистка длительности поездок
        df_clean = self._clean_duration(df_clean)
        
        # 5. Стандартизация типов данных
        df_clean = self._standardize_data_types(df_clean)
        
        # 6. Обработка пропущенных станций
        df_clean = self._handle_missing_stations(df_clean)
        
        logger.info(f"Очистка завершена. Финальный размер: {df_clean.height:,} строк")
        logger.info(f"Удалено строк: {df.height - df_clean.height:,} ({(df.height - df_clean.height) / df.height * 100:.2f}%)")
        
        return df_clean
    
    def _remove_duplicates(self, df: pl.DataFrame) -> pl.DataFrame:
        """Удаление дубликатов."""
        initial_count = df.height
        
        # Удаляем полные дубликаты
        df_clean = df.unique()
        
        # Удаляем дубликаты по ride_id если есть
        if 'ride_id' in df.columns:
            df_clean = df_clean.unique(subset=['ride_id'])
        
        removed = initial_count - df_clean.height
        if removed > 0:
            logger.info(f"Удалено дубликатов: {removed:,}")
        
        return df_clean
    
    def _clean_timestamps(self, df: pl.DataFrame) -> pl.DataFrame:
        """Очистка временных меток."""
        # Определяем колонки с временными метками
        time_cols = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['started_at', 'ended_at', 'start_time', 'end_time']):
                time_cols.append(col)
        
        if not time_cols:
            return df
        
        # Конвертируем в datetime если нужно
        df_clean = df
        for col in time_cols:
            if df_clean[col].dtype != pl.Datetime:
                try:
                    df_clean = df_clean.with_columns(
                        pl.col(col).str.to_datetime().alias(col)
                    )
                except:
                    logger.warning(f"Не удалось конвертировать {col} в datetime")
        
        # Фильтруем отрицательные длительности
        if 'started_at' in df_clean.columns and 'ended_at' in df_clean.columns:
            initial_count = df_clean.height
            
            df_clean = df_clean.filter(
                pl.col('ended_at') > pl.col('started_at')
            )
            
            removed = initial_count - df_clean.height
            if removed > 0:
                logger.info(f"Удалено поездок с отрицательной длительностью: {removed:,}")
        
        return df_clean
    
    def _filter_geographic_outliers(self, df: pl.DataFrame) -> pl.DataFrame:
        """Фильтрация географических выбросов."""
        # Определяем колонки с координатами
        lat_cols = [col for col in df.columns if 'lat' in col.lower()]
        lng_cols = [col for col in df.columns if 'lng' in col.lower() or 'lon' in col.lower()]
        
        if not lat_cols or not lng_cols:
            return df
        
        initial_count = df.height
        
        # Фильтруем по границам Чикаго
        conditions = []
        
        for lat_col in lat_cols:
            conditions.extend([
                pl.col(lat_col).is_between(self.chicago_bounds['lat_min'], self.chicago_bounds['lat_max']),
                pl.col(lat_col).is_not_null()
            ])
        
        for lng_col in lng_cols:
            conditions.extend([
                pl.col(lng_col).is_between(self.chicago_bounds['lng_min'], self.chicago_bounds['lng_max']),
                pl.col(lng_col).is_not_null()
            ])
        
        # Применяем все условия
        if conditions:
            df_clean = df.filter(pl.all_horizontal(conditions))
            
            removed = initial_count - df_clean.height
            if removed > 0:
                logger.info(f"Удалено географических выбросов: {removed:,}")
        else:
            df_clean = df
        
        return df_clean
    
    def _clean_duration(self, df: pl.DataFrame) -> pl.DataFrame:
        """Очистка длительности поездок."""
        # Ищем колонку с длительностью
        duration_col = None
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['duration', 'trip_duration']):
                duration_col = col
                break
        
        # Если нет готовой колонки, создаем из временных меток
        if not duration_col and 'started_at' in df.columns and 'ended_at' in df.columns:
            df = df.with_columns([
                ((pl.col('ended_at') - pl.col('started_at')).dt.total_seconds() / 60.0)
                .alias('duration_minutes')
            ])
            duration_col = 'duration_minutes'
        
        if not duration_col:
            return df
        
        initial_count = df.height
        
        # Фильтруем по разумным пределам
        df_clean = df.filter(
            pl.col(duration_col).is_between(
                self.duration_limits['min'], 
                self.duration_limits['max']
            )
        )
        
        removed = initial_count - df_clean.height
        if removed > 0:
            logger.info(f"Удалено поездок с аномальной длительностью: {removed:,}")
        
        return df_clean
    
    def _standardize_data_types(self, df: pl.DataFrame) -> pl.DataFrame:
        """Стандартизация типов данных."""
        df_clean = df
        
        # Стандартизируем типы пользователей
        if 'member_casual' in df.columns:
            df_clean = df_clean.with_columns([
                pl.col('member_casual').str.to_lowercase().alias('member_casual')
            ])
        
        # Стандартизируем типы велосипедов
        if 'rideable_type' in df.columns:
            df_clean = df_clean.with_columns([
                pl.col('rideable_type').str.to_lowercase().alias('rideable_type')
            ])
        
        # Приводим ID станций к строковому типу
        for col in df.columns:
            if 'station_id' in col.lower():
                df_clean = df_clean.with_columns([
                    pl.col(col).cast(pl.Utf8).alias(col)
                ])
        
        return df_clean
    
    def _handle_missing_stations(self, df: pl.DataFrame) -> pl.DataFrame:
        """Обработка пропущенных данных о станциях."""
        station_cols = [col for col in df.columns if 'station' in col.lower()]
        
        if not station_cols:
            return df
        
        # Заполняем пропущенные названия станций
        for col in station_cols:
            if 'name' in col.lower():
                df = df.with_columns([
                    pl.col(col).fill_null("Non-Station Parking").alias(col)
                ])
            elif 'id' in col.lower():
                df = df.with_columns([
                    pl.col(col).fill_null("unknown").alias(col)
                ])
        
        return df
    
    def validate_data(self, df: pl.DataFrame) -> Dict[str, any]:
        """
        Валидация данных на корректность.
        
        Args:
            df: DataFrame для валидации
            
        Returns:
            Словарь с результатами валидации
        """
        validation_results = {
            'total_rows': df.height,
            'total_columns': len(df.columns),
            'issues': [],
            'warnings': [],
            'summary': {}
        }
        
        # Проверка на пустой DataFrame
        if df.height == 0:
            validation_results['issues'].append("DataFrame пустой")
            return validation_results
        
        # Проверка обязательных колонок
        required_cols = ['started_at', 'ended_at', 'member_casual']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            validation_results['issues'].append(f"Отсутствуют обязательные колонки: {missing_cols}")
        
        # Проверка пропущенных значений
        null_counts = {}
        for col in df.columns:
            null_count = df[col].null_count()
            if null_count > 0:
                null_counts[col] = {
                    'count': null_count,
                    'percentage': (null_count / df.height) * 100
                }
        
        validation_results['summary']['null_counts'] = null_counts
        
        # Проверка дубликатов
        if 'ride_id' in df.columns:
            duplicate_count = df.height - df['ride_id'].n_unique()
            if duplicate_count > 0:
                validation_results['warnings'].append(f"Найдено дубликатов по ride_id: {duplicate_count}")
        
        # Проверка временных меток
        if 'started_at' in df.columns and 'ended_at' in df.columns:
            negative_duration_count = df.filter(
                pl.col('ended_at') <= pl.col('started_at')
            ).height
            
            if negative_duration_count > 0:
                validation_results['warnings'].append(
                    f"Поездки с отрицательной длительностью: {negative_duration_count}"
                )
        
        # Проверка координат
        coord_cols = [col for col in df.columns if any(x in col.lower() for x in ['lat', 'lng', 'lon'])]
        for col in coord_cols:
            if 'lat' in col.lower():
                out_of_bounds = df.filter(
                    ~pl.col(col).is_between(self.chicago_bounds['lat_min'], self.chicago_bounds['lat_max'])
                ).height
            else:  # longitude
                out_of_bounds = df.filter(
                    ~pl.col(col).is_between(self.chicago_bounds['lng_min'], self.chicago_bounds['lng_max'])
                ).height
            
            if out_of_bounds > 0:
                validation_results['warnings'].append(
                    f"Координаты вне границ Чикаго в {col}: {out_of_bounds}"
                )
        
        return validation_results
    
    def generate_cleaning_report(self, original_df: pl.DataFrame, 
                               cleaned_df: pl.DataFrame) -> Dict[str, any]:
        """
        Генерирует отчет об очистке данных.
        
        Args:
            original_df: Исходный DataFrame
            cleaned_df: Очищенный DataFrame
            
        Returns:
            Отчет об очистке
        """
        report = {
            'original_size': original_df.height,
            'cleaned_size': cleaned_df.height,
            'removed_rows': original_df.height - cleaned_df.height,
            'removal_percentage': ((original_df.height - cleaned_df.height) / original_df.height) * 100,
            'data_quality_score': (cleaned_df.height / original_df.height) * 100
        }
        
        return report


def clean_trip_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    Функция-обертка для очистки данных о поездках.
    
    Args:
        df: Исходный DataFrame
        
    Returns:
        Очищенный DataFrame
    """
    cleaner = DataCleaner()
    return cleaner.clean_trip_data(df)


def validate_data(df: pl.DataFrame) -> Dict[str, any]:
    """
    Функция-обертка для валидации данных.
    
    Args:
        df: DataFrame для валидации
        
    Returns:
        Результаты валидации
    """
    cleaner = DataCleaner()
    return cleaner.validate_data(df)
