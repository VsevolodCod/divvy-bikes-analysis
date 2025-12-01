"""Контекстный менеджер для работы с данными."""
from contextlib import contextmanager
import polars as pl
from pathlib import Path
from typing import Generator

from src.config.paths import (
    PROCESSED_DATA_DIR, INTERIM_DATA_DIR, EXTERNAL_DATA_DIR
)


@contextmanager
def load_dataset(name: str, source: str = 'processed') -> Generator[pl.DataFrame, None, None]:
    """
    Контекстный менеджер для загрузки данных.
    
    Args:
        name: Имя датасета (без расширения)
        source: Источник данных (processed, interim, или путь к external)
    
    Yields:
        DataFrame с данными
    
    Example:
        >>> with load_dataset('trips_final', 'processed') as df:
        ...     analysis = df.group_by('year').agg(pl.count())
    """
    if source == 'processed':
        path = PROCESSED_DATA_DIR / f"{name}.parquet"
    elif source == 'interim':
        path = INTERIM_DATA_DIR / f"{name}.parquet"
    elif source == 'raw':
        raise ValueError("Для raw данных используйте load_raw_data(year)")
    else:
        # Для external данных source - это подпапка (weather, holidays, etc.)
        path = EXTERNAL_DATA_DIR / source / f"{name}.parquet"
    
    try:
        df = pl.read_parquet(path)
        yield df
    except FileNotFoundError:
        print(f"Файл не найден: {path}")
        yield pl.DataFrame()
    except Exception as e:
        print(f"Ошибка загрузки {name}: {e}")
        yield pl.DataFrame()
    finally:
        # Можно добавить логирование использования
        pass


@contextmanager
def lazy_load_dataset(name: str, source: str = 'processed') -> Generator[pl.LazyFrame, None, None]:
    """
    Контекстный менеджер для ленивой загрузки данных.
    
    Использует LazyFrame для эффективной работы с большими данными.
    
    Args:
        name: Имя датасета (без расширения)
        source: Источник данных
    
    Yields:
        LazyFrame с данными
    
    Example:
        >>> with lazy_load_dataset('trips_final') as lf:
        ...     result = lf.filter(pl.col('year') == 2024).collect()
    """
    if source == 'processed':
        path = PROCESSED_DATA_DIR / f"{name}.parquet"
    elif source == 'interim':
        path = INTERIM_DATA_DIR / f"{name}.parquet"
    else:
        path = EXTERNAL_DATA_DIR / source / f"{name}.parquet"
    
    try:
        lf = pl.scan_parquet(path)
        yield lf
    except FileNotFoundError:
        print(f"Файл не найден: {path}")
        yield pl.LazyFrame()
    except Exception as e:
        print(f"Ошибка загрузки {name}: {e}")
        yield pl.LazyFrame()
