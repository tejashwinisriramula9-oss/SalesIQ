"""
SalesIQ Forecasting Module
Enterprise-grade ML forecasting models for sales prediction
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SalesForecaster:
    """
    Enterprise sales forecasting engine
    Uses Linear Regression and Random Forest for predictions
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize sales forecaster
        
        Args:
            df: Sales data DataFrame
        """
        self.df = df.copy()
        self.lr_model = None
        self.rf_model = None
        self.feature_columns = []
        self._validate_data()
    
    def _validate_data(self):
        """Validate required columns exist"""
        required_cols = ['Order Date', 'Revenue']
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(self.df['Order Date']):
            self.df['Order Date'] = pd.to_datetime(self.df['Order Date'])
    
    def prepare_time_series_data(self) -> pd.DataFrame:
        """
        Prepare time series data for forecasting
        
        Returns:
            DataFrame with time series features
        """
        try:
            # Aggregate data by month
            self.df['YearMonth'] = self.df['Order Date'].dt.to_period('ME')
            
            monthly_data = self.df.groupby('YearMonth').agg({
                'Revenue': 'sum',
                'Profit': 'sum',
                'Quantity': 'sum',
                'Order ID': 'count'
            }).reset_index()
            
            monthly_data.columns = ['YearMonth', 'Revenue', 'Profit', 'Quantity', 'Orders']
            monthly_data['YearMonth'] = monthly_data['YearMonth'].astype(str)
            
            # Create time-based features
            monthly_data['Month_Num'] = pd.to_datetime(monthly_data['YearMonth']).dt.month
            monthly_data['Year_Num'] = pd.to_datetime(monthly_data['YearMonth']).dt.year
            monthly_data['Quarter'] = pd.to_datetime(monthly_data['YearMonth']).dt.quarter
            
            # Create lag features
            monthly_data['Revenue_Lag1'] = monthly_data['Revenue'].shift(1)
            monthly_data['Revenue_Lag2'] = monthly_data['Revenue'].shift(2)
            monthly_data['Revenue_Lag3'] = monthly_data['Revenue'].shift(3)
            
            # Create moving average features
            monthly_data['Revenue_MA3'] = monthly_data['Revenue'].rolling(window=3).mean()
            monthly_data['Revenue_MA6'] = monthly_data['Revenue'].rolling(window=6).mean()
            
            # Drop rows with NaN values (from lag/rolling features)
            monthly_data = monthly_data.dropna()
            
            # Define feature columns
            self.feature_columns = ['Month_Num', 'Year_Num', 'Quarter',
                                   'Revenue_Lag1', 'Revenue_Lag2', 'Revenue_Lag3',
                                   'Revenue_MA3', 'Revenue_MA6']
            
            logger.info("Time series data prepared for forecasting")
            return monthly_data
            
        except Exception as e:
            logger.error(f"Failed to prepare time series data: {e}")
            raise
    
    def train_linear_regression(self, data: pd.DataFrame) -> Dict:
        """
        Train Linear Regression model
        
        Args:
            data: Prepared time series data
            
        Returns:
            Dictionary with model performance metrics
        """
        try:
            # Prepare features and target
            X = data[self.feature_columns]
            y = data['Revenue']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            # Train model
            self.lr_model = LinearRegression()
            self.lr_model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = self.lr_model.predict(X_test)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)
            
            metrics = {
                'model_type': 'Linear Regression',
                'mae': float(round(mae, 2)),
                'mse': float(round(mse, 2)),
                'rmse': float(round(rmse, 2)),
                'r2_score': float(round(r2, 4)),
                'feature_importance': {k: float(v) for k, v in zip(self.feature_columns, self.lr_model.coef_)}
            }
            
            logger.info(f"Linear Regression trained - R2: {r2:.4f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to train Linear Regression: {e}")
            raise
    
    def train_random_forest(self, data: pd.DataFrame) -> Dict:
        """
        Train Random Forest Regressor model
        
        Args:
            data: Prepared time series data
            
        Returns:
            Dictionary with model performance metrics
        """
        try:
            # Prepare features and target
            X = data[self.feature_columns]
            y = data['Revenue']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            # Train model
            self.rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.rf_model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = self.rf_model.predict(X_test)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)
            
            # Feature importance
            feature_importance = dict(zip(self.feature_columns, self.rf_model.feature_importances_))
            
            metrics = {
                'model_type': 'Random Forest',
                'mae': float(round(mae, 2)),
                'mse': float(round(mse, 2)),
                'rmse': float(round(rmse, 2)),
                'r2_score': float(round(r2, 4)),
                'feature_importance': {k: float(v) for k, v in zip(self.feature_columns, self.rf_model.feature_importances_)}
            }
            
            logger.info(f"Random Forest trained - R2: {r2:.4f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to train Random Forest: {e}")
            raise
    
    def forecast_next_month(self, model: str = 'rf') -> Dict:
        """
        Forecast revenue for next month
        
        Args:
            model: Model to use ('lr' for Linear Regression, 'rf' for Random Forest)
            
        Returns:
            Dictionary with forecast results
        """
        try:
            data = self.prepare_time_series_data()
            
            # Select model
            if model == 'lr':
                if self.lr_model is None:
                    self.train_linear_regression(data)
                model_obj = self.lr_model
            else:
                if self.rf_model is None:
                    self.train_random_forest(data)
                model_obj = self.rf_model
            
            # Get last month data
            last_row = data.iloc[-1].copy()
            
            # Create next month features
            next_month_num = last_row['Month_Num'] % 12 + 1
            next_year_num = last_row['Year_Num'] + (1 if next_month_num == 1 else 0)
            next_quarter = (next_month_num - 1) // 3 + 1
            
            next_features = pd.DataFrame({
                'Month_Num': [next_month_num],
                'Year_Num': [next_year_num],
                'Quarter': [next_quarter],
                'Revenue_Lag1': [last_row['Revenue']],
                'Revenue_Lag2': [last_row['Revenue_Lag1']],
                'Revenue_Lag3': [last_row['Revenue_Lag2']],
                'Revenue_MA3': [last_row['Revenue_MA3']],
                'Revenue_MA6': [last_row['Revenue_MA6']]
            })
            
            # Make prediction
            forecast = model_obj.predict(next_features[self.feature_columns])[0]
            
            # Calculate confidence interval (simplified)
            forecast_std = data['Revenue'].std()
            confidence_lower = forecast - 1.96 * forecast_std
            confidence_upper = forecast + 1.96 * forecast_std
            
            result = {
                'forecast_period': f"{int(next_year_num)}-{int(next_month_num):02d}",
                'forecast_value': float(round(float(forecast), 2)),
                'confidence_lower': float(round(float(confidence_lower), 2)),
                'confidence_upper': float(round(float(confidence_upper), 2)),
                'model_used': 'Linear Regression' if model == 'lr' else 'Random Forest',
                'last_actual_value': float(round(float(last_row['Revenue']), 2)),
                'growth_rate': float(round(float((forecast - last_row['Revenue']) / last_row['Revenue'] * 100), 2)) if float(last_row['Revenue']) != 0 else 0.0
            }
            
            logger.info(f"Next month forecast: {forecast:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to forecast next month: {e}")
            raise
    
    def forecast_quarter(self, model: str = 'rf') -> List[Dict]:
        """
        Forecast revenue for next quarter (3 months)
        
        Args:
            model: Model to use ('lr' for Linear Regression, 'rf' for Random Forest)
            
        Returns:
            List of forecast results for each month
        """
        try:
            forecasts = []
            data = self.prepare_time_series_data()
            
            # Select model
            if model == 'lr':
                if self.lr_model is None:
                    self.train_linear_regression(data)
                model_obj = self.lr_model
            else:
                if self.rf_model is None:
                    self.train_random_forest(data)
                model_obj = self.rf_model
            
            # Get last month data
            last_row = data.iloc[-1].copy()
            
            # Forecast 3 months ahead
            for i in range(1, 4):
                next_month_num = (last_row['Month_Num'] + i - 1) % 12 + 1
                next_year_num = last_row['Year_Num'] + (1 if next_month_num < last_row['Month_Num'] else 0)
                next_quarter = (next_month_num - 1) // 3 + 1
                
                next_features = pd.DataFrame({
                    'Month_Num': [next_month_num],
                    'Year_Num': [next_year_num],
                    'Quarter': [next_quarter],
                    'Revenue_Lag1': [last_row['Revenue']],
                    'Revenue_Lag2': [last_row['Revenue_Lag1']],
                    'Revenue_Lag3': [last_row['Revenue_Lag2']],
                    'Revenue_MA3': [last_row['Revenue_MA3']],
                    'Revenue_MA6': [last_row['Revenue_MA6']]
                })
                
                forecast = model_obj.predict(next_features[self.feature_columns])[0]
                
                forecasts.append({
                    'forecast_period': f"{int(next_year_num)}-{int(next_month_num):02d}",
                    'forecast_value': float(round(float(forecast), 2)),
                    'model_used': 'Linear Regression' if model == 'lr' else 'Random Forest'
                })
            
            logger.info("Quarterly forecast completed")
            return forecasts
            
        except Exception as e:
            logger.error(f"Failed to forecast quarter: {e}")
            raise
    
    def forecast_year(self, model: str = 'rf') -> List[Dict]:
        """
        Forecast revenue for next year (12 months)
        
        Args:
            model: Model to use ('lr' for Linear Regression, 'rf' for Random Forest)
            
        Returns:
            List of forecast results for each month
        """
        try:
            forecasts = []
            data = self.prepare_time_series_data()
            
            # Select model
            if model == 'lr':
                if self.lr_model is None:
                    self.train_linear_regression(data)
                model_obj = self.lr_model
            else:
                if self.rf_model is None:
                    self.train_random_forest(data)
                model_obj = self.rf_model
            
            # Get last month data
            last_row = data.iloc[-1].copy()
            
            # Forecast 12 months ahead
            for i in range(1, 13):
                next_month_num = (last_row['Month_Num'] + i - 1) % 12 + 1
                next_year_num = last_row['Year_Num'] + (1 if next_month_num < last_row['Month_Num'] else 0)
                next_quarter = (next_month_num - 1) // 3 + 1
                
                next_features = pd.DataFrame({
                    'Month_Num': [next_month_num],
                    'Year_Num': [next_year_num],
                    'Quarter': [next_quarter],
                    'Revenue_Lag1': [last_row['Revenue']],
                    'Revenue_Lag2': [last_row['Revenue_Lag1']],
                    'Revenue_Lag3': [last_row['Revenue_Lag2']],
                    'Revenue_MA3': [last_row['Revenue_MA3']],
                    'Revenue_MA6': [last_row['Revenue_MA6']]
                })
                
                forecast = model_obj.predict(next_features[self.feature_columns])[0]
                
                forecasts.append({
                    'forecast_period': f"{int(next_year_num)}-{int(next_month_num):02d}",
                    'forecast_value': float(round(float(forecast), 2)),
                    'model_used': 'Linear Regression' if model == 'lr' else 'Random Forest'
                })
            
            logger.info("Yearly forecast completed")
            return forecasts
            
        except Exception as e:
            logger.error(f"Failed to forecast year: {e}")
            raise
    
    def get_model_comparison(self) -> Dict:
        """
        Compare Linear Regression and Random Forest models
        
        Returns:
            Dictionary with model comparison metrics
        """
        try:
            data = self.prepare_time_series_data()
            
            # Train both models
            lr_metrics = self.train_linear_regression(data)
            rf_metrics = self.train_random_forest(data)
            
            comparison = {
                'linear_regression': lr_metrics,
                'random_forest': rf_metrics,
                'recommended_model': 'Random Forest' if rf_metrics['r2_score'] > lr_metrics['r2_score'] else 'Linear Regression'
            }
            
            logger.info("Model comparison completed")
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare models: {e}")
            raise
