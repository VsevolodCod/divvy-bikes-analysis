"""Визуализация и исследование данных."""
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Optional, List, Tuple
import warnings

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class DataExplorer:
    """Класс для визуализации и исследования данных."""
    
    def __init__(self, df: pl.DataFrame):
        """
        Инициализация исследователя данных.
        
        Args:
            df: DataFrame для визуализации
        """
        self.df = df
        self.numeric_cols = self._get_numeric_columns()
        self.categorical_cols = self._get_categorical_columns()
        self.datetime_cols = self._get_datetime_columns()
    
    def _get_numeric_columns(self) -> List[str]:
        """Получить список числовых колонок."""
        return [
            col for col, dtype in self.df.schema.items()
            if dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64,
                        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                        pl.Float32, pl.Float64]
        ]
    
    def _get_categorical_columns(self) -> List[str]:
        """Получить список категориальных колонок."""
        return [
            col for col, dtype in self.df.schema.items()
            if dtype in [pl.Utf8, pl.Categorical]
        ]
    
    def _get_datetime_columns(self) -> List[str]:
        """Получить список временных колонок."""
        return [
            col for col, dtype in self.df.schema.items()
            if dtype in [pl.Date, pl.Datetime]
        ]
    
    def plot_numeric_distributions(
        self,
        cols: Optional[List[str]] = None,
        figsize: Tuple[int, int] = (15, 10),
        plots_per_row: int = 3,
        log_scale: bool = False,
    ) -> None:
        """
        Распределения числовых переменных (гистограммы + KDE).
        
        Args:
            cols: Список колонок (если None - все числовые)
            figsize: Размер фигуры
            plots_per_row: Количество графиков в строке
            log_scale: Логарифмическая шкала по оси X (удобно для признаков с хвостами)
        """
        cols = cols or self.numeric_cols
        
        if not cols:
            print("Числовых колонок не найдено")
            return
        
        n_cols = len(cols)
        n_rows = (n_cols + plots_per_row - 1) // plots_per_row
        
        fig, axes = plt.subplots(
            n_rows,
            plots_per_row,
            figsize=(figsize[0], figsize[1] * n_rows / 3))

        if n_rows == 1:
            axes = [axes] if plots_per_row == 1 else axes
        else:
            axes = axes.flatten()
        
        for idx, col in enumerate(cols):
            data_series = self.df[col].drop_nulls()
            if data_series.len() == 0:
                continue

            data = data_series.to_numpy()
            data = np.asarray(data, dtype=None)
            
            if data.ndim > 1:
                data = data.flatten()
            try:
                data = np.asarray(data, dtype=np.float64)
            except (ValueError, TypeError):
                continue
            
            mask = np.isfinite(data)
            data = data[mask]
            data = np.ascontiguousarray(data)
            
            if len(data) == 0:
                continue
            
            if len(data) < 2:
                continue
            
            if len(data) > 0:
                data_min, data_max = float(np.min(data)), float(np.max(data))
                
                if data_max > data_min:
                    try:
                        n_bins = min(50, max(10, int(np.sqrt(len(data)))))
                        counts, bin_edges = np.histogram(data, bins=n_bins, density=True)
                        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                        bin_width = bin_edges[1] - bin_edges[0]
                        axes[idx].bar(bin_centers, counts, width=bin_width * 0.9,
                                     alpha=0.6, color='skyblue', edgecolor='black')
                        
                    except Exception as e:
                        try:
                            counts, bin_edges = np.histogram(data, bins='auto', density=True)
                            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                            bin_width = bin_edges[1] - bin_edges[0]
                            axes[idx].bar(bin_centers, counts, width=bin_width * 0.9,
                                         alpha=0.6, color='skyblue', edgecolor='black')
                        except Exception:
                            axes[idx].text(0.5, 0.5, 
                                         f'Ошибка построения\nMin: {data_min:.2f}\nMax: {data_max:.2f}\nN: {len(data)}',
                                         transform=axes[idx].transAxes,
                                         ha='center', va='center')
                            axes[idx].set_title(f'Распределение: {col}', fontsize=12, fontweight='bold')
                            continue
                else:
                    axes[idx].text(0.5, 0.5, f'Все значения = {data_min}', 
                                 transform=axes[idx].transAxes,
                                 ha='center', va='center')
                    axes[idx].set_title(f'Распределение: {col}', fontsize=12, fontweight='bold')
                    continue
                
                try:
                    from scipy import stats
                    data_for_kde = data[(data > 0) & np.isfinite(data)] if log_scale else data[np.isfinite(data)]
                    if len(data_for_kde) > 1:
                        kde = stats.gaussian_kde(data_for_kde)
                        x_range = np.linspace(data_for_kde.min(), data_for_kde.max(), 100)
                        kde_values = kde(x_range)
                        axes[idx].plot(
                            x_range,
                            kde_values,
                            'r-',
                            linewidth=2,
                            label='KDE',
                        )
                except Exception:
                    pass
                
                axes[idx].set_title(
                    f'Распределение: {col}',
                    fontsize=12,
                    fontweight='bold',
                )
                axes[idx].set_xlabel(col)
                axes[idx].set_ylabel('Плотность')
                if log_scale and data_min > 0:
                    axes[idx].set_xscale('log')
                axes[idx].grid(True, alpha=0.3)
                if len(data) > 0:
                    axes[idx].legend()
        
        if isinstance(axes, np.ndarray):
            for idx in range(n_cols, len(axes)):
                if idx < len(axes):
                    fig.delaxes(axes[idx])
        elif isinstance(axes, list):
            for idx in range(n_cols, len(axes)):
                if idx < len(axes):
                    fig.delaxes(axes[idx])
        
        plt.tight_layout()
        plt.show()
    
    def plot_numeric_boxplots(
        self,
        cols: Optional[List[str]] = None,
        figsize: Tuple[int, int] = (15, 10),
        plots_per_row: int = 3,
    ) -> None:
        """
        Boxplot'ы для числовых переменных.
        
        Args:
            cols: Список колонок (если None - все числовые)
            figsize: Размер фигуры
            plots_per_row: Количество графиков в строке
        """
        cols = cols or self.numeric_cols
        
        if not cols:
            print("Числовых колонок не найдено")
            return
        
        n_cols = len(cols)
        n_rows = (n_cols + plots_per_row - 1) // plots_per_row
        
        fig, axes = plt.subplots(
            n_rows,
            plots_per_row,
            figsize=(figsize[0], figsize[1] * n_rows / 3),
        )

        if n_rows == 1:
            axes = [axes] if plots_per_row == 1 else axes
        else:
            axes = axes.flatten()
        
        for idx, col in enumerate(cols):
            data_series = self.df[col].drop_nulls()
            if data_series.len() == 0:
                continue
            
            data = data_series.to_numpy()
            if data.ndim > 1:
                data = data.flatten()
            
            if len(data) > 0:
                bp = axes[idx].boxplot(data, vert=True, patch_artist=True,
                                      boxprops=dict(facecolor='lightblue', alpha=0.7),
                                      medianprops=dict(color='red', linewidth=2),
                                      whiskerprops=dict(color='blue', linewidth=1.5),
                                      capprops=dict(color='blue', linewidth=1.5))
                
                axes[idx].set_title(f'Boxplot: {col}', fontsize=12, fontweight='bold')
                axes[idx].set_ylabel(col)
                axes[idx].grid(True, alpha=0.3, axis='y')
                
                q1, median, q3 = np.percentile(data, [25, 50, 75])
                axes[idx].text(0.02, 0.98, 
                             f'Q1: {q1:.2f}\nMedian: {median:.2f}\nQ3: {q3:.2f}',
                             transform=axes[idx].transAxes,
                             verticalalignment='top',
                             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                             fontsize=8)
        
        if isinstance(axes, np.ndarray):
            for idx in range(n_cols, len(axes)):
                if idx < len(axes):
                    fig.delaxes(axes[idx])
        elif isinstance(axes, list):
            for idx in range(n_cols, len(axes)):
                if idx < len(axes):
                    fig.delaxes(axes[idx])
        
        plt.tight_layout()
        plt.show()
    
    def plot_correlation_matrix(self,
                                cols: Optional[List[str]] = None,
                                figsize: Tuple[int, int] = (12, 10),
                                method: str = 'pearson') -> None:
        """
        Матрица корреляций для числовых переменных.
        
        Args:
            cols: Список колонок (если None - все числовые)
            figsize: Размер фигуры
            method: Метод корреляции ('pearson', 'spearman')
        """
        cols = cols or self.numeric_cols
        
        if not cols or len(cols) < 2:
            print("Недостаточно числовых колонок для корреляции")
            return
        
        corr_df = self.df.select(cols).to_pandas().corr(method=method)
        
        plt.figure(figsize=figsize)
        mask = np.triu(np.ones_like(corr_df, dtype=bool))
        sns.heatmap(corr_df, mask=mask, annot=True, fmt='.2f', 
                   cmap='coolwarm', center=0, square=True,
                   linewidths=1, cbar_kws={"shrink": 0.8})
        
        plt.title(f'Матрица корреляций ({method.capitalize()})', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.show()
    
    def plot_categorical_bars(self,
                             cols: Optional[List[str]] = None,
                             top_n: int = 10,
                             figsize: Tuple[int, int] = (15, 10),
                             plots_per_row: int = 2) -> None:
        """
        Столбчатые диаграммы для категориальных переменных.
        
        Args:
            cols: Список колонок (если None - все категориальные)
            top_n: Количество топ значений для отображения
            figsize: Размер фигуры
            plots_per_row: Количество графиков в строке
        """
        cols = cols or self.categorical_cols
        
        if not cols:
            print("Категориальных колонок не найдено")
            return
        
        n_cols = len(cols)
        n_rows = (n_cols + plots_per_row - 1) // plots_per_row
        
        fig, axes = plt.subplots(
            n_rows,
            plots_per_row,
            figsize=(figsize[0], figsize[1] * n_rows / 2),
        )
        
        if n_rows == 1:
            axes = [axes] if plots_per_row == 1 else axes
        else:
            axes = axes.flatten()
        
        for idx, col in enumerate(cols):
            value_counts = (
                self.df
                .group_by(col)
                .agg(pl.len().alias('count'))
                .sort('count', descending=True)
                .head(top_n)
            )
            
            if value_counts.height > 0:
                categories = value_counts[col].to_list()
                counts = value_counts['count'].to_list()
                bars = axes[idx].barh(range(len(categories)), counts, 
                                     color=plt.cm.viridis(np.linspace(0, 1, len(categories))))
                
                axes[idx].set_yticks(range(len(categories)))
                axes[idx].set_yticklabels([str(c)[:30] for c in categories])
                axes[idx].set_xlabel('Количество')
                axes[idx].set_title(f'Топ-{top_n}: {col}', 
                                   fontsize=12, fontweight='bold')
                axes[idx].grid(True, alpha=0.3, axis='x')
                
                for i, (bar, count) in enumerate(zip(bars, counts)):
                    axes[idx].text(count, i, f' {count:,}', 
                                 va='center', fontsize=9)
        
        if isinstance(axes, np.ndarray):
            for idx in range(n_cols, len(axes)):
                if idx < len(axes):
                    fig.delaxes(axes[idx])
        elif isinstance(axes, list):
            for idx in range(n_cols, len(axes)):
                if idx < len(axes):
                    fig.delaxes(axes[idx])
        
        plt.tight_layout()
        plt.show()
    
    def plot_time_series(self,
                        date_col: str,
                        value_col: Optional[str] = None,
                        agg: str = 'count',
                        freq: str = '1d',
                        figsize: Tuple[int, int] = (15, 6)) -> None:
        """
        Временной ряд.
        
        Args:
            date_col: Колонка с датой/временем
            value_col: Колонка со значениями (если None - считаем количество)
            agg: Агрегация ('count', 'sum', 'mean', 'median')
            freq: Частота ('1d' - день, '1w' - неделя, '1mo' - месяц, '1h' - час)
            figsize: Размер фигуры
        """
        if date_col not in self.datetime_cols:
            print(f"{date_col} не является временной колонкой")
            return
        
        freq_map = {
            'D': '1d', 'd': '1d',
            'W': '1w', 'w': '1w',
            'M': '1mo', 'm': '1mo',
            'H': '1h', 'h': '1h'
        }
        freq = freq_map.get(freq, freq)
        df_sorted = self.df.sort(date_col)
        
        if value_col is None:
            ts_data = (
                df_sorted
                .lazy()
                .group_by_dynamic(date_col, every=freq)
                .agg(pl.len().alias('count'))
                .collect()
            )
            y_col = 'count'
            y_label = 'Количество'
        else:
            agg_expr = {
                'count': pl.len(),
                'sum': pl.col(value_col).sum(),
                'mean': pl.col(value_col).mean(),
                'median': pl.col(value_col).median()
            }[agg]
            
            ts_data = (
                df_sorted
                .lazy()
                .group_by_dynamic(date_col, every=freq)
                .agg(agg_expr.alias('value'))
                .collect()
            )
            y_col = 'value'
            y_label = f'{agg.capitalize()} of {value_col}'
        
        fig, ax = plt.subplots(figsize=figsize)
        
        dates = ts_data[date_col].to_numpy()
        values = ts_data[y_col].to_numpy()
        
        ax.plot(dates, values, linewidth=2, marker='o', markersize=4, 
               color='steelblue', label=y_label)
        ax.fill_between(dates, values, alpha=0.3, color='steelblue')
        
        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.set_title(f'Временной ряд: {y_label}', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def plot_missing_heatmap(self, figsize: Tuple[int, int] = (12, 8)) -> None:
        """
        Тепловая карта пропущенных значений.
        
        Args:
            figsize: Размер фигуры
        """
        missing_matrix = self.df.select([
            pl.col(col).is_null().alias(col) for col in self.df.columns
        ]).to_pandas()
        
        if missing_matrix.sum().sum() == 0:
            print("Пропусков не обнаружено!")
            return
        
        plt.figure(figsize=figsize)
        
        sns.heatmap(
            missing_matrix.T,
            cmap='RdYlGn_r',
            cbar_kws={'label': 'Пропуск'},
            yticklabels=True,
            xticklabels=False,
        )
        
        plt.title('Карта пропущенных значений', fontsize=16, fontweight='bold')
        plt.xlabel('Индекс строки')
        plt.ylabel('Колонки')
        plt.tight_layout()
        plt.show()
    
    def plot_pairplot(self,
                     cols: Optional[List[str]] = None,
                     sample_size: Optional[int] = 1000,
                     hue: Optional[str] = None) -> None:
        """
        Парные графики для числовых переменных.
        
        Args:
            cols: Список колонок (если None - все числовые, макс 5)
            sample_size: Размер выборки (для ускорения)
            hue: Колонка для цветового кодирования
        """
        cols = cols or self.numeric_cols[:5] 
        
        if not cols or len(cols) < 2:
            print("Недостаточно числовых колонок")
            return
        
        missing_cols = [col for col in cols if col not in self.df.columns]
        if missing_cols:
            print(f"Колонки не найдены: {missing_cols}")
            print(f"Доступные числовые колонки: {self.numeric_cols}")
            return
    
        if hue and hue not in self.df.columns:
            print(f"Колонка для hue не найдена: {hue}")
            return
        
        df_sample = self.df.select(cols + ([hue] if hue else []))
        if sample_size and df_sample.height > sample_size:
            df_sample = df_sample.sample(sample_size)
        df_pandas = df_sample.to_pandas()
        
        print(f"Построение pairplot для {len(cols)} колонок...")
        sns.pairplot(df_pandas, hue=hue, diag_kind='kde', corner=True)
        plt.suptitle('Парные графики', y=1.01, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def plot_geospatial_points(
        self,
        lat_col: str,
        lon_col: str,
        figsize: Tuple[int, int] = (8, 8),
        sample_size: Optional[int] = 5000,
        alpha: float = 0.3,
    ) -> None:
        """
        Простейшая гео-визуализация точек (станции, начальные/конечные точки поездок).
        Работает поверх Matplotlib в стиле scatter; при желании можно заменить на geoplotlib.
        
        Args:
            lat_col: Название колонки с широтой
            lon_col: Название колонки с долготой
            figsize: Размер фигуры
            sample_size: Размер выборки (для ускорения отрисовки)
            alpha: Прозрачность точек
        """
        if lat_col not in self.df.columns or lon_col not in self.df.columns:
            print(f"Не найдены колонки '{lat_col}' и/или '{lon_col}'")
            return
        
        df_geo = self.df.select([lat_col, lon_col]).drop_nulls()
        if sample_size and df_geo.height > sample_size:
            df_geo = df_geo.sample(sample_size)
        
        lats = df_geo[lat_col].to_numpy()
        lons = df_geo[lon_col].to_numpy()
        
        fig, ax = plt.subplots(figsize=figsize)
        ax.scatter(
            lons,
            lats,
            s=5,
            alpha=alpha,
            c='steelblue',
            edgecolors='none',
        )
        ax.set_xlabel('Долгота')
        ax.set_ylabel('Широта')
        ax.set_title('Гео-точки (простая карта)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def explore_all(self, quick: bool = False) -> None:
        """
        Полное исследование данных со всеми графиками.
        
        Args:
            quick: Быстрый режим (меньше графиков)
        """
        print("Начинаем визуальное исследование данных...\n")

        if self.numeric_cols:
            print("1. Распределения числовых переменных")
            self.plot_numeric_distributions()
        
        # 2. Boxplot'ы
        if self.numeric_cols:
            print("\n2. Boxplot'ы числовых переменных")
            self.plot_numeric_boxplots()
        

        if len(self.numeric_cols) >= 2:
            print("\n3. Матрица корреляций")
            self.plot_correlation_matrix()
        
        if len(self.numeric_cols) >= 2 and not quick:
            limited_cols = self.numeric_cols[:5]
            print(f"\n3.1. Парные графики для колонок: {limited_cols}")
            self.plot_pairplot(cols=limited_cols, sample_size=1500)
        
        if self.categorical_cols:
            print("\n4. Категориальные переменные")
            self.plot_categorical_bars()
        
        print("\n5. Карта пропусков")
        self.plot_missing_heatmap()
        
        if self.datetime_cols and not quick:
            print(f"\n6. Временной ряд по {self.datetime_cols[0]}")
            self.plot_time_series(self.datetime_cols[0], freq='1d')
        
        print("\nВизуальное исследование завершено!")


def plot_boxplots(df: pl.DataFrame, **kwargs) -> None:
    """Быстрая функция для boxplot'ов."""
    explorer = DataExplorer(df)
    explorer.plot_numeric_boxplots(**kwargs)


def plot_distributions(df: pl.DataFrame, **kwargs) -> None:
    """Быстрая функция для распределений."""
    explorer = DataExplorer(df)
    explorer.plot_numeric_distributions(**kwargs)


def plot_correlations(df: pl.DataFrame, **kwargs) -> None:
    """Быстрая функция для корреляций."""
    explorer = DataExplorer(df)
    explorer.plot_correlation_matrix(**kwargs)


def explore_data(df: pl.DataFrame, quick: bool = False) -> None:
    """Быстрая функция для полного исследования."""
    explorer = DataExplorer(df)
    explorer.explore_all(quick=quick)
