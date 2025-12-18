# Design Document

## Overview

Проект реорганизации структуры Divvy bikes analysis направлен на создание четкой, стандартизированной структуры папок согласно cookiecutter data science template. В корневой директории находится более 200 файлов изображений (PNG), анимаций (GIF) и отчетов (HTML), которые необходимо систематически организовать.

## Architecture

### Current State Analysis
- **Root directory**: содержит ~200+ PNG файлов, ~30+ GIF анимаций, 9 HTML отчетов
- **Existing structure**: частично соответствует cookiecutter template (src/, notebooks/, tests/)
- **Legacy code**: папка divvy_analysis содержит старый код, который нужно интегрировать или удалить
- **Backup folders**: my-project-backup-* папки, которые нужно проанализировать и очистить

### Target Structure
```
divvy-bikes-analysis/
├── data/                    # Данные (создать если нет)
├── src/                     # Исходный код (уже существует)
├── notebooks/               # Jupyter notebooks (уже существует)
├── models/                  # Сохраненные модели (уже существует)
├── reports/                 # Отчеты и результаты
│   ├── figures/            # Все визуализации
│   │   ├── animations/     # GIF анимации
│   │   ├── heatmaps/       # Тепловые карты
│   │   ├── seasonal/       # Сезонный анализ
│   │   ├── hourly/         # Почасовой анализ
│   │   ├── stations/       # Анализ станций
│   │   ├── trends/         # Трендовый анализ
│   │   └── combined/       # Комбинированные визуализации
│   └── *.html              # HTML отчеты
├── tests/                   # Тесты (уже существует)
├── docs/                    # Документация (уже существует)
├── references/              # Справочные материалы (уже существует)
└── config files             # Конфигурационные файлы в корне
```

## Components and Interfaces

### File Classification System
Система классификации файлов основана на анализе имен файлов:

1. **Animation Files (.gif)**
   - `*_animation.gif` → `reports/figures/animations/`
   - Группировка по типам: seasonal, hourly, combined, etc.

2. **Image Files (.png)**
   - `heatmap_*` → `reports/figures/heatmaps/`
   - `season_*`, `*_fall_*`, `*_winter_*`, `*_spring_*`, `*_summer_*` → `reports/figures/seasonal/`
   - `*_hour_*`, `hourly_*` → `reports/figures/hourly/`
   - `combined_*` → `reports/figures/combined/`
   - `*_station*`, `top_*` → `reports/figures/stations/`
   - `trend_*` → `reports/figures/trends/`
   - `start_*`, `end_*` → `reports/figures/spatial/`

3. **Report Files (.html)**
   - All HTML files → `reports/`
   - Maintain original names for reference integrity

### Migration Strategy
1. **Analysis Phase**: Scan and categorize all files
2. **Backup Phase**: Create backup of current state
3. **Directory Creation**: Create target directory structure
4. **File Movement**: Move files according to classification rules
5. **Cleanup Phase**: Remove empty directories and backup folders
6. **Validation Phase**: Verify all files moved correctly

## Data Models

### File Classification Model
```python
FileClassification = {
    'source_path': str,
    'target_path': str,
    'file_type': str,  # 'image', 'animation', 'report'
    'category': str,   # 'heatmap', 'seasonal', 'hourly', etc.
    'action': str      # 'move', 'copy', 'delete'
}
```

### Migration Log Model
```python
MigrationLog = {
    'timestamp': datetime,
    'source': str,
    'destination': str,
    'status': str,     # 'success', 'failed', 'skipped'
    'reason': str      # Explanation for action taken
}
```

## Error Handling

### File Conflicts
- **Duplicate names**: Add timestamp suffix to avoid overwrites
- **Missing directories**: Create directories automatically
- **Permission errors**: Log and skip, provide manual intervention list

### Validation Checks
- **File integrity**: Verify file sizes before/after move
- **Reference integrity**: Check if moved files are referenced in code/notebooks
- **Completeness**: Ensure all files are accounted for

### Rollback Strategy
- Maintain detailed migration log
- Keep backup of original structure until validation complete
- Provide rollback script in case of issues

## Testing Strategy

### Pre-migration Tests
1. **File inventory**: Count and catalog all files by type
2. **Dependency analysis**: Check for hardcoded paths in code
3. **Disk space**: Verify sufficient space for reorganization

### Post-migration Tests
1. **File count verification**: Ensure no files lost
2. **Structure validation**: Verify target structure created correctly
3. **Reference testing**: Test that moved files are accessible
4. **Integration testing**: Run existing notebooks/scripts to check for broken paths

### Cleanup Validation
1. **Empty directory removal**: Verify only truly empty directories removed
2. **Backup folder analysis**: Ensure no unique data lost
3. **Legacy code integration**: Verify divvy_analysis folder properly handled

## Implementation Phases

### Phase 1: Analysis and Planning
- Scan current directory structure
- Classify all files according to naming patterns
- Identify potential conflicts and dependencies
- Create detailed migration plan

### Phase 2: Structure Creation
- Create target directory structure
- Set up logging and backup systems
- Prepare migration scripts

### Phase 3: File Migration
- Move files according to classification rules
- Update any hardcoded paths in code
- Generate migration log

### Phase 4: Cleanup and Validation
- Remove empty directories
- Clean up backup folders
- Validate migration success
- Update documentation

### Phase 5: Documentation Update
- Update README.md with new structure
- Create STRUCTURE.md guide
- Update any relevant documentation