"""Визуализация экономических показателей велопроката."""

import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings

warnings.filterwarnings('ignore')

# Фирменная цветовая палитра проекта
BRAND_COLORS = {
    'primary': '#1a1b9c',      # Темно-синий
    'secondary': '#88e5ff',     # Яркий голубой
    'gradient': ['#1a1b9c', '#2a3cad', '#3a5cbe', '#4a7ccf', '#5a9cdd', '#6abcee', '#7adcff', '#88e5ff'],
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8'
}


class EconomicMetricsVisualizer:
    """Класс для визуализации экономических показателей."""
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Инициализация визуализатора.
        
        Args:
            figsize: Размер фигур по умолчанию
        """
        self.figsize = figsize
        self.setup_style()
    
    def setup_style(self):
        """Настройка стиля графиков."""
        plt.style.use('default')
        sns.set_palette(BRAND_COLORS['gradient'])
        
        # Настройки matplotlib
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': '#cccccc',
            'axes.linewidth': 0.8,
            'axes.grid': True,
            'grid.color': '#f0f0f0',
            'grid.linewidth': 0.8,
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
        })
    
    def plot_revenue_breakdown(self, revenue_data: Dict, 
                             figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Разбивка выручки по категориям.
        
        Args:
            revenue_data: Словарь с данными о выручке
            figsize: Размер фигуры
        """
        figsize = figsize or self.figsize
        
        # Подготовка данных
        categories = ['Поездки', 'Подписки']
        values = [
            revenue_data.get('ride_revenue', 0),
            revenue_data.get('subscription_revenue', 0)
        ]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(figsize[0], figsize[1]))
        
        # Круговая диаграмма
        colors = [BRAND_COLORS['primary'], BRAND_COLORS['secondary']]
        wedges, texts, autotexts = ax1.pie(
            values, 
            labels=categories,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            explode=(0.05, 0.05)
        )
        
        # Улучшаем внешний вид текста
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)
        
        ax1.set_title('Состав выручки', fontsize=16, fontweight='bold', pad=20)
        
        # Столбчатая диаграмма
        bars = ax2.bar(categories, values, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
        
        # Добавляем значения на столбцы
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.01,
                    f'${value:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        ax2.set_title('Выручка по категориям', fontsize=16, fontweight='bold', pad=20)
        ax2.set_ylabel('Выручка ($)', fontsize=12)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
        
        plt.tight_layout()
        plt.show()
    
    def plot_revenue_trends(self, df: pl.DataFrame, 
                           figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Тренды выручки во времени.
        
        Args:
            df: DataFrame с данными по времени
            figsize: Размер фигуры
        """
        figsize = figsize or self.figsize
        
        if 'year' not in df.columns or 'total_revenue' not in df.columns:
            print("Необходимы колонки 'year' и 'total_revenue'")
            return
        
        # Группируем по годам
        yearly_revenue = df.group_by('year').agg([
            pl.col('total_revenue').sum().alias('revenue')
        ]).sort('year')
        
        fig, ax = plt.subplots(figsize=figsize)
        
        years = yearly_revenue['year'].to_list()
        revenues = yearly_revenue['revenue'].to_list()
        
        # Линейный график с заливкой
        ax.plot(years, revenues, marker='o', linewidth=3, markersize=8, 
               color=BRAND_COLORS['primary'], markerfacecolor=BRAND_COLORS['secondary'])
        ax.fill_between(years, revenues, alpha=0.3, color=BRAND_COLORS['primary'])
        
        # Добавляем значения на точки
        for year, revenue in zip(years, revenues):
            ax.annotate(f'${revenue/1e6:.1f}M', 
                       (year, revenue), 
                       textcoords="offset points", 
                       xytext=(0,10), 
                       ha='center',
                       fontweight='bold')
        
        ax.set_title('Рост выручки по годам', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Год', fontsize=12)
        ax.set_ylabel('Выручка ($)', fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
        
        # Добавляем сетку
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_kpi_dashboard(self, kpis: Dict, 
                          figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Дашборд ключевых показателей.
        
        Args:
            kpis: Словарь с KPI
            figsize: Размер фигуры
        """
        figsize = figsize or (16, 10)
        
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Определяем метрики для отображения
        metrics = [
            ('ARPU', kpis.get('arpu', 0), '$/месяц', BRAND_COLORS['primary']),
            ('LTV', kpis.get('ltv', 0), '$', BRAND_COLORS['secondary']),
            ('CAC', kpis.get('cac', 0), '$', BRAND_COLORS['info']),
            ('ROI', kpis.get('roi', 0), '%', BRAND_COLORS['success']),
            ('LTV/CAC', kpis.get('ltv_cac_ratio', 0), 'x', BRAND_COLORS['warning']),
            ('Gross Margin', kpis.get('gross_margin', 0) * 100, '%', BRAND_COLORS['danger']),
        ]
        
        # Создаем карточки метрик
        for i, (name, value, unit, color) in enumerate(metrics):
            row = i // 3
            col = i % 3
            ax = fig.add_subplot(gs[row, col])
            
            # Создаем карточку
            ax.text(0.5, 0.7, f'{value:,.1f}', 
                   ha='center', va='center', fontsize=24, fontweight='bold', 
                   color=color, transform=ax.transAxes)
            ax.text(0.5, 0.5, unit, 
                   ha='center', va='center', fontsize=12, 
                   color='gray', transform=ax.transAxes)
            ax.text(0.5, 0.2, name, 
                   ha='center', va='center', fontsize=14, fontweight='bold',
                   transform=ax.transAxes)
            
            # Убираем оси
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Добавляем рамку
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color(color)
                spine.set_linewidth(2)
        
        # Общий заголовок
        fig.suptitle('Панель ключевых показателей', fontsize=20, fontweight='bold', y=0.95)
        
        plt.show()
    
    def plot_user_type_comparison(self, user_metrics: pl.DataFrame,
                                 figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Сравнение метрик по типам пользователей.
        
        Args:
            user_metrics: DataFrame с метриками по пользователям
            figsize: Размер фигуры
        """
        figsize = figsize or self.figsize
        
        if 'member_casual' not in user_metrics.columns:
            print("Необходима колонка 'member_casual'")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(figsize[0] * 1.5, figsize[1] * 1.2))
        axes = axes.flatten()
        
        # Метрики для сравнения
        metrics = ['rides', 'revenue', 'avg_cost']
        
        for i, metric in enumerate(metrics):
            if metric not in user_metrics.columns:
                continue
                
            ax = axes[i]
            
            # Данные для графика
            user_types = user_metrics['member_casual'].to_list()
            values = user_metrics[metric].to_list()
            
            colors = [BRAND_COLORS['primary'] if ut == 'member' else BRAND_COLORS['secondary'] 
                     for ut in user_types]
            
            bars = ax.bar(user_types, values, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
            
            # Добавляем значения на столбцы
            for bar, value in zip(bars, values):
                height = bar.get_height()
                if metric == 'rides':
                    label = f'{value:,.0f}'
                elif metric in ['revenue', 'avg_cost']:
                    label = f'${value:,.2f}'
                else:
                    label = f'{value:.2f}'
                
                ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.01,
                       label, ha='center', va='bottom', fontweight='bold')
            
            ax.set_title(f'{metric.replace("_", " ").title()}', fontsize=14, fontweight='bold')
            ax.set_ylabel(metric.replace('_', ' ').title())
            
            if metric == 'revenue':
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
        
        # Убираем лишний subplot
        fig.delaxes(axes[3])
        
        plt.suptitle('Сравнение типов пользователей', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def plot_profitability_by_station(self, station_data: pl.DataFrame,
                                     top_n: int = 20,
                                     figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Прибыльность по станциям.
        
        Args:
            station_data: DataFrame с данными по станциям
            top_n: Количество топ станций для отображения
            figsize: Размер фигуры
        """
        figsize = figsize or (14, 8)
        
        if 'station_name' not in station_data.columns or 'revenue' not in station_data.columns:
            print("Необходимы колонки 'station_name' и 'revenue'")
            return
        
        # Топ станций по выручке
        top_stations = station_data.sort('revenue', descending=True).head(top_n)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        stations = top_stations['station_name'].to_list()
        revenues = top_stations['revenue'].to_list()
        
        # Создаем градиент цветов
        colors = plt.cm.viridis(np.linspace(0, 1, len(stations)))
        
        bars = ax.barh(range(len(stations)), revenues, color=colors, alpha=0.8, edgecolor='white')
        
        # Настраиваем оси
        ax.set_yticks(range(len(stations)))
        ax.set_yticklabels([s[:30] + '...' if len(s) > 30 else s for s in stations])
        ax.set_xlabel('Выручка ($)', fontsize=12)
        ax.set_title(f'Топ-{top_n} станций по выручке', fontsize=16, fontweight='bold', pad=20)
        
        # Добавляем значения
        for i, (bar, revenue) in enumerate(zip(bars, revenues)):
            ax.text(revenue + max(revenues) * 0.01, i, f'${revenue:,.0f}', 
                   va='center', fontweight='bold')
        
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))
        
        plt.tight_layout()
        plt.show()
    
    def plot_seasonal_revenue(self, df: pl.DataFrame,
                             figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Сезонная выручка.
        
        Args:
            df: DataFrame с данными
            figsize: Размер фигуры
        """
        figsize = figsize or self.figsize
        
        if 'month' not in df.columns or 'revenue' not in df.columns:
            print("Необходимы колонки 'month' и 'revenue'")
            return
        
        # Группируем по месяцам
        monthly_revenue = df.group_by('month').agg([
            pl.col('revenue').sum().alias('total_revenue')
        ]).sort('month')
        
        fig, ax = plt.subplots(figsize=figsize)
        
        months = monthly_revenue['month'].to_list()
        revenues = monthly_revenue['total_revenue'].to_list()
        
        # Названия месяцев
        month_names = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
                      'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
        
        # Цвета по сезонам
        season_colors = {
            1: '#87CEEB', 2: '#87CEEB', 12: '#87CEEB',  # Зима - голубой
            3: '#98FB98', 4: '#98FB98', 5: '#98FB98',   # Весна - зеленый
            6: '#FFD700', 7: '#FFD700', 8: '#FFD700',   # Лето - желтый
            9: '#DEB887', 10: '#DEB887', 11: '#DEB887'  # Осень - коричневый
        }
        
        colors = [season_colors.get(m, BRAND_COLORS['primary']) for m in months]
        
        bars = ax.bar([month_names[m-1] for m in months], revenues, 
                     color=colors, alpha=0.8, edgecolor='white', linewidth=2)
        
        # Добавляем значения
        for bar, revenue in zip(bars, revenues):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(revenues) * 0.01,
                   f'${revenue/1e6:.1f}M', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('Сезонная выручка по месяцам', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Выручка ($)', fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


# Функции-обертки для быстрого использования
def plot_revenue_breakdown(revenue_data: Dict, **kwargs) -> None:
    """Быстрая функция для разбивки выручки."""
    visualizer = EconomicMetricsVisualizer()
    visualizer.plot_revenue_breakdown(revenue_data, **kwargs)


def plot_kpi_dashboard(kpis: Dict, **kwargs) -> None:
    """Быстрая функция для дашборда KPI."""
    visualizer = EconomicMetricsVisualizer()
    visualizer.plot_kpi_dashboard(kpis, **kwargs)


def plot_profitability_by_station(station_data: pl.DataFrame, **kwargs) -> None:
    """Быстрая функция для прибыльности станций."""
    visualizer = EconomicMetricsVisualizer()
    visualizer.plot_profitability_by_station(station_data, **kwargs)


def plot_user_type_comparison(user_metrics: pl.DataFrame, **kwargs) -> None:
    """Быстрая функция для сравнения пользователей."""
    visualizer = EconomicMetricsVisualizer()
    visualizer.plot_user_type_comparison(user_metrics, **kwargs)
