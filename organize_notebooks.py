#!/usr/bin/env python3
"""
Notebook Organization Script
Organizes notebooks and related files into logical subdirectories
"""

import os
import shutil
from pathlib import Path
import re

class NotebookOrganizer:
    def __init__(self, notebooks_dir="notebooks"):
        self.notebooks_dir = Path(notebooks_dir)
        self.target_structure = {
            'exploratory': [],  # Исследовательские ноутбуки
            'modeling': [],     # Модели и ML
            'analysis': [],     # Анализ данных
            'visualization': [], # Визуализация
            'reports': [],      # Отчеты и презентации
            'experiments': [],  # Эксперименты и тесты
            'assets': {         # Вспомогательные файлы
                'models': [],   # Сохраненные модели
                'data': [],     # Данные
                'images': [],   # Изображения
                'html': []      # HTML файлы
            }
        }
        
        # Правила классификации файлов
        self.classification_rules = {
            'exploratory': [
                r'start\.ipynb$', r'quick_start\.ipynb$', r'example.*\.ipynb$',
                r'data_.*example\.ipynb$', r'test.*\.ipynb$', r'Untitled\.ipynb$'
            ],
            'modeling': [
                r'модели\.ipynb$', r'юнит модель\.ipynb$', r'.*model.*\.ipynb$'
            ],
            'analysis': [
                r'\d{4}\.ipynb$',  # 2020.ipynb, 2021.ipynb etc
                r'анализ.*\.ipynb$', r'гипотизы\.ipynb$', r'additional_hypotheses.*',
                r'data_profiling.*\.ipynb$'
            ],
            'visualization': [
                r'data_visualization.*\.ipynb$', r'преза\.ipynb$'
            ],
            'reports': [
                r'заполнение пропусков.*\.ipynb$', r'в csv\.ipynb$'
            ],
            'experiments': [
                r'test_.*\.ipynb$'
            ],
            'assets': {
                'models': [r'.*\.pkl$'],
                'data': [r'.*\.csv$', r'.*\.json$', r'.*\.txt$'],
                'images': [r'.*\.png$', r'.*\.svg$', r'.*\.gif$'],
                'html': [r'.*\.html$']
            }
        }
    
    def create_structure(self):
        """Создает целевую структуру папок"""
        print("📁 Creating notebook organization structure...")
        
        # Создаем основные папки
        for folder in ['exploratory', 'modeling', 'analysis', 'visualization', 'reports', 'experiments']:
            folder_path = self.notebooks_dir / folder
            folder_path.mkdir(exist_ok=True)
            print(f"  ✓ Created {folder_path}")
        
        # Создаем папку assets и подпапки
        assets_path = self.notebooks_dir / 'assets'
        assets_path.mkdir(exist_ok=True)
        
        for subfolder in ['models', 'data', 'images', 'html']:
            subfolder_path = assets_path / subfolder
            subfolder_path.mkdir(exist_ok=True)
            print(f"  ✓ Created {subfolder_path}")
    
    def classify_file(self, filename):
        """Классифицирует файл по названию"""
        filename_lower = filename.lower()
        
        # Проверяем основные категории
        for category, patterns in self.classification_rules.items():
            if category == 'assets':
                continue
            for pattern in patterns:
                if re.search(pattern, filename_lower):
                    return category
        
        # Проверяем assets
        for asset_type, patterns in self.classification_rules['assets'].items():
            for pattern in patterns:
                if re.search(pattern, filename_lower):
                    return f'assets/{asset_type}'
        
        # По умолчанию - exploratory для .ipynb, assets/data для остальных
        if filename.endswith('.ipynb'):
            return 'exploratory'
        else:
            return 'assets/data'
    
    def organize_files(self, dry_run=True):
        """Организует файлы в папке notebooks"""
        action = "DRY RUN" if dry_run else "EXECUTING"
        print(f"\n🚀 {action}: Organizing notebook files...")
        
        # Получаем все файлы в корне notebooks (исключая папки)
        files_to_move = []
        for item in self.notebooks_dir.iterdir():
            if item.is_file() and item.name not in ['.gitkeep', '.python-version']:
                category = self.classify_file(item.name)
                target_path = self.notebooks_dir / category / item.name
                files_to_move.append({
                    'source': item,
                    'target': target_path,
                    'category': category
                })
        
        # Показываем или выполняем перемещения
        for item in files_to_move:
            if dry_run:
                print(f"  📋 {item['source'].name} → {item['category']}/")
            else:
                try:
                    # Убеждаемся, что целевая папка существует
                    item['target'].parent.mkdir(parents=True, exist_ok=True)
                    
                    # Перемещаем файл
                    shutil.move(str(item['source']), str(item['target']))
                    print(f"  ✅ Moved {item['source'].name} → {item['category']}/")
                    
                except Exception as e:
                    print(f"  ❌ Failed to move {item['source'].name}: {e}")
        
        return files_to_move
    
    def handle_existing_folders(self, dry_run=True):
        """Обрабатывает существующие папки"""
        action = "DRY RUN" if dry_run else "EXECUTING"
        print(f"\n📂 {action}: Handling existing folders...")
        
        existing_folders = [
            'catboost_env',
            'catboost_info', 
            'data_analysis_plots',
            'premium_analysis_results'
        ]
        
        for folder_name in existing_folders:
            folder_path = self.notebooks_dir / folder_name
            if folder_path.exists():
                if folder_name == 'catboost_env':
                    # Удаляем виртуальное окружение
                    if dry_run:
                        print(f"  📋 Remove virtual environment: {folder_name}/")
                    else:
                        shutil.rmtree(folder_path)
                        print(f"  🗑️ Removed virtual environment: {folder_name}/")
                
                elif folder_name == 'catboost_info':
                    # Перемещаем в assets/data
                    target = self.notebooks_dir / 'assets' / 'data' / folder_name
                    if dry_run:
                        print(f"  📋 Move {folder_name}/ → assets/data/")
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(folder_path), str(target))
                        print(f"  ✅ Moved {folder_name}/ → assets/data/")
                
                elif folder_name == 'data_analysis_plots':
                    # Перемещаем в assets/images
                    target = self.notebooks_dir / 'assets' / 'images' / folder_name
                    if dry_run:
                        print(f"  📋 Move {folder_name}/ → assets/images/")
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(folder_path), str(target))
                        print(f"  ✅ Moved {folder_name}/ → assets/images/")
                
                elif folder_name == 'premium_analysis_results':
                    # Перемещаем в reports (это результаты анализа)
                    target = self.notebooks_dir / 'reports' / folder_name
                    if dry_run:
                        print(f"  📋 Move {folder_name}/ → reports/")
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(folder_path), str(target))
                        print(f"  ✅ Moved {folder_name}/ → reports/")

