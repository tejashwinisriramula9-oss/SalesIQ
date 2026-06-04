"""
SalesIQ AI Insights Engine
Enterprise-grade AI-powered business insights generation
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsightsEngine:
    """
    AI-powered insights generation engine
    Analyzes data patterns and generates actionable business insights
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize insights engine
        
        Args:
            df: Sales data DataFrame
        """
        self.df = df.copy()
        self.insights = []
        self._validate_data()
    
    def _validate_data(self):
        """Validate required columns exist"""
        required_cols = ['Revenue', 'Order Date']
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        if not pd.api.types.is_datetime64_any_dtype(self.df['Order Date']):
            self.df['Order Date'] = pd.to_datetime(self.df['Order Date'])
    
    def generate_all_insights(self) -> List[Dict]:
        """
        Generate comprehensive business insights
        
        Returns:
            List of insight dictionaries
        """
        try:
            self.insights = []
            
            # Revenue insights
            self._generate_revenue_insights()
            
            # Growth insights
            self._generate_growth_insights()
            
            # Product insights
            self._generate_product_insights()
            
            # Regional insights
            self._generate_regional_insights()
            
            # Profitability insights
            self._generate_profitability_insights()
            
            # Customer insights
            self._generate_customer_insights()
            
            # Seasonal insights
            self._generate_seasonal_insights()
            
            logger.info(f"Generated {len(self.insights)} business insights")
            return self.insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            raise
    
    def _generate_revenue_insights(self):
        """Generate revenue-related insights"""
        try:
            total_revenue = self.df['Revenue'].sum()
            avg_revenue = self.df['Revenue'].mean()
            
            # Revenue trend
            self.df['YearMonth'] = self.df['Order Date'].dt.to_period('ME')
            monthly_revenue = self.df.groupby('YearMonth')['Revenue'].sum()
            
            if len(monthly_revenue) >= 2:
                recent_growth = (monthly_revenue.iloc[-1] - monthly_revenue.iloc[-2]) / monthly_revenue.iloc[-2] * 100
                
                if recent_growth > 10:
                    self.insights.append({
                        'type': 'Revenue',
                        'category': 'Growth',
                        'insight': f"Revenue increased by {recent_growth:.1f}% compared to previous month",
                        'impact': 'High',
                        'actionable': True
                    })
                elif recent_growth < -10:
                    self.insights.append({
                        'type': 'Revenue',
                        'category': 'Warning',
                        'insight': f"Revenue decreased by {abs(recent_growth):.1f}% compared to previous month",
                        'impact': 'High',
                        'actionable': True
                    })
            
            # Total revenue milestone
            if total_revenue > 1000000:
                self.insights.append({
                    'type': 'Revenue',
                    'category': 'Achievement',
                    'insight': f"Total revenue exceeds ${total_revenue/1000000:.1f}M milestone",
                    'impact': 'Medium',
                    'actionable': False
                })
            
        except Exception as e:
            logger.error(f"Failed to generate revenue insights: {e}")
    
    def _generate_growth_insights(self):
        """Generate growth-related insights"""
        try:
            # Calculate quarter-over-quarter growth
            self.df['Quarter'] = self.df['Order Date'].dt.to_period('Q')
            quarterly_revenue = self.df.groupby('Quarter')['Revenue'].sum()
            
            if len(quarterly_revenue) >= 2:
                qoq_growth = (quarterly_revenue.iloc[-1] - quarterly_revenue.iloc[-2]) / quarterly_revenue.iloc[-2] * 100
                
                if qoq_growth > 0:
                    self.insights.append({
                        'type': 'Growth',
                        'category': 'Quarterly',
                        'insight': f"Quarter-over-quarter revenue growth: {qoq_growth:.1f}%",
                        'impact': 'High',
                        'actionable': True
                    })
            
            # Year-over-year growth
            self.df['Year'] = self.df['Order Date'].dt.year
            yearly_revenue = self.df.groupby('Year')['Revenue'].sum()
            
            if len(yearly_revenue) >= 2:
                yoy_growth = (yearly_revenue.iloc[-1] - yearly_revenue.iloc[-2]) / yearly_revenue.iloc[-2] * 100
                
                self.insights.append({
                    'type': 'Growth',
                    'category': 'Yearly',
                    'insight': f"Year-over-year revenue growth: {yoy_growth:.1f}%",
                    'impact': 'High',
                    'actionable': True
                })
            
        except Exception as e:
            logger.error(f"Failed to generate growth insights: {e}")
    
    def _generate_product_insights(self):
        """Generate product-related insights"""
        try:
            if 'Product' not in self.df.columns:
                return
            
            # Top product
            product_revenue = self.df.groupby('Product')['Revenue'].sum().sort_values(ascending=False)
            if not product_revenue.empty:
                top_product = product_revenue.index[0]
                top_product_revenue = product_revenue.iloc[0]
                total_revenue = self.df['Revenue'].sum()
                contribution = (top_product_revenue / total_revenue * 100)
                
                self.insights.append({
                    'type': 'Product',
                    'category': 'Performance',
                    'insight': f"'{top_product}' is the top performer contributing {contribution:.1f}% of total revenue",
                    'impact': 'High',
                    'actionable': True
                })
            
            # Product concentration risk
            if len(product_revenue) > 0:
                top_3_contribution = (product_revenue.head(3).sum() / total_revenue * 100)
                if top_3_contribution > 70:
                    self.insights.append({
                        'type': 'Product',
                        'category': 'Risk',
                        'insight': f"Top 3 products contribute {top_3_contribution:.1f}% of revenue - consider diversification",
                        'impact': 'Medium',
                        'actionable': True
                    })
            
        except Exception as e:
            logger.error(f"Failed to generate product insights: {e}")
    
    def _generate_regional_insights(self):
        """Generate regional insights"""
        try:
            if 'Region' not in self.df.columns:
                return
            
            # Top region
            regional_revenue = self.df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)
            if not regional_revenue.empty:
                top_region = regional_revenue.index[0]
                top_region_revenue = regional_revenue.iloc[0]
                total_revenue = self.df['Revenue'].sum()
                contribution = (top_region_revenue / total_revenue * 100)
                
                self.insights.append({
                    'type': 'Regional',
                    'category': 'Performance',
                    'insight': f"'{top_region}' region generates the highest revenue ({contribution:.1f}% of total)",
                    'impact': 'High',
                    'actionable': True
                })
            
            # Regional profit
            if 'Profit' in self.df.columns:
                regional_profit = self.df.groupby('Region')['Profit'].sum().sort_values(ascending=False)
                if not regional_profit.empty:
                    top_profit_region = regional_profit.index[0]
                    self.insights.append({
                        'type': 'Regional',
                        'category': 'Profitability',
                        'insight': f"'{top_profit_region}' region is the most profitable",
                        'impact': 'High',
                        'actionable': True
                    })
            
        except Exception as e:
            logger.error(f"Failed to generate regional insights: {e}")
    
    def _generate_profitability_insights(self):
        """Generate profitability insights"""
        try:
            if 'Profit' not in self.df.columns:
                return
            
            total_profit = self.df['Profit'].sum()
            total_revenue = self.df['Revenue'].sum()
            profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Profit margin assessment
            if profit_margin > 30:
                self.insights.append({
                    'type': 'Profitability',
                    'category': 'Performance',
                    'insight': f"Excellent profit margin of {profit_margin:.1f}%",
                    'impact': 'High',
                    'actionable': False
                })
            elif profit_margin > 15:
                self.insights.append({
                    'type': 'Profitability',
                    'category': 'Performance',
                    'insight': f"Healthy profit margin of {profit_margin:.1f}%",
                    'impact': 'Medium',
                    'actionable': False
                })
            elif profit_margin > 0:
                self.insights.append({
                    'type': 'Profitability',
                    'category': 'Warning',
                    'insight': f"Low profit margin of {profit_margin:.1f}% - consider cost optimization",
                    'impact': 'Medium',
                    'actionable': True
                })
            else:
                self.insights.append({
                    'type': 'Profitability',
                    'category': 'Critical',
                    'insight': f"Negative profit margin of {profit_margin:.1f}% - immediate action required",
                    'impact': 'High',
                    'actionable': True
                })
            
            # Loss-making orders
            loss_orders = len(self.df[self.df['Profit'] < 0])
            total_orders = len(self.df)
            loss_rate = (loss_orders / total_orders * 100) if total_orders > 0 else 0
            
            if loss_rate > 10:
                self.insights.append({
                    'type': 'Profitability',
                    'category': 'Risk',
                    'insight': f"{loss_rate:.1f}% of orders are loss-making - review pricing and costs",
                    'impact': 'High',
                    'actionable': True
                })
            
        except Exception as e:
            logger.error(f"Failed to generate profitability insights: {e}")
    
    def _generate_customer_insights(self):
        """Generate customer insights"""
        try:
            if 'Customer ID' not in self.df.columns:
                return
            
            unique_customers = self.df['Customer ID'].nunique()
            total_orders = len(self.df)
            avg_orders_per_customer = total_orders / unique_customers if unique_customers > 0 else 0
            
            self.insights.append({
                'type': 'Customer',
                'category': 'Engagement',
                'insight': f"Average {avg_orders_per_customer:.1f} orders per customer",
                'impact': 'Medium',
                'actionable': True
            })
            
            # Repeat customer rate
            customer_order_counts = self.df.groupby('Customer ID')['Order ID'].count()
            repeat_customers = len(customer_order_counts[customer_order_counts > 1])
            repeat_rate = (repeat_customers / unique_customers * 100) if unique_customers > 0 else 0
            
            if repeat_rate > 50:
                self.insights.append({
                    'type': 'Customer',
                    'category': 'Loyalty',
                    'insight': f"Strong customer loyalty with {repeat_rate:.1f}% repeat purchase rate",
                    'impact': 'High',
                    'actionable': False
                })
            elif repeat_rate < 30:
                self.insights.append({
                    'type': 'Customer',
                    'category': 'Retention',
                    'insight': f"Low repeat purchase rate ({repeat_rate:.1f}%) - focus on customer retention",
                    'impact': 'High',
                    'actionable': True
                })
            
        except Exception as e:
            logger.error(f"Failed to generate customer insights: {e}")
    
    def _generate_seasonal_insights(self):
        """Generate seasonal insights"""
        try:
            self.df['Month'] = self.df['Order Date'].dt.month
            monthly_revenue = self.df.groupby('Month')['Revenue'].mean()

            if monthly_revenue.empty:
                return

            peak_month = monthly_revenue.idxmax()
            peak_rows = self.df[self.df['Month'] == peak_month]['Order Date']
            if not peak_rows.empty:
                peak_month_name = peak_rows.dt.strftime('%B').iloc[0]
                self.insights.append({
                    'type': 'Seasonal',
                    'category': 'Pattern',
                    'insight': f"{peak_month_name} is historically the strongest month",
                    'impact': 'Medium',
                    'actionable': True
                })

            # Low season identification — guard with same empty check
            low_month = monthly_revenue.idxmin()
            low_rows = self.df[self.df['Month'] == low_month]['Order Date']
            if not low_rows.empty:
                low_month_name = low_rows.dt.strftime('%B').iloc[0]
                self.insights.append({
                    'type': 'Seasonal',
                    'category': 'Pattern',
                    'insight': f"{low_month_name} shows lowest average revenue - consider promotional campaigns",
                    'impact': 'Medium',
                    'actionable': True
                })
            
        except Exception as e:
            logger.error(f"Failed to generate seasonal insights: {e}")
    
    def get_insights_summary(self) -> Dict:
        """
        Get summary of generated insights
        
        Returns:
            Dictionary with insights summary
        """
        try:
            if not self.insights:
                self.generate_all_insights()
            
            summary = {
                'total_insights': len(self.insights),
                'by_type': {},
                'by_impact': {},
                'actionable_count': sum(1 for i in self.insights if i.get('actionable', False))
            }
            
            for insight in self.insights:
                insight_type = insight.get('type', 'Unknown')
                impact = insight.get('impact', 'Unknown')
                
                summary['by_type'][insight_type] = summary['by_type'].get(insight_type, 0) + 1
                summary['by_impact'][impact] = summary['by_impact'].get(impact, 0) + 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate insights summary: {e}")
            raise
    
    def get_high_priority_insights(self) -> List[Dict]:
        """
        Get high-priority actionable insights
        
        Returns:
            List of high-priority insights
        """
        try:
            high_priority = [i for i in self.insights if i.get('impact') == 'High' and i.get('actionable')]
            return high_priority
            
        except Exception as e:
            logger.error(f"Failed to get high priority insights: {e}")
            raise
