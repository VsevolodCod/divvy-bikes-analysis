# divvy_bikes_unit_economics

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Comprehensive analysis of Divvy bike-sharing unit economics and market dynamics

## Project Organization

```
divvy-bikes-analysis/
├── data/                    # Данные проекта
│   ├── raw/                # Исходные данные (2013-2025)
│   ├── interim/            # Промежуточные данные
│   ├── processed/          # Обработанные данные
│   └── external/           # Внешние источники данных
│
├── src/                    # Исходный код проекта
│   ├── data/              # Обработка данных
│   │   ├── load_data.py       # Загрузка данных из файлов
│   │   ├── clean_data.py      # Очистка и валидация
│   │   └── merge_data.py      # Объединение датасетов
│   │
│   ├── features/          # Feature engineering
│   │   ├── temporal_features.py   # Временные признаки (час, день, сезон)
│   │   └── spatial_features.py    # Пространственные признаки (расстояния, маршруты)
│   │
│   ├── models/            # Модели и аналитика
│   │   ├── unit_economics.py      # Модель юнит-экономики
│   │   └── sensitivity.py         # Анализ чувствительности
│   │
│   └── visualization/     # Визуализации
│       ├── time_series.py         # Графики временных рядов
│       └── economic_metrics.py    # Экономические показатели
│
├── divvy_analysis/         # Существующий пакет (legacy)
│   ├── config.py          # Конфигурация
│   ├── dataset.py         # Работа с данными
│   ├── features.py        # Создание признаков
│   ├── plots.py           # Визуализация
│   └── modeling/          # Модели
│
├── notebooks/              # Jupyter notebooks для исследований
├── models/                 # Сохраненные модели
├── reports/                # Отчеты и результаты
│   └── figures/           # Графики для отчетов
├── tests/                  # Тесты
├── docs/                   # Документация
└── references/             # Справочные материалы
```

--------

