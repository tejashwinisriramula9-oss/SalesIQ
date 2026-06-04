"""
SalesIQ Sales Analytics Module
Enterprise-grade sales performance analytics and insights
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SalesAnalytics:
    """
    Comprehensive sales analytics engine
    Provides revenue, product, regional, and trend analysis
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize sales analytics
        
        Args:
            df: Sales data DataFrame
        """
        self.df = df.copy()
        self._validate_data()
    
    def _validate_data(self):
        """Validate required columns exist"""
        required_cols = ['Order Date', 'Revenue', 'Profit']
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(self.df['Order Date']):
            self.df['Order Date'] = pd.to_datetime(self.df['Order Date'])
    
    def get_kpi_metrics(self) -> Dict:
        """
        Calculate key performance indicators
        
        Returns:
            Dictionary of KPI metrics
        """
        try:
            total_revenue = self.df['Revenue'].sum()
            total_profit = self.df['Profit'].sum()
            total_orders = len(self.df)
            unique_customers = self.df['Customer ID'].nunique() if 'Customer ID' in self.df.columns else 0
            
            # Calculate growth rates (compare with previous period)
            if 'Order Date' in self.df.columns:
                latest_date = self.df['Order Date'].max()
                previous_period_start = latest_date - timedelta(days=30)
                
                current_period = self.df[self.df['Order Date'] >= previous_period_start]
                previous_period = self.df[self.df['Order Date'] < previous_period_start]
                
                current_revenue = current_period['Revenue'].sum()
                previous_revenue = previous_period['Revenue'].sum()
                
                revenue_growth = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
                
                current_profit = current_period['Profit'].sum()
                previous_profit = previous_period['Profit'].sum()
                
                profit_growth = ((current_profit - previous_profit) / previous_profit * 100) if previous_profit > 0 else 0
            else:
                revenue_growth = 0
                profit_growth = 0
            
            kpis = {
                'total_revenue': round(total_revenue, 2),
                'total_profit': round(total_profit, 2),
                'total_orders': total_orders,
                'total_customers': unique_customers,
                'revenue_growth': round(revenue_growth, 2),
                'profit_growth': round(profit_growth, 2),
                'avg_order_value': round(total_revenue / total_orders, 2) if total_orders > 0 else 0,
                'profit_margin': round((total_profit / total_revenue * 100), 2) if total_revenue > 0 else 0
            }
            
            logger.info("KPI metrics calculated successfully")
            return kpis
            
        except Exception as e:
            logger.error(f"Failed to calculate KPI metrics: {e}")
            raise
    
    def get_top_products(self, n: int = 10, metric: str = 'Revenue') -> pd.DataFrame:
        """
        Get top performing products
        
        Args:
            n: Number of top products to return
            metric: Metric to rank by (Revenue, Profit, Quantity)
            
        Returns:
            DataFrame of top products
        """
        try:
            if 'Product' not in self.df.columns:
                return pd.DataFrame()
            
            metric_col = metric if metric in self.df.columns else 'Revenue'
            
            product_stats = self.df.groupby('Product').agg({
                'Revenue': 'sum',
                'Profit': 'sum',
                'Quantity': 'sum'
            }).reset_index()
            
            product_stats = product_stats.sort_values(by=metric_col, ascending=False).head(n)
            product_stats = product_stats.reset_index(drop=True)
            
            logger.info(f"Top {n} products by {metric} retrieved")
            return product_stats
            
        except Exception as e:
            logger.error(f"Failed to get top products: {e}")
            raise
    
    def get_top_categories(self, n: int = 10, metric: str = 'Revenue') -> pd.DataFrame:
        """
        Get top performing categories
        
        Args:
            n: Number of top categories to return
            metric: Metric to rank by (Revenue, Profit, Quantity)
            
        Returns:
            DataFrame of top categories
        """
        try:
            if 'Category' not in self.df.columns:
                return pd.DataFrame()
            
            metric_col = metric if metric in self.df.columns else 'Revenue'
            
            category_stats = self.df.groupby('Category').agg({
                'Revenue': 'sum',
                'Profit': 'sum',
                'Quantity': 'sum'
            }).reset_index()
            
            category_stats = category_stats.sort_values(by=metric_col, ascending=False).head(n)
            category_stats = category_stats.reset_index(drop=True)
            
            logger.info(f"Top {n} categories by {metric} retrieved")
            return category_stats
            
        except Exception as e:
            logger.error(f"Failed to get top categories: {e}")
            raise
    
    def get_regional_performance(self) -> pd.DataFrame:
        """
        Get regional performance analysis
        
        Returns:
            DataFrame of regional performance
        """
        try:
            if 'Region' not in self.df.columns:
                return pd.DataFrame()
            
            regional_stats = self.df.groupby('Region').agg({
                'Revenue': 'sum',
                'Profit': 'sum',
                'Quantity': 'sum',
                'Order ID': 'count'
            }).rename(columns={'Order ID': 'Orders'}).reset_index()
            
            regional_stats['ProfitMargin'] = (regional_stats['Profit'] / regional_stats['Revenue'] * 100).round(2)
            regional_stats = regional_stats.sort_values(by='Revenue', ascending=False)
            regional_stats = regional_stats.reset_index(drop=True)
            
            logger.info("Regional performance analysis completed")
            return regional_stats
            
        except Exception as e:
            logger.error(f"Failed to get regional performance: {e}")
            raise
    
    def get_monthly_trends(self) -> pd.DataFrame:
        """
        Get monthly sales trends
        
        Returns:
            DataFrame of monthly trends
        """
        try:
            if 'Order Date' not in self.df.columns:
                return pd.DataFrame()
            
            self.df['YearMonth'] = self.df['Order Date'].dt.to_period('ME')
            
            monthly_stats = self.df.groupby('YearMonth').agg({
                'Revenue': 'sum',
                'Profit': 'sum',
                'Quantity': 'sum',
                'Order ID': 'count'
            }).rename(columns={'Order ID': 'Orders'}).reset_index()
            
            monthly_stats['YearMonth'] = monthly_stats['YearMonth'].astype(str)
            monthly_stats['ProfitMargin'] = (monthly_stats['Profit'] / monthly_stats['Revenue'] * 100).round(2)
            
            # Calculate month-over-month growth
            monthly_stats['RevenueGrowth'] = monthly_stats['Revenue'].pct_change() * 100
            monthly_stats['RevenueGrowth'] = monthly_stats['RevenueGrowth'].round(2)
            
            logger.info("Monthly trends analysis completed")
            return monthly_stats
            
        except Exception as e:
            logger.error(f"Failed to get monthly trends: {e}")
            raise
    
    def get_quarterly_trends(self) -> pd.DataFrame:
        """
        Get quarterly sales trends
        
        Returns:
            DataFrame of quarterly trends
        """
        try:
            if 'Order Date' not in self.df.columns:
                return pd.DataFrame()
            
            self.df['YearQuarter'] = self.df['Order Date'].dt.to_period('Q')
            
            quarterly_stats = self.df.groupby('YearQuarter').agg({
                'Revenue': 'sum',
                'Profit': 'sum',
                'Quantity': 'sum',
                'Order ID': 'count'
            }).rename(columns={'Order ID': 'Orders'}).reset_index()
            
            quarterly_stats['YearQuarter'] = quarterly_stats['YearQuarter'].astype(str)
            quarterly_stats['ProfitMargin'] = (quarterly_stats['Profit'] / quarterly_stats['Revenue'] * 100).round(2)
            
            logger.info("Quarterly trends analysis completed")
            return quarterly_stats
            
        except Exception as e:
            logger.error(f"Failed to get quarterly trends: {e}")
            raise
    
    def get_revenue_heatmap_data(self) -> pd.DataFrame:
        """
        Get data for revenue heatmap (region x category)
        
        Returns:
            DataFrame for heatmap visualization
        """
        try:
            if 'Region' not in self.df.columns or 'Category' not in self.df.columns:
                return pd.DataFrame()
            
            heatmap_data = self.df.pivot_table(
                values='Revenue',
                index='Region',
                columns='Category',
                aggfunc='sum',
                fill_value=0
            )
            
            logger.info("Revenue heatmap data prepared")
            return heatmap_data
            
        except Exception as e:
            logger.error(f"Failed to generate heatmap data: {e}")
            raise
    
    def get_product_category_matrix(self) -> pd.DataFrame:
        """
        Get product-category relationship matrix
        
        Returns:
            DataFrame showing product distribution across categories
        """
        try:
            if 'Product' not in self.df.columns or 'Category' not in self.df.columns:
                return pd.DataFrame()
            
            matrix = self.df.groupby(['Category', 'Product']).agg({
                'Revenue': 'sum',
                'Quantity': 'sum'
            }).reset_index()
            
            matrix = matrix.sort_values(['Category', 'Revenue'], ascending=[True, False])
            
            logger.info("Product-category matrix generated")
            return matrix
            
        except Exception as e:
            logger.error(f"Failed to generate product-category matrix: {e}")
            raise
    
    def get_sales_velocity(self) -> pd.DataFrame:
        """
        Calculate sales velocity metrics
        
        Returns:
            DataFrame with sales velocity indicators
        """
        try:
            if 'Order Date' not in self.df.columns:
                return pd.DataFrame()
            
            # Calculate days between orders
            self.df = self.df.sort_values('Order Date')
            
            if 'Customer ID' in self.df.columns:
                customer_velocity = self.df.groupby('Customer ID').agg({
                    'Order Date': ['min', 'max', 'count'],
                    'Revenue': 'sum'
                }).reset_index()
                
                customer_velocity.columns = ['Customer ID', 'First Order', 'Last Order', 'Order Count', 'Total Revenue']
                customer_velocity['Days Active'] = (customer_velocity['Last Order'] - customer_velocity['First Order']).dt.days + 1
                customer_velocity['Orders Per Month'] = (customer_velocity['Order Count'] / (customer_velocity['Days Active'] / 30)).round(2)
                
                logger.info("Sales velocity analysis completed")
                return customer_velocity
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Failed to calculate sales velocity: {e}")
            raise
