"""Модель юнит-экономики велопроката Divvy."""

import polars as pl
from typing import Dict, Tuple, Optional
from datetime import datetime
import numpy as np


class UnitEconomicsModel:
    """Модель для расчета юнит-экономики велопроката."""
    
    def __init__(self):
        """Инициализация модели с тарифными сетками."""
        self.pricing_rules = self._load_pricing_rules()
    
    def _load_pricing_rules(self) -> Dict:
        """Загружает тарифные сетки по годам."""
        return {
            2020: {
                'casual': {
                    'classic_bike': {'unlock_fee': 2.50, 'per_minute': 0.125, 'free_minutes': 0},
                    'electric_bike': {'unlock_fee': 3.00, 'per_minute': 0.185, 'free_minutes': 0}
                },
                'member': {
                    'classic_bike': {'unlock_fee': 0.00, 'per_minute': 0.126, 'free_minutes': 60},
                    'electric_bike': {'unlock_fee': 0.00, 'per_minute': 0.154, 'free_minutes': 45}
                }
            },
            2021: {
                'casual': {
                    'classic_bike': {'unlock_fee': 2.80, 'per_minute': 0.135, 'free_minutes': 0},
                    'electric_bike': {'unlock_fee': 3.20, 'per_minute': 0.195, 'free_minutes': 0}
                },
                'member': {
                    'classic_bike': {'unlock_fee': 0.00, 'per_minute': 0.136, 'free_minutes': 60},
                    'electric_bike': {'unlock_fee': 0.00, 'per_minute': 0.164, 'free_minutes': 45}
                }
            },
            2022: {
                'casual': {
                    'classic_bike': {'unlock_fee': 0.90, 'per_minute': 0.141, 'free_minutes': 10},
                    'electric_bike': {'unlock_fee': 1.00, 'per_minute': 0.355, 'free_minutes': 5}
                },
                'member': {
                    'classic_bike': {'unlock_fee': 0.00, 'per_minute': 0.146, 'free_minutes': 60},
                    'electric_bike': {'unlock_fee': 0.00, 'per_minute': 0.143, 'free_minutes': 30}
                }
            },
            2023: {
                'casual': {
                    'classic_bike': {'unlock_fee': 0.90, 'per_minute': 0.151, 'free_minutes': 10},
                    'electric_bike': {'unlock_fee': 1.00, 'per_minute': 0.385, 'free_minutes': 5}
                },
                'member': {
                    'classic_bike': {'unlock_fee': 0.00, 'per_minute': 0.156, 'free_minutes': 60},
                    'electric_bike': {'unlock_fee': 0.00, 'per_minute': 0.153, 'free_minutes': 30}
                }
            },
            2024: {
                'casual': {
                    'classic_bike': {'unlock_fee': 0.90, 'per_minute': 0.161, 'free_minutes': 10},
                    'electric_bike': {'unlock_fee': 1.00, 'per_minute': 0.405, 'free_minutes': 5}
                },
                'member': {
                    'classic_bike': {'unlock_fee': 0.00, 'per_minute': 0.166, 'free_minutes': 60},
                    'electric_bike': {'unlock_fee': 0.00, 'per_minute': 0.163, 'free_minutes': 30}
                }
            },
            2025: {
                'casual': {
                    'classic_bike': {'unlock_fee': 0.90, 'per_minute': 0.171, 'free_minutes': 10},
                    'electric_bike': {'unlock_fee': 1.00, 'per_minute': 0.425, 'free_minutes': 5}
                },
                'member': {
                    'classic_bike': {'unlock_fee': 0.00, 'per_minute': 0.176, 'free_minutes': 60},
                    'electric_bike': {'unlock_fee': 0.00, 'per_minute': 0.173, 'free_minutes': 30}
                }
            }
        }
    
    def calculate_ride_cost(self, duration_minutes: float, user_type: str, 
                           bike_type: str, year: int) -> float:
        """Рассчитывает стоимость поездки."""
        if year not in self.pricing_rules:
            year = 2025  # Используем последние тарифы
        
        # Нормализуем типы
        user_type = 'casual' if user_type == 'casual' else 'member'
        bike_type = 'electric_bike' if 'electric' in bike_type.lower() else 'classic_bike'
        
        pricing = self.pricing_rules[year][user_type][bike_type]
        
        unlock_fee = pricing['unlock_fee']
        per_minute = pricing['per_minute']
        free_minutes = pricing['free_minutes']
        
        if duration_minutes <= free_minutes:
            return unlock_fee
        else:
            return unlock_fee + (duration_minutes - free_minutes) * per_minute
    
    def calculate_revenue_metrics(self, df: pl.DataFrame) -> Dict:
        """Рассчитывает основные метрики выручки."""
        # Добавляем стоимость поездок
        df_with_cost = df.with_columns([
            pl.struct(['duration_minutes', 'member_casual', 'rideable_type', 'year'])
            .map_elements(lambda x: self.calculate_ride_cost(
                x['duration_minutes'], x['member_casual'], x['rideable_type'], x['year']
            ), return_dtype=pl.Float64)
            .alias('ride_cost')
        ])
        
        # Базовые метрики
        total_rides = df_with_cost.height
        total_revenue = df_with_cost['ride_cost'].sum()
        avg_ride_cost = df_with_cost['ride_cost'].mean()
        
        # Метрики по типам пользователей
        user_metrics = df_with_cost.group_by('member_casual').agg([
            pl.count().alias('rides'),
            pl.col('ride_cost').sum().alias('revenue'),
            pl.col('ride_cost').mean().alias('avg_cost')
        ])
        
        # Метрики по типам велосипедов
        bike_metrics = df_with_cost.group_by('rideable_type').agg([
            pl.count().alias('rides'),
            pl.col('ride_cost').sum().alias('revenue'),
            pl.col('ride_cost').mean().alias('avg_cost')
        ])
        
        return {
            'total_rides': total_rides,
            'total_revenue': total_revenue,
            'avg_ride_cost': avg_ride_cost,
            'user_metrics': user_metrics,
            'bike_metrics': bike_metrics
        }
    
    def calculate_subscription_revenue(self, df: pl.DataFrame) -> Dict:
        """Рассчитывает выручку от подписок."""
        # Подписка стоит $15/месяц
        monthly_subscription_fee = 15.0
        
        # Считаем уникальных member пользователей по месяцам
        member_df = df.filter(pl.col('member_casual') == 'member')
        
        # Группируем по годам и месяцам
        monthly_members = member_df.group_by(['year', 'month']).agg([
            pl.col('ride_id').n_unique().alias('unique_members_approx')
        ])
        
        # Приблизительная оценка подписчиков (60% от активных пользователей)
        subscription_revenue = (monthly_members['unique_members_approx'].sum() * 
                              monthly_subscription_fee * 0.6)
        
        return {
            'subscription_revenue': subscription_revenue,
            'monthly_subscription_fee': monthly_subscription_fee,
            'estimated_subscribers': monthly_members['unique_members_approx'].sum() * 0.6
        }
    
    def calculate_kpis(self, df: pl.DataFrame) -> Dict:
        """Рассчитывает ключевые показатели эффективности."""
        revenue_metrics = self.calculate_revenue_metrics(df)
        subscription_metrics = self.calculate_subscription_revenue(df)
        
        # ARPU (Average Revenue Per User)
        total_users = df['ride_id'].n_unique()  # Приблизительно
        total_revenue = revenue_metrics['total_revenue'] + subscription_metrics['subscription_revenue']
        arpu = total_revenue / total_users if total_users > 0 else 0
        
        # Валовая маржа (предполагаем 96% как в презентации)
        gross_margin = 0.96
        
        # LTV (упрощенная оценка)
        avg_monthly_revenue_per_user = arpu
        avg_customer_lifetime_months = 40  # Предположение
        ltv = avg_monthly_revenue_per_user * avg_customer_lifetime_months
        
        # CAC (предположение на основе индустрии)
        cac = 40.0
        
        # ROI
        roi = (ltv - cac) / cac * 100 if cac > 0 else 0
        
        return {
            'arpu': arpu,
            'ltv': ltv,
            'cac': cac,
            'roi': roi,
            'gross_margin': gross_margin,
            'ltv_cac_ratio': ltv / cac if cac > 0 else 0,
            'total_revenue': total_revenue,
            'ride_revenue': revenue_metrics['total_revenue'],
            'subscription_revenue': subscription_metrics['subscription_revenue']
        }
