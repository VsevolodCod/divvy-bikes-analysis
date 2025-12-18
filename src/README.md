# Исходный код проекта Divvy Bikes Analysis

Этот каталог содержит весь производственный код проекта, организованный по функциональным модулям.

## Структура

### `config/` - Конфигурация
- `paths.py` - Пути к файлам и директориям проекта

### `data/` - Обработка данных
- `load_data.py` (360 строк) - Загрузка данных из файлов с поддержкой Polars
- `clean_data.py` (354 строк) - Очистка и валидация данных
- `data_profiler.py` (269 строк) - Профилирование и анализ качества данных
- `data_manager.py` (80 строк) - Контекстный менеджер для работы с данными

### `features/` - Feature Engineering
- `temporal_features.py` (389 строк) - Временные признаки (час, день, сезон, циклические)
- `spatial_features.py` - Пространственные признаки (расстояния, маршруты)

### `models/` - Модели и аналитика
- `unit_economics.py` (194 строк) - Модель юнит-экономики с тарифными сетками
- `sensitivity.py` - Анализ чувствительности

### `visualization/` - Визуализации
- `data_explorer.py` (604 строк) - Исследовательский анализ данных
- `economic_metrics.py` (395 строк) - Экономические показатели и KPI
- `time_series.py` - Графики временных рядов

## Основные возможности

### Загрузка данных
```python
from src.data.load_data import load_raw_data, load_trips
from src.data.data_profiler import check_data

# Загрузка данных за год
trips_2024 = load_raw_data(year=2024)

# Быстрый анализ данных
check_data(trips_2024)
```

### Очистка данных
```python
from src.data.clean_data import clean_trip_data, validate_data

# Очистка данных
clean_trips = clean_trip_data(trips_2024)

# Валидация
validation_report = validate_data(clean_trips)
```

### Временные признаки
```python
from src.features.temporal_features import create_all_temporal_features

# Создание всех временных признаков
trips_with_features = create_all_temporal_features(
    clean_trips, 
    datetime_col='started_at',
    end_datetime_col='ended_at'
)
```

### Юнит-экономика
```python
from src.models.unit_economics import UnitEconomicsModel

# Расчет экономических метрик
economics = UnitEconomicsModel()
kpis = economics.calculate_kpis(trips_with_features)
revenue_metrics = economics.calculate_revenue_metrics(trips_with_features)
```

### Визуализация
```python
from src.visualization.data_explorer import explore_data
from src.visualization.economic_metrics import plot_kpi_dashboard

# Исследовательский анализ
explore_data(trips_with_features, quick=True)

# Дашборд KPI
plot_kpi_dashboard(kpis)
```

## Ключевые особенности

### Высокая производительность
- **Polars** для обработки 31M+ записей
- Оптимизированные алгоритмы очистки данных
- Эффективная работа с временными рядами

### Реальные тарифы
- Полная тарифная сетка 2020-2025 годов
- Точные формулы расчета стоимости поездок
- Учет всех типов велосипедов и пользователей

### Профессиональная визуализация
- Фирменная цветовая палитра (#1a1b9c → #88e5ff)
- Готовые шаблоны для презентаций
- Интерактивные дашборды

### Комплексная аналитика
- Временные паттерны и сезонность
- Географический анализ
- Юнит-экономика и KPI
- Проверка статистических гипотез

## Статистика кода

**Всего строк кода: 2,717**
- Обработка данных: 1,063 строк (39%)
- Визуализация: 999 строк (37%) 
- Feature Engineering: 389 строк (14%)
- Модели: 194 строки (7%)
- Конфигурация: 31 строка (1%)

Код покрывает все этапы анализа от загрузки сырых данных до финальных визуализаций и бизнес-метрик.