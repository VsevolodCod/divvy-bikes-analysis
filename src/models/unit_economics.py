"""Модель юнит-экономики велопроката."""


class UnitEconomicsModel:
    """
    Расчет юнит-экономики Divvy Bikes:
    - Выручка на поездку
    - Стоимость обслуживания
    - Маржинальность
    - ROI по станциям
    """
    
    def __init__(self, pricing_params, cost_params):
        self.pricing = pricing_params
        self.costs = cost_params
    
    def calculate_revenue(self, trips_df):
        """Расчет выручки."""
        pass
    
    def calculate_costs(self, trips_df):
        """Расчет операционных затрат."""
        pass
    
    def calculate_profit(self, trips_df):
        """Расчет прибыли."""
        pass
