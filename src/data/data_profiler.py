"""Профилирование и анализ данных."""
import polars as pl
from typing import Optional, List
from datetime import datetime


class DataProfiler:
    """Класс для анализа и профилирования данных."""
    
    # ANSI цвета для красивого вывода
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    
    def __init__(self, df: pl.DataFrame):
        self.df = df
        self.n_rows = df.shape[0]
        self.n_cols = df.shape[1]
    
    def _print_header(self, text: str, color: str = CYAN):
        """Печать заголовка секции."""
        print(f"\n{color}{self.BOLD}{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}{self.RESET}\n")
    
    def _print_subheader(self, text: str):
        """Печать подзаголовка."""
        print(f"{self.BOLD}{self.BLUE}{text}{self.RESET}")
    
    def basic_info(self):
        """Базовая информация о датасете."""
        self._print_header("БАЗОВАЯ ИНФОРМАЦИЯ")
        
        print(f"{self.BOLD}Размер датасета:{self.RESET}")
        print(f"  Строк: {self.n_rows:,}")
        print(f"  Колонок: {self.n_cols}")
        print(f"  Размер в памяти: {self.df.estimated_size('mb'):.2f} MB")
        
        print(f"\n{self.BOLD}Типы данных:{self.RESET}")
        schema = self.df.schema
        type_counts = {}
        for col, dtype in schema.items():
            dtype_str = str(dtype)
            type_counts[dtype_str] = type_counts.get(dtype_str, 0) + 1
        
        for dtype, count in sorted(type_counts.items()):
            print(f"  {dtype}: {count} колонок")
        
        print(f"\n{self.BOLD}Колонки:{self.RESET}")
        for i, (col, dtype) in enumerate(schema.items(), 1):
            print(f"  {i:2d}. {col:30s} ({dtype})")
    
    def check_missing(self):
        """Проверка пропущенных значений."""
        self._print_header("АНАЛИЗ ПРОПУСКОВ")
        
        # Подсчет пропусков по колонкам
        null_counts = self.df.null_count()
        
        total_cells = self.n_rows * self.n_cols
        total_nulls = sum(null_counts.row(0))
        null_percentage = (total_nulls / total_cells) * 100
        
        print(f"{self.BOLD}Общая статистика:{self.RESET}")
        print(f"  Всего пропусков: {total_nulls:,}")
        print(f"  Доля пропусков: {null_percentage:.2f}%")
        
        # Строки с пропусками
        rows_with_nulls = self.df.select(
            pl.any_horizontal(pl.all().is_null())
        ).sum().item()
        rows_null_pct = (rows_with_nulls / self.n_rows) * 100
        print(f"  Строк с пропусками: {rows_with_nulls:,} ({rows_null_pct:.2f}%)")
        
        # Детали по колонкам
        print(f"\n{self.BOLD}Пропуски по колонкам:{self.RESET}")
        
        has_nulls = False
        for col in self.df.columns:
            null_count = null_counts[col][0]
            if null_count > 0:
                has_nulls = True
                null_pct = (null_count / self.n_rows) * 100
                color = self.RED if null_pct > 50 else self.YELLOW if null_pct > 10 else self.GREEN
                print(f"  {color}• {col:30s}: {null_count:8,} ({null_pct:5.2f}%){self.RESET}")
        
        if not has_nulls:
            print(f"  {self.GREEN}Пропусков не обнаружено!{self.RESET}")
    
    def check_duplicates(self):
        """Проверка дубликатов."""
        self._print_header("ПРОВЕРКА ДУБЛИКАТОВ")
        
        # Полные дубликаты
        n_duplicates = self.df.is_duplicated().sum()
        dup_pct = (n_duplicates / self.n_rows) * 100
        
        print(f"{self.BOLD}Полные дубликаты:{self.RESET}")
        if n_duplicates > 0:
            print(f"  {self.YELLOW}Найдено: {n_duplicates:,} строк ({dup_pct:.2f}%){self.RESET}")
        else:
            print(f"  {self.GREEN}Полных дубликатов не найдено{self.RESET}")
        
        # Уникальные строки
        n_unique = self.df.unique().shape[0]
        print(f"\n{self.BOLD}Уникальность:{self.RESET}")
        print(f"  Уникальных строк: {n_unique:,}")
        print(f"  Доля уникальных: {(n_unique/self.n_rows)*100:.2f}%")
    
    def describe_numeric(self):
        """Описание числовых колонок."""
        self._print_header("ЧИСЛОВЫЕ ДАННЫЕ")
        
        numeric_cols = [col for col, dtype in self.df.schema.items() 
                       if dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, 
                                   pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                                   pl.Float32, pl.Float64]]
        
        if not numeric_cols:
            print(f"  {self.YELLOW}Числовых колонок не найдено{self.RESET}")
            return
        
        print(f"{self.BOLD}Найдено {len(numeric_cols)} числовых колонок{self.RESET}\n")
        
        # Статистика
        stats = self.df.select(numeric_cols).describe()
        print(stats)
    
    def describe_categorical(self):
        """Описание категориальных колонок."""
        self._print_header("КАТЕГОРИАЛЬНЫЕ ДАННЫЕ")
        
        # Строковые и категориальные колонки
        cat_cols = [col for col, dtype in self.df.schema.items() 
                   if dtype in [pl.Utf8, pl.Categorical]]
        
        if not cat_cols:
            print(f"  {self.YELLOW}Категориальных колонок не найдено{self.RESET}")
            return
        
        print(f"{self.BOLD}Найдено {len(cat_cols)} категориальных колонок{self.RESET}\n")
        
        for col in cat_cols:
            n_unique = self.df[col].n_unique()
            n_nulls = self.df[col].null_count()
            
            print(f"{self.BOLD}{self.BLUE}▸ {col}{self.RESET}")
            print(f"  Уникальных значений: {n_unique:,}")
            print(f"  Пропусков: {n_nulls:,}")
            
            # Топ-5 значений
            if n_unique > 0:
                top_values = (
                    self.df
                    .group_by(col)
                    .agg(pl.len().alias('count'))
                    .sort('count', descending=True)
                    .head(5)
                )
                
                print(f"  Топ-5 значений:")
                for row in top_values.iter_rows(named=True):
                    value = row[col]
                    count = row['count']
                    pct = (count / self.n_rows) * 100
                    # Обрезаем длинные значения
                    value_str = str(value)[:40] + '...' if len(str(value)) > 40 else str(value)
                    print(f"    - {value_str:40s}: {count:8,} ({pct:5.2f}%)")
            print()
    
    def describe_datetime(self):
        """Описание временных колонок."""
        self._print_header("ВРЕМЕННЫЕ ДАННЫЕ")
        
        datetime_cols = [col for col, dtype in self.df.schema.items() 
                        if dtype in [pl.Date, pl.Datetime, pl.Time, pl.Duration]]
        
        if not datetime_cols:
            print(f"  {self.YELLOW}Временных колонок не найдено{self.RESET}")
            return
        
        print(f"{self.BOLD}Найдено {len(datetime_cols)} временных колонок{self.RESET}\n")
        
        for col in datetime_cols:
            print(f"{self.BOLD}{self.BLUE}▸ {col}{self.RESET}")
            
            col_data = self.df[col].drop_nulls()
            if len(col_data) > 0:
                min_val = col_data.min()
                max_val = col_data.max()
                
                print(f"  Минимум: {min_val}")
                print(f"  Максимум: {max_val}")
                
                # Для datetime вычисляем диапазон
                if self.df.schema[col] == pl.Datetime:
                    range_days = (max_val - min_val).days if hasattr(max_val - min_val, 'days') else 'N/A'
                    print(f"  Диапазон: {range_days} дней")
            
            n_nulls = self.df[col].null_count()
            print(f"  Пропусков: {n_nulls:,}")
            print()
    
    def sample_data(self, n: int = 5):
        """Показать примеры данных."""
        self._print_header("ПРИМЕРЫ ДАННЫХ")
        
        print(f"{self.BOLD}Первые {n} строк:{self.RESET}")
        print(self.df.head(n))
        
        print(f"\n{self.BOLD}Последние {n} строк:{self.RESET}")
        print(self.df.tail(n))
        
        if self.n_rows > n * 2:
            print(f"\n{self.BOLD}Случайная выборка ({n} строк):{self.RESET}")
            print(self.df.sample(n))
    
    def full_report(self, show_samples: bool = True, sample_size: int = 3):
        """Полный отчет по данным."""
        print(f"\n{self.CYAN}{self.BOLD}")
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 15 + "DATA PROFILING REPORT" + " " * 22 + "║")
        print("╚" + "═" * 58 + "╝")
        print(self.RESET)
        
        self.basic_info()
        self.check_missing()
        self.check_duplicates()
        self.describe_numeric()
        self.describe_categorical()
        self.describe_datetime()
        
        if show_samples:
            self.sample_data(sample_size)
        
        print(f"\n{self.GREEN}{self.BOLD}Анализ завершен!{self.RESET}\n")


def check_data(df: pl.DataFrame, 
               show_samples: bool = True,
               sample_size: int = 3) -> None:
    """
    Быстрая функция для анализа данных.
    
    Args:
        df: DataFrame для анализа
        show_samples: Показывать ли примеры данных
        sample_size: Количество строк в примерах
    
    Example:
        >>> from src.data.load_data import load_raw_data
        >>> from src.data.data_profiler import check_data
        >>> 
        >>> trips = load_raw_data(year=2024, month=1)
        >>> check_data(trips)
    """
    profiler = DataProfiler(df)
    profiler.full_report(show_samples=show_samples, sample_size=sample_size)


def quick_check(df: pl.DataFrame) -> None:
    """
    Быстрая проверка данных (без примеров).
    
    Args:
        df: DataFrame для анализа
    """
    profiler = DataProfiler(df)
    profiler.basic_info()
    profiler.check_missing()
    profiler.check_duplicates()
