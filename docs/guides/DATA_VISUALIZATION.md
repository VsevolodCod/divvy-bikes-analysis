## Визуальное исследование данных

Этот модуль помогает быстро **увидеть структуру и проблемы в данных**: выбросы, пропуски, перекосы распределений, связи между признаками, а также базовую гео‑картинку по станциям и поездкам.

Основой является класс `DataExplorer` (Polars) и набор быстрых функций-обёрток.

## Быстрый старт

```python
import polars as pl
from src.data.load_data import load_raw_data
from src.visualization import explore_data

# Загрузить данные (Polars DataFrame)
trips: pl.DataFrame = load_raw_data(year=2024, month=1)

# Полное визуальное исследование
explore_data(trips)

# Быстрый режим (без тяжёлых графиков вроде pairplot)
explore_data(trips, quick=True)
```

## Что показывает визуальный обзор

### 1. Распределения числовых признаков
- **Гистограммы + KDE** по всем числовым колонкам
- Легко увидеть:
  - сильные хвосты распределений
  - перекосы (skewness)
  - подозрительные пики / артефакты округления

```python
from src.visualization import plot_distributions

plot_distributions(trips, plots_per_row=3)

# Для признаков с длинными хвостами можно использовать log_scale
# (пример: если бы была колонка с длительностью поездки)
# plot_distributions(trips, cols=["trip_duration"], log_scale=True)
```

### 2. Boxplot'ы и выбросы
- Boxplot для каждого числового признака
- На графике дополнительно выводятся `Q1`, `Median`, `Q3`
- Полезно для:
  - поиска выбросов
  - сравнения масштабов разных признаков

```python
from src.visualization import plot_boxplots

plot_boxplots(trips, plots_per_row=3)
```

### 3. Матрица корреляций и парные графики

- **Матрица корреляций** (Pearson или Spearman) по всем числовым колонкам
- Тепловая карта с маской верхнего треугольника
- В `explore_all` дополнительно строится `pairplot` (Seaborn) для первых 5 числовых колонок:
  - диагональ — KDE
  - вне диагонали — scatter‑графики

```python
from src.visualization import plot_correlations, DataExplorer

plot_correlations(trips, method="pearson")

explorer = DataExplorer(trips)
explorer.plot_pairplot()               # авто-выбор до 5 колонок
explorer.plot_pairplot(cols=["start_lat", "start_lng", "end_lat"], sample_size=2000)
```

### 4. Категориальные признаки

- Горизонтальные **bar‑chart'ы** для категориальных колонок (`Utf8`, `Categorical`)
- Для каждой колонки:
  - топ‑N значений
  - подписи с абсолютными значениями

```python
explorer = DataExplorer(trips)
explorer.plot_categorical_bars(top_n=15, plots_per_row=2)
```

### 5. Пропущенные значения

- **Тепловая карта пропусков**: строки по оси X, колонки по оси Y
- Быстро видно:
  - какие признаки чаще всего пустые
  - есть ли «паттерны» пропусков (например, блоками по периодам)

```python
explorer = DataExplorer(trips)
explorer.plot_missing_heatmap()
```

Если пропусков нет, выводится сообщение:

> ✅ Пропусков не обнаружено!

### 6. Временные ряды

- Агрегация по времени с помощью `group_by_dynamic` (Polars)
- Можно строить:
  - количество поездок
  - сумму / среднее / медиану по числовому признаку
- Частота: день, неделя, месяц, час (`"1d"`, `"1w"`, `"1mo"`, `"1h"`)

```python
explorer = DataExplorer(trips)

# Количество поездок по дням
explorer.plot_time_series(date_col="started_at", freq="1d")

# Количество поездок по неделям (пример с агрегацией)
explorer.plot_time_series(
    date_col="started_at",
    value_col=None,  # None означает подсчет количества записей
    agg="count",
    freq="1w",
)
```

### 7. Простая гео‑визуализация

Если в данных есть широта/долгота станций или точек начала/конца поездок,
можно быстро посмотреть **распределение точек на карте** (scatter поверх Matplotlib).

```python
explorer = DataExplorer(trips)

explorer.plot_geospatial_points(
    lat_col="start_lat",
    lon_col="start_lng",
    sample_size=10000,
    alpha=0.2,
)
```

> При необходимости этот метод можно легко адаптировать под geoplotlib или другие картографические библиотеки.

## Комплексный обзор: `explore_all`

Главная функция для «одной команды»:

```python
from src.visualization import explore_data

explore_data(trips)          # полный обзор
explore_data(trips, quick=True)  # быстрый режим
```

Последовательно выполняется:

1. **Распределения числовых признаков**
2. **Boxplot'ы**
3. **Матрица корреляций**
4. *(не quick)* **Pairplot** для первых 5 числовых признаков
5. **Категориальные bar‑chart'ы**
6. **Карта пропусков**
7. *(если есть datetime и не quick)* **Временной ряд** по первой временной колонке

Это даёт быстрый обзор и позволяет:
- увидеть выбросы и артефакты
- понять структуру категорий
- проверить пропуски
- оценить сезонность и тренды во времени

## API Reference

### `DataExplorer(df: pl.DataFrame)`

Основной класс визуального исследования.

**Атрибуты:**
- `numeric_cols` — числовые колонки
- `categorical_cols` — категориальные колонки
- `datetime_cols` — временные колонки

**Основные методы:**
- `plot_numeric_distributions(cols=None, figsize=(15, 10), plots_per_row=3, log_scale=False)`
- `plot_numeric_boxplots(cols=None, figsize=(15, 10), plots_per_row=3)`
- `plot_correlation_matrix(cols=None, figsize=(12, 10), method="pearson")`
- `plot_categorical_bars(cols=None, top_n=10, figsize=(15, 10), plots_per_row=2)`
- `plot_time_series(date_col, value_col=None, agg="count", freq="1d", figsize=(15, 6))`
- `plot_missing_heatmap(figsize=(12, 8))`
- `plot_pairplot(cols=None, sample_size=1000, hue=None)`
- `plot_geospatial_points(lat_col, lon_col, figsize=(8, 8), sample_size=5000, alpha=0.3)`
- `explore_all(quick=False)`

### Быстрые функции

Все принимают `pl.DataFrame` и просто создают внутри `DataExplorer`.

```python
from src.visualization import (
    plot_boxplots,
    plot_distributions,
    plot_correlations,
    explore_data,
)
```

- `plot_boxplots(df, **kwargs)` — быстрые boxplot'ы
- `plot_distributions(df, **kwargs)` — распределения числовых признаков
- `plot_correlations(df, **kwargs)` — матрица корреляций
- `explore_data(df, quick=False)` — полный визуальный обзор

## Советы по использованию

1. **Для первого знакомства с датасетом**  
   ```python
   explore_data(df)
   ```

2. **Если датасет очень большой**  
   Используйте быстрый режим и/или выборку:
   ```python
   explore_data(df, quick=True)
   df_sample = df.sample(100_000)
   explore_data(df_sample)
   ```

3. **Для поиска проблем с качеством данных**  
   - смотрите `plot_missing_heatmap()` для пропусков  
   - `plot_boxplots()` и `plot_distributions(log_scale=True)` для выбросов  
   - `plot_categorical_bars()` для подозрительных «мусорных» категорий

4. **Для гео‑анализа**  
   Используйте `plot_geospatial_points()` на столбцах с координатами станций
   или точек начала/конца поездок.


