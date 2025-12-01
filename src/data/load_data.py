"""Загрузка данных Divvy Bikes."""
import polars as pl
from pathlib import Path
from typing import Optional, Union
import logging

from src.config.paths import (
    RAW_DATA_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR, EXTERNAL_DATA_DIR,
    TRIPS_CLEANED, TRIPS_FINAL, STATIONS_UNIFIED, DAILY_AGGREGATES,
    WEATHER_DATA, PROJECT_ROOT
)

logger = logging.getLogger(__name__)


class DataLoader:
    """Класс для загрузки данных Divvy Bikes."""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or PROJECT_ROOT / 'data'
    
    def load_raw_trips_month(self, year: int, month: int) -> pl.DataFrame:
        """
        Загрузить данные за конкретный месяц.
        
        Args:
            year: Год (2013-2025)
            month: Месяц (1-12)
        
        Returns:
            DataFrame с данными поездок за месяц
        """
        year_dir = RAW_DATA_DIR / str(year)
        
        if not year_dir.exists():
            raise FileNotFoundError(f"Директория {year_dir} не найдена")
        
        # Формат: YYYYMM-divvy-tripdata.csv
        month_str = f"{month:02d}"
        file_pattern = f"{year}{month_str}-divvy-tripdata.csv"
        file_path = year_dir / file_pattern
        
        if file_path.exists():
            logger.info(f"Загрузка {file_path.name}")
            return pl.read_csv(
                file_path,
                infer_schema_length=10000,
                try_parse_dates=True,
                low_memory=False
            )
        else:
            raise FileNotFoundError(f"Файл не найден: {file_pattern}")
    
    def load_raw_trips_quarter(self, year: int, quarter: int) -> pl.DataFrame:
        """
        Загрузить данные за квартал.
        
        Args:
            year: Год (2013-2025)
            quarter: Квартал (1-4)
        
        Returns:
            DataFrame с данными поездок за квартал
        """
        year_dir = RAW_DATA_DIR / str(year)
        
        if not year_dir.exists():
            raise FileNotFoundError(f"Директория {year_dir} не найдена")
        
        # Старый формат: Divvy_Trips_2018_Q1.csv
        quarter_file = year_dir / f"Divvy_Trips_{year}_Q{quarter}.csv"
        
        if quarter_file.exists():
            logger.info(f"Загрузка {quarter_file.name}")
            return pl.read_csv(
                quarter_file,
                infer_schema_length=10000,
                try_parse_dates=True,
                low_memory=False
            )
        else:
            # Если квартального файла нет, загружаем месяцы
            logger.info(f"Квартальный файл не найден, загружаем по месяцам")
            months = {
                1: [1, 2, 3],
                2: [4, 5, 6],
                3: [7, 8, 9],
                4: [10, 11, 12]
            }
            
            dfs = []
            for month in months[quarter]:
                try:
                    df = self.load_raw_trips_month(year, month)
                    dfs.append(df)
                except FileNotFoundError:
                    logger.warning(f"Месяц {month} не найден")
            
            if dfs:
                return pl.concat(dfs, how='diagonal')
            else:
                raise FileNotFoundError(f"Не найдены данные за Q{quarter} {year}")
    
    def load_raw_trips_year(self, year: int) -> pl.DataFrame:
        """
        Загрузить сырые данные о поездках за конкретный год.
        Автоматически загружает ВСЕ месяцы/кварталы за год.
        
        Args:
            year: Год данных (2013-2025)
        
        Returns:
            DataFrame с данными поездок за весь год
        """
        year_dir = RAW_DATA_DIR / str(year)
        
        if not year_dir.exists():
            raise FileNotFoundError(f"Директория {year_dir} не найдена")
        
        # Ищем все CSV файлы с поездками за год
        # Поддерживаем разные форматы имен файлов:
        # - Старый формат: Divvy_Trips_*.csv (кварталы)
        # - Новый формат: YYYYMM-divvy-tripdata.csv (месяцы)
        trip_files = list(year_dir.glob('Divvy_Trips_*.csv'))
        if not trip_files:
            trip_files = list(year_dir.glob(f'{year}*-divvy-tripdata.csv'))
        if not trip_files:
            trip_files = list(year_dir.glob('*tripdata.csv'))
        
        if not trip_files:
            raise FileNotFoundError(f"Не найдены файлы поездок за {year} год")
        
        logger.info(f"Найдено файлов: {len(trip_files)}")
        
        # Загружаем и объединяем все файлы
        dfs = []
        for file in sorted(trip_files):  # Сортируем для порядка
            logger.info(f"Загрузка {file.name}")
            try:
                df = pl.read_csv(
                    file,
                    infer_schema_length=10000,
                    try_parse_dates=True,
                    low_memory=False
                )
                dfs.append(df)
            except Exception as e:
                logger.warning(f"Ошибка загрузки {file}: {e}")
        
        if dfs:
            return pl.concat(dfs, how='diagonal')
        else:
            return pl.DataFrame()
    
    def load_raw_trips_range(self, start_year: int, end_year: int) -> pl.DataFrame:
        """
        Загрузить сырые данные за диапазон лет.
        
        Args:
            start_year: Начальный год
            end_year: Конечный год
        
        Returns:
            DataFrame с данными поездок
        """
        dfs = []
        for year in range(start_year, end_year + 1):
            try:
                df = self.load_raw_trips_year(year)
                if df.height > 0:
                    df = df.with_columns(pl.lit(year).alias('year'))
                    dfs.append(df)
            except FileNotFoundError:
                logger.warning(f"Пропуск {year} года: данные не найдены")
        
        return pl.concat(dfs, how='diagonal') if dfs else pl.DataFrame()
    
    def load_raw_stations_year(self, year: int) -> pl.DataFrame:
        """
        Загрузить данные о станциях за конкретный год.
        
        Args:
            year: Год данных
        
        Returns:
            DataFrame с данными о станциях
        """
        year_dir = RAW_DATA_DIR / str(year)
        
        if not year_dir.exists():
            raise FileNotFoundError(f"Директория {year_dir} не найдена")
        
        # Ищем файлы со станциями
        # Поддерживаем разные форматы
        station_files = list(year_dir.glob('Divvy_Stations_*.csv'))
        if not station_files:
            station_files = list(year_dir.glob('*stations*.csv'))
        
        if not station_files:
            raise FileNotFoundError(f"Не найдены файлы станций за {year} год")
        
        # Загружаем первый найденный файл
        logger.info(f"Загрузка {station_files[0].name}")
        return pl.read_csv(station_files[0])
    
    def load_interim_data(self, dataset_name: str) -> pl.DataFrame:
        """
        Загрузить промежуточные данные.
        
        Args:
            dataset_name: Имя датасета (без расширения)
        
        Returns:
            DataFrame
        """
        file_path = INTERIM_DATA_DIR / f"{dataset_name}.parquet"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл {file_path} не найден")
        
        return pl.read_parquet(file_path)
    
    def load_processed_data(self, dataset_name: str) -> pl.DataFrame:
        """
        Загрузить обработанные данные.
        
        Args:
            dataset_name: Имя датасета (без расширения)
        
        Returns:
            DataFrame
        """
        file_path = PROCESSED_DATA_DIR / f"{dataset_name}.parquet"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл {file_path} не найден")
        
        return pl.read_parquet(file_path)
    
    def load_external_data(self, source: str, dataset: str) -> pl.DataFrame:
        """
        Загрузить внешние данные.
        
        Args:
            source: Источник данных (weather, holidays, demographics)
            dataset: Имя датасета
        
        Returns:
            DataFrame
        """
        file_path = EXTERNAL_DATA_DIR / source / f"{dataset}.parquet"
        
        if file_path.exists():
            return pl.read_parquet(file_path)
        else:
            # Пробуем CSV если Parquet нет
            csv_path = EXTERNAL_DATA_DIR / source / f"{dataset}.csv"
            if csv_path.exists():
                return pl.read_csv(csv_path)
            else:
                raise FileNotFoundError(f"Файл не найден: {dataset}")
    
    def load_all_trips(self, use_processed: bool = True) -> pl.DataFrame:
        """
        Загрузить все данные о поездках.
        
        Args:
            use_processed: Использовать обработанные данные если доступны
        
        Returns:
            DataFrame с данными поездок
        """
        if use_processed and TRIPS_FINAL.exists():
            logger.info("Загрузка обработанных данных о поездках")
            return pl.read_parquet(TRIPS_FINAL)
        elif TRIPS_CLEANED.exists():
            logger.info("Загрузка очищенных данных о поездках")
            return pl.read_parquet(TRIPS_CLEANED)
        else:
            logger.info("Загрузка сырых данных о поездках")
            return self.load_raw_trips_range(2013, 2025)
    
    def save_dataframe(self, df: pl.DataFrame, path: Union[str, Path],
                      format: str = 'parquet'):
        """
        Сохранить DataFrame в файл.
        
        Args:
            df: DataFrame для сохранения
            path: Путь к файлу
            format: Формат файла (parquet или csv)
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'parquet':
            df.write_parquet(path)
        elif format == 'csv':
            df.write_csv(path)
        else:
            raise ValueError(f"Неподдерживаемый формат: {format}")
        
        logger.info(f"Данные сохранены: {path}")


# Функции для быстрого доступа
def load_trips(use_processed: bool = True) -> pl.DataFrame:
    """Загрузить данные о поездках."""
    loader = DataLoader()
    return loader.load_all_trips(use_processed=use_processed)


def load_stations() -> pl.DataFrame:
    """Загрузить данные о станциях."""
    loader = DataLoader()
    return loader.load_interim_data('stations_unified')


def load_daily_metrics() -> pl.DataFrame:
    """Загрузить ежедневные агрегаты."""
    loader = DataLoader()
    return loader.load_processed_data('daily_aggregates')


def load_weather() -> pl.DataFrame:
    """Загрузить данные о погоде."""
    if WEATHER_DATA.exists():
        return pl.read_parquet(WEATHER_DATA)
    else:
        raise FileNotFoundError("Данные о погоде не найдены")


def load_raw_data(year: int, month: int = None, quarter: int = None) -> pl.DataFrame:
    """
    Загрузка сырых данных за указанный период.
    
    Args:
        year: Год данных (2013-2025)
        month: Месяц данных (1-12, опционально)
        quarter: Квартал (1-4, опционально)
    
    Returns:
        DataFrame с данными поездок
    
    Examples:
        >>> # Загрузить весь год
        >>> trips = load_raw_data(year=2024)
        
        >>> # Загрузить конкретный месяц
        >>> trips_jan = load_raw_data(year=2024, month=1)
        
        >>> # Загрузить квартал
        >>> trips_q1 = load_raw_data(year=2018, quarter=1)
    """
    loader = DataLoader()
    
    if month is not None:
        return loader.load_raw_trips_month(year, month)
    elif quarter is not None:
        return loader.load_raw_trips_quarter(year, quarter)
    else:
        return loader.load_raw_trips_year(year)


def load_station_data(year: int = 2024) -> pl.DataFrame:
    """
    Загрузка данных о станциях.
    
    Args:
        year: Год данных (по умолчанию 2024)
    
    Returns:
        DataFrame с данными о станциях
    """
    loader = DataLoader()
    return loader.load_raw_stations_year(year)
