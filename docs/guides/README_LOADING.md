# Полное руководство по загрузке данных Divvy Bikes

## Что реализовано

Система загрузки данных поддерживает:
- ✅ Загрузку всего года (все месяцы/кварталы)
- ✅ Загрузку конкретного месяца
- ✅ Загрузку квартала
- ✅ Загрузку диапазона лет
- ✅ Автоматическое определение формата файлов
- ✅ Поддержку старых (квартальных) и новых (месячных) форматов

## Быстрый старт

```python
from src.data.load_data import load_raw_data

# Весь год
trips = load_raw_data(year=2024)

# Конкретный месяц
trips_jan = load_raw_data(year=2024, month=1)

# Квартал
trips_q1 = load_raw_data(year=2024, quarter=1)
```

## Тестирование

```bash
# Базовый тест
python tests/test_load.py

# Тест месяцев и кварталов
python tests/test_month_quarter.py
```


## Примеры использования

### В Python скрипте

```python
from src.data.load_data import load_raw_data, DataLoader

# Простая загрузка
trips = load_raw_data(year=2024, month=7)

# Продвинутая загрузка
loader = DataLoader()
trips = loader.load_raw_trips_range(2022, 2024)
```

### В Jupyter Notebook

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))

from src.data.load_data import load_raw_data
import polars as pl

# Загрузка и анализ
trips = load_raw_data(year=2024, month=7)
print(f"Июль 2024: {trips.shape[0]:,} поездок")

# Группировка по дням недели
daily = trips.group_by(
    pl.col('started_at').dt.weekday()
).agg(pl.len().alias('trips'))
```

## 📁 Поддерживаемые форматы файлов

### Старый формат (2013-2019)
```
data/raw/2018/
  ├── Divvy_Trips_2018_Q1.csv
  ├── Divvy_Trips_2018_Q2.csv
  ├── Divvy_Trips_2018_Q3.csv
  └── Divvy_Trips_2018_Q4.csv
```

### Новый формат (2020+)
```
data/raw/2024/
  ├── 202401-divvy-tripdata.csv
  ├── 202402-divvy-tripdata.csv
  ├── ...
  └── 202412-divvy-tripdata.csv
```

Система автоматически определяет формат и загружает данные!

## API Reference

### `load_raw_data(year, month=None, quarter=None)`

Основная функция для загрузки данных.

**Параметры:**
- `year` (int): Год данных (2013-2025)
- `month` (int, optional): Месяц (1-12)
- `quarter` (int, optional): Квартал (1-4)

**Возвращает:**
- `pl.DataFrame`: DataFrame с данными поездок

**Примеры:**
```python
# Весь год
load_raw_data(year=2024)

# Месяц
load_raw_data(year=2024, month=7)

# Квартал
load_raw_data(year=2024, quarter=2)
```

### `DataLoader` класс

Для продвинутого использования.

**Методы:**
- `load_raw_trips_year(year)` - загрузить весь год
- `load_raw_trips_month(year, month)` - загрузить месяц
- `load_raw_trips_quarter(year, quarter)` - загрузить квартал
- `load_raw_trips_range(start_year, end_year)` - загрузить диапазон лет
- `save_dataframe(df, path, format='parquet')` - сохранить результат

## Сохранение результатов

```python
from src.data.load_data import DataLoader
from src.config.paths import INTERIM_DATA_DIR

loader = DataLoader()

# Обработка данных
trips = load_raw_data(year=2024, month=7)
processed = trips.filter(pl.col('duration') > 0)

# Сохранение
loader.save_dataframe(
    processed,
    INTERIM_DATA_DIR / 'trips_2024_07_clean.parquet'
)
```

## Best Practices

1. **Загружайте только нужные данные**
   ```python
   # Плохо: загружает весь год
   trips = load_raw_data(year=2024)
   july_trips = trips.filter(pl.col('started_at').dt.month() == 7)
   
   # Хорошо: загружает только июль
   july_trips = load_raw_data(year=2024, month=7)
   ```

2. **Используйте Parquet для промежуточных данных**
   ```python
   # Сохраняйте обработанные данные
   loader.save_dataframe(processed, path, format='parquet')
   ```

3. **Для больших периодов используйте LazyFrame**
   ```python
   import polars as pl
   lf = pl.scan_parquet('data/processed/trips_final.parquet')
   result = lf.filter(...).collect()
   ```

## Notebooks

- `notebooks/quick_start.ipynb` - быстрый старт
- `notebooks/example_data_loading.ipynb` - подробные примеры

## FAQ

**Q: Как загрузить только летние месяцы?**
```python
summer = []
for month in [6, 7, 8]:
    df = load_raw_data(year=2024, month=month)
    summer.append(df)
summer_trips = pl.concat(summer, how='diagonal')
```

**Q: Как загрузить данные за несколько лет?**
```python
loader = DataLoader()
trips = loader.load_raw_trips_range(2020, 2024)
```

**Q: Квартал загружает один файл или три месяца?**
- Для старых данных (2013-2019): загружает квартальный файл
- Для новых данных (2020+): загружает 3 месяца и объединяет

**Q: Сколько памяти нужно для загрузки года?**
- 2024 год (~5.8 млн поездок): ~500-800 MB в памяти
- Используйте `month=` если нужен только один месяц

## Troubleshooting

**FileNotFoundError: Не найдены файлы**
```bash
# Проверьте наличие данных
python scripts/setup_data.py

# Скачайте данные
./scripts/download_from_yandex_s3.sh
```

**Ошибка памяти**
```python
# Загружайте по месяцам вместо всего года
for month in range(1, 13):
    trips = load_raw_data(year=2024, month=month)
    # обработка
```