def main():
    """Main execution function"""
    print("🚀 Starting Notebook Organization")
    print("=" * 50)
    
    organizer = NotebookOrganizer()
    
    # Создаем структуру
    organizer.create_structure()
    
    # Показываем план организации файлов
    print("\n" + "=" * 50)
    print("📋 FILE ORGANIZATION PLAN (DRY RUN)")
    print("=" * 50)
    files_plan = organizer.organize_files(dry_run=True)
    
    # Показываем план для папок
    print("\n" + "=" * 50)
    print("📂 FOLDER ORGANIZATION PLAN (DRY RUN)")
    print("=" * 50)
    organizer.handle_existing_folders(dry_run=True)
    
    print(f"\n📈 Summary: {len(files_plan)} files will be organized")
    print("\nTo execute the organization, run this script with --execute flag")

if __name__ == "__main__":
    import sys
    
    main()
    
    # Проверяем, хочет ли пользователь выполнить
    if "--execute" in sys.argv:
        print("\n" + "=" * 50)
        print("⚡ EXECUTING ORGANIZATION")
        print("=" * 50)
        organizer = NotebookOrganizer()
        organizer.create_structure()
        organizer.organize_files(dry_run=False)
        organizer.handle_existing_folders(dry_run=False)
        print("\n✅ Notebook organization completed!")
    else:
        print("\n💡 To execute organization, run: python organize_notebooks.py --execute")