"""
SalesIQ Profitability Analytics Module
Enterprise-grade profitability analysis, margin analysis, and loss identification
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProfitabilityAnalytics:
    """
    Comprehensive profitability analytics engine
    Provides margin analysis, product profitability, and loss identification
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize profitability analytics
        
        Args:
            df: Sales data DataFrame
        """
        self.df = df.copy()
        self._validate_data()
    
    def _validate_data(self):
        """Validate required columns exist"""
        required_cols = ['Revenue', 'Cost', 'Profit']
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    def get_profitability_summary(self) -> Dict:
        """
        Calculate overall profitability metrics
        
        Returns:
            Dictionary of profitability metrics
        """
        try:
            total_revenue = self.df['Revenue'].sum()
            total_cost = self.df['Cost'].sum()
            total_profit = self.df['Profit'].sum()
            
            gross_profit = total_revenue - total_cost
            gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            net_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Calculate profit/loss distribution
            profitable_orders = len(self.df[self.df['Profit'] > 0])
            loss_orders = len(self.df[self.df['Profit'] < 0])
            break_even_orders = len(self.df[self.df['Profit'] == 0])
            total_orders = len(self.df)
            
            summary = {
                'total_revenue': round(total_revenue, 2),
                'total_cost': round(total_cost, 2),
                'total_profit': round(total_profit, 2),
                'gross_profit': round(gross_profit, 2),
                'gross_margin': round(gross_margin, 2),
                'net_margin': round(net_margin, 2),
                'profitable_orders': profitable_orders,
                'loss_orders': loss_orders,
                'break_even_orders': break_even_orders,
                'total_orders': total_orders,
                'profitability_rate': round((profitable_orders / total_orders * 100), 2) if total_orders > 0 else 0
            }
            
            logger.info("Profitability summary calculated")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to calculate profitability summary: {e}")
            raise
    
    def get_product_profitability(self) -> pd.DataFrame:
        """
        Analyze profitability by product
        
        Returns:
            DataFrame with product profitability metrics
        """
        try:
            if 'Product' not in self.df.columns:
                return pd.DataFrame()
            
            product_profit = self.df.groupby('Product').agg({
                'Revenue': 'sum',
                'Cost': 'sum',
                'Profit': 'sum',
                'Quantity': 'sum',
                'Order ID': 'count'
            }).reset_index()
            
            product_profit.columns = ['Product', 'Revenue', 'Cost', 'Profit',
                                     'Quantity', 'Order Count']
            
            product_profit['Profit Margin'] = (product_profit['Profit'] / product_profit['Revenue'] * 100).round(2)
            product_profit['Cost Ratio'] = (product_profit['Cost'] / product_profit['Revenue'] * 100).round(2)
            product_profit['Is Profitable'] = product_profit['Profit'] > 0
            product_profit['Profitability Status'] = product_profit['Is Profitable'].map({
                True: 'Profitable',
                False: 'Loss-Making'
            })
            
            product_profit = product_profit.sort_values('Profit', ascending=False)
            product_profit = product_profit.reset_index(drop=True)
            
            logger.info("Product profitability analysis completed")
            return product_profit
            
        except Exception as e:
            logger.error(f"Failed to analyze product profitability: {e}")
            raise
    
    def get_category_profitability(self) -> pd.DataFrame:
        """
        Analyze profitability by category
        
        Returns:
            DataFrame with category profitability metrics
        """
        try:
            if 'Category' not in self.df.columns:
                return pd.DataFrame()
            
            category_profit = self.df.groupby('Category').agg({
                'Revenue': 'sum',
                'Cost': 'sum',
                'Profit': 'sum',
                'Quantity': 'sum',
                'Order ID': 'count'
            }).reset_index()
            
            category_profit.columns = ['Category', 'Revenue', 'Cost', 'Profit',
                                       'Quantity', 'Order Count']
            
            category_profit['Profit Margin'] = (category_profit['Profit'] / category_profit['Revenue'] * 100).round(2)
            category_profit['Cost Ratio'] = (category_profit['Cost'] / category_profit['Revenue'] * 100).round(2)
            category_profit['Is Profitable'] = category_profit['Profit'] > 0
            
            category_profit = category_profit.sort_values('Profit', ascending=False)
            category_profit = category_profit.reset_index(drop=True)
            
            logger.info("Category profitability analysis completed")
            return category_profit
            
        except Exception as e:
            logger.error(f"Failed to analyze category profitability: {e}")
            raise
    
    def get_regional_profitability(self) -> pd.DataFrame:
        """
        Analyze profitability by region
        
        Returns:
            DataFrame with regional profitability metrics
        """
        try:
            if 'Region' not in self.df.columns:
                return pd.DataFrame()
            
            regional_profit = self.df.groupby('Region').agg({
                'Revenue': 'sum',
                'Cost': 'sum',
                'Profit': 'sum',
                'Quantity': 'sum',
                'Order ID': 'count'
            }).reset_index()
            
            regional_profit.columns = ['Region', 'Revenue', 'Cost', 'Profit',
                                       'Quantity', 'Order Count']
            
            regional_profit['Profit Margin'] = (regional_profit['Profit'] / regional_profit['Revenue'] * 100).round(2)
            regional_profit['Cost Ratio'] = (regional_profit['Cost'] / regional_profit['Revenue'] * 100).round(2)
            regional_profit['Is Profitable'] = regional_profit['Profit'] > 0
            
            regional_profit = regional_profit.sort_values('Profit', ascending=False)
            regional_profit = regional_profit.reset_index(drop=True)
            
            logger.info("Regional profitability analysis completed")
            return regional_profit
            
        except Exception as e:
            logger.error(f"Failed to analyze regional profitability: {e}")
            raise
    
    def identify_loss_making_products(self, threshold: float = 0) -> pd.DataFrame:
        """
        Identify loss-making products
        
        Args:
            threshold: Loss threshold (products with profit below this)
            
        Returns:
            DataFrame of loss-making products
        """
        try:
            if 'Product' not in self.df.columns:
                return pd.DataFrame()
            
            product_profit = self.get_product_profitability()
            loss_products = product_profit[product_profit['Profit'] < threshold]
            
            loss_products = loss_products.sort_values('Profit', ascending=True)
            loss_products = loss_products.reset_index(drop=True)
            
            logger.info(f"Identified {len(loss_products)} loss-making products")
            return loss_products
            
        except Exception as e:
            logger.error(f"Failed to identify loss-making products: {e}")
            raise
    
    def identify_loss_making_orders(self) -> pd.DataFrame:
        """
        Identify individual loss-making orders
        
        Returns:
            DataFrame of loss-making orders
        """
        try:
            loss_orders = self.df[self.df['Profit'] < 0].copy()
            
            if not loss_orders.empty:
                loss_orders = loss_orders.sort_values('Profit', ascending=True)
                loss_orders = loss_orders.reset_index(drop=True)
            
            logger.info(f"Identified {len(loss_orders)} loss-making orders")
            return loss_orders
            
        except Exception as e:
            logger.error(f"Failed to identify loss-making orders: {e}")
            raise
    
    def get_margin_distribution(self) -> Dict:
        """
        Analyze profit margin distribution
        
        Returns:
            Dictionary with margin distribution statistics
        """
        try:
            self.df['Profit Margin'] = (self.df['Profit'] / self.df['Revenue'] * 100).round(2)
            self.df['Profit Margin'] = self.df['Profit Margin'].fillna(0)
            
            margins = self.df['Profit Margin']
            
            distribution = {
                'mean_margin': round(margins.mean(), 2),
                'median_margin': round(margins.median(), 2),
                'std_margin': round(margins.std(), 2),
                'min_margin': round(margins.min(), 2),
                'max_margin': round(margins.max(), 2),
                'high_margin_orders': len(margins[margins > 30]),
                'medium_margin_orders': len(margins[(margins >= 10) & (margins <= 30)]),
                'low_margin_orders': len(margins[(margins >= 0) & (margins < 10)]),
                'negative_margin_orders': len(margins[margins < 0])
            }
            
            logger.info("Margin distribution analysis completed")
            return distribution
            
        except Exception as e:
            logger.error(f"Failed to analyze margin distribution: {e}")
            raise
    
    def get_profit_trends(self) -> pd.DataFrame:
        """
        Analyze profit trends over time
        
        Returns:
            DataFrame with profit trends
        """
        try:
            if 'Order Date' not in self.df.columns:
                return pd.DataFrame()
            
            if not pd.api.types.is_datetime64_any_dtype(self.df['Order Date']):
                self.df['Order Date'] = pd.to_datetime(self.df['Order Date'])
            
            self.df['YearMonth'] = self.df['Order Date'].dt.to_period('ME')
            
            profit_trends = self.df.groupby('YearMonth').agg({
                'Revenue': 'sum',
                'Cost': 'sum',
                'Profit': 'sum',
                'Order ID': 'count'
            }).reset_index()
            
            profit_trends.columns = ['YearMonth', 'Revenue', 'Cost', 'Profit', 'Orders']
            profit_trends['YearMonth'] = profit_trends['YearMonth'].astype(str)
            profit_trends['Profit Margin'] = (profit_trends['Profit'] / profit_trends['Revenue'] * 100).round(2)
            profit_trends['Cost Ratio'] = (profit_trends['Cost'] / profit_trends['Revenue'] * 100).round(2)
            
            # Calculate month-over-month profit growth
            profit_trends['Profit Growth'] = profit_trends['Profit'].pct_change() * 100
            profit_trends['Profit Growth'] = profit_trends['Profit Growth'].round(2)
            
            logger.info("Profit trends analysis completed")
            return profit_trends
            
        except Exception as e:
            logger.error(f"Failed to analyze profit trends: {e}")
            raise
    
    def get_cost_analysis(self) -> pd.DataFrame:
        """
        Analyze cost structure by category and product
        
        Returns:
            DataFrame with cost analysis
        """
        try:
            if 'Category' not in self.df.columns or 'Product' not in self.df.columns:
                return pd.DataFrame()
            
            cost_analysis = self.df.groupby(['Category', 'Product']).agg({
                'Revenue': 'sum',
                'Cost': 'sum',
                'Profit': 'sum',
                'Quantity': 'sum'
            }).reset_index()
            
            cost_analysis.columns = ['Category', 'Product', 'Revenue', 'Cost', 'Profit', 'Quantity']
            cost_analysis['Cost per Unit'] = (cost_analysis['Cost'] / cost_analysis['Quantity']).round(2)
            cost_analysis['Revenue per Unit'] = (cost_analysis['Revenue'] / cost_analysis['Quantity']).round(2)
            cost_analysis['Profit per Unit'] = (cost_analysis['Profit'] / cost_analysis['Quantity']).round(2)
            
            cost_analysis = cost_analysis.sort_values('Cost', ascending=False)
            cost_analysis = cost_analysis.reset_index(drop=True)
            
            logger.info("Cost analysis completed")
            return cost_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze costs: {e}")
            raise
    
    def get_profitability_recommendations(self) -> List[str]:
        """
        Generate profitability improvement recommendations
        
        Returns:
            List of recommendations
        """
        try:
            recommendations = []
            
            # Analyze loss-making products
            loss_products = self.identify_loss_making_products()
            if not loss_products.empty:
                top_loss_product = loss_products.iloc[0]
                recommendations.append(
                    f"Review pricing strategy for {top_loss_product['Product']} "
                    f"(loss: ${abs(top_loss_product['Profit']):,.2f})"
                )
            
            # Analyze low-margin categories
            if 'Category' in self.df.columns:
                category_profit = self.get_category_profitability()
                low_margin_categories = category_profit[category_profit['Profit Margin'] < 10]
                if not low_margin_categories.empty:
                    recommendations.append(
                        f"Consider optimizing {len(low_margin_categories)} low-margin categories "
                        f"(< 10% margin)"
                    )
            
            # Analyze cost structure
            summary = self.get_profitability_summary()
            cost_ratio = round((summary['total_cost'] / summary['total_revenue'] * 100), 2) if summary['total_revenue'] > 0 else 0
            if cost_ratio > 70:
                recommendations.append("High cost ratio detected (>70%). Review supply chain and procurement.")
            
            # Analyze loss order rate
            if summary['profitability_rate'] < 90:
                recommendations.append(
                    f"Improve order profitability (current rate: {summary['profitability_rate']:.1f}%)"
                )
            
            if not recommendations:
                recommendations.append("Profitability is healthy. Continue current strategies.")
            
            logger.info("Profitability recommendations generated")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            raise
