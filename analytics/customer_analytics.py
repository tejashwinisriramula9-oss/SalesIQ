"""
SalesIQ Customer Analytics Module
Enterprise-grade customer intelligence, RFM analysis, and segmentation
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerAnalytics:
    """
    Comprehensive customer analytics engine
    Provides RFM analysis, customer lifetime value, and segmentation
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize customer analytics
        
        Args:
            df: Sales data DataFrame
        """
        self.df = df.copy()
        self.customer_segments = None
        self._validate_data()
    
    def _validate_data(self):
        """Validate required columns exist"""
        required_cols = ['Order Date', 'Revenue', 'Customer ID']
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(self.df['Order Date']):
            self.df['Order Date'] = pd.to_datetime(self.df['Order Date'])
    
    def calculate_rfm(self) -> pd.DataFrame:
        """
        Calculate RFM (Recency, Frequency, Monetary) scores
        
        Returns:
            DataFrame with RFM scores and segments
        """
        try:
            reference_date = self.df['Order Date'].max() + timedelta(days=1)
            
            # Calculate RFM metrics
            rfm = self.df.groupby('Customer ID').agg({
                'Order Date': lambda x: (reference_date - x.max()).days,  # Recency
                'Order ID': 'count',  # Frequency
                'Revenue': 'sum'  # Monetary
            }).reset_index()
            
            rfm.columns = ['Customer ID', 'Recency', 'Frequency', 'Monetary']

            n_customers = len(rfm)
            if n_customers < 5:
                # Not enough customers for quintile scoring — assign mid scores
                rfm['R_Score'] = 3
                rfm['F_Score'] = 3
                rfm['M_Score'] = 3
            else:
                # Calculate RFM scores (1-5 scale, 5 being best)
                rfm['R_Score'] = pd.qcut(rfm['Recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1])
                rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
                rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
            
            # Convert scores to numeric
            rfm['R_Score'] = rfm['R_Score'].astype(int)
            rfm['F_Score'] = rfm['F_Score'].astype(int)
            rfm['M_Score'] = rfm['M_Score'].astype(int)
            
            # Calculate combined RFM score
            rfm['RFM_Score'] = rfm['R_Score'] * 100 + rfm['F_Score'] * 10 + rfm['M_Score']
            
            # Segment customers based on RFM scores
            rfm['Segment'] = rfm.apply(self._assign_rfm_segment, axis=1)
            
            logger.info("RFM analysis completed")
            self.customer_segments = rfm
            return rfm
            
        except Exception as e:
            logger.error(f"Failed to calculate RFM: {e}")
            raise
    
    def _assign_rfm_segment(self, row: pd.Series) -> str:
        """
        Assign RFM segment based on scores
        
        Args:
            row: DataFrame row with RFM scores
            
        Returns:
            Segment name
        """
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 4 and f >= 3:
            return 'Loyal Customers'
        elif r >= 3 and m >= 4:
            return 'Potential Loyalists'
        elif r >= 4 and f <= 2:
            return 'New Customers'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2 and m >= 3:
            return 'Hibernating'
        elif r <= 2 and f <= 2 and m <= 2:
            return 'Lost'
        else:
            return 'Others'
    
    def calculate_customer_lifetime_value(self) -> pd.DataFrame:
        """
        Calculate Customer Lifetime Value (CLV)
        
        Returns:
            DataFrame with CLV metrics
        """
        try:
            # Calculate basic customer metrics
            customer_metrics = self.df.groupby('Customer ID').agg({
                'Order Date': ['min', 'max', 'count'],
                'Revenue': ['sum', 'mean'],
                'Profit': 'sum'
            }).reset_index()
            
            customer_metrics.columns = ['Customer ID', 'First Purchase', 'Last Purchase',
                                      'Total Orders', 'Total Revenue', 'Avg Order Value',
                                      'Total Profit']
            
            # Calculate customer lifespan in days
            customer_metrics['Lifespan Days'] = (
                customer_metrics['Last Purchase'] - customer_metrics['First Purchase']
            ).dt.days + 1
            
            # Calculate average purchase frequency (orders per day)
            customer_metrics['Purchase Frequency'] = (
                customer_metrics['Total Orders'] / customer_metrics['Lifespan Days']
            )
            
            # Calculate CLV (simplified model: Avg Order Value * Purchase Frequency * 365)
            customer_metrics['CLV'] = (
                customer_metrics['Avg Order Value'] * 
                customer_metrics['Purchase Frequency'] * 365
            ).round(2)
            
            # Add customer names if available
            if 'Customer Name' in self.df.columns:
                customer_names = self.df.groupby('Customer ID')['Customer Name'].first().reset_index()
                customer_metrics = customer_metrics.merge(customer_names, on='Customer ID', how='left')
            
            logger.info("Customer Lifetime Value calculated")
            return customer_metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate CLV: {e}")
            raise
    
    def perform_customer_clustering(self, n_clusters: int = 5) -> pd.DataFrame:
        """
        Perform K-means clustering on customers
        
        Args:
            n_clusters: Number of clusters to create
            
        Returns:
            DataFrame with cluster assignments
        """
        try:
            # Prepare data for clustering
            customer_data = self.df.groupby('Customer ID').agg({
                'Revenue': 'sum',
                'Order ID': 'count',
                'Quantity': 'sum',
                'Profit': 'sum'
            }).reset_index()
            
            customer_data.columns = ['Customer ID', 'Total Revenue', 'Order Count',
                                   'Total Quantity', 'Total Profit']
            
            # Add average order value
            customer_data['Avg Order Value'] = customer_data['Total Revenue'] / customer_data['Order Count']
            
            # Select features for clustering
            features = ['Total Revenue', 'Order Count', 'Total Quantity', 'Total Profit', 'Avg Order Value']
            X = customer_data[features].values
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Add cluster labels to dataframe
            customer_data['Cluster'] = clusters
            customer_data['Cluster'] = customer_data['Cluster'].astype(str)
            
            # Calculate cluster statistics
            cluster_stats = customer_data.groupby('Cluster').agg({
                'Total Revenue': ['mean', 'sum'],
                'Order Count': 'mean',
                'Total Profit': 'mean',
                'Customer ID': 'count'
            }).reset_index()
            
            cluster_stats.columns = ['Cluster', 'Avg Revenue', 'Total Revenue',
                                   'Avg Orders', 'Avg Profit', 'Customer Count']
            
            logger.info(f"Customer clustering completed with {n_clusters} clusters")
            return customer_data, cluster_stats
            
        except Exception as e:
            logger.error(f"Failed to perform customer clustering: {e}")
            raise
    
    def get_retention_metrics(self) -> Dict:
        """
        Calculate customer retention metrics
        
        Returns:
            Dictionary of retention metrics
        """
        try:
            # Calculate customer retention by month
            self.df['YearMonth'] = self.df['Order Date'].dt.to_period('ME')
            
            # Get unique customers per month
            monthly_customers = self.df.groupby('YearMonth')['Customer ID'].nunique()
            
            # Calculate retention rate (customers who returned in subsequent months)
            retention_rates = []
            for i in range(1, len(monthly_customers)):
                prev_month = monthly_customers.index[i-1]
                curr_month = monthly_customers.index[i]
                
                prev_customers = set(self.df[self.df['YearMonth'] == prev_month]['Customer ID'])
                curr_customers = set(self.df[self.df['YearMonth'] == curr_month]['Customer ID'])
                
                retained = len(prev_customers & curr_customers)
                retention_rate = (retained / len(prev_customers)) * 100 if prev_customers else 0
                retention_rates.append(retention_rate)
            
            avg_retention_rate = np.mean(retention_rates) if retention_rates else 0
            
            # Calculate repeat purchase rate
            customer_order_counts = self.df.groupby('Customer ID')['Order ID'].count()
            repeat_customers = len(customer_order_counts[customer_order_counts > 1])
            repeat_purchase_rate = (repeat_customers / len(customer_order_counts)) * 100 if not customer_order_counts.empty else 0
            
            metrics = {
                'avg_retention_rate': round(avg_retention_rate, 2),
                'repeat_purchase_rate': round(repeat_purchase_rate, 2),
                'total_customers': len(customer_order_counts),
                'repeat_customers': repeat_customers
            }
            
            logger.info("Retention metrics calculated")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate retention metrics: {e}")
            raise
    
    def get_segment_summary(self, rfm_df: pd.DataFrame) -> pd.DataFrame:
        """
        Get summary statistics for each customer segment
        
        Args:
            rfm_df: DataFrame with RFM segments
            
        Returns:
            DataFrame with segment summaries
        """
        try:
            segment_summary = rfm_df.groupby('Segment').agg({
                'Customer ID': 'count',
                'Recency': 'mean',
                'Frequency': 'mean',
                'Monetary': 'mean'
            }).reset_index()
            
            segment_summary.columns = ['Segment', 'Customer Count', 'Avg Recency',
                                     'Avg Frequency', 'Avg Monetary']
            segment_summary = segment_summary.sort_values('Avg Monetary', ascending=False)
            
            logger.info("Segment summary generated")
            return segment_summary
            
        except Exception as e:
            logger.error(f"Failed to generate segment summary: {e}")
            raise
    
    def get_top_customers(self, n: int = 10, metric: str = 'Revenue') -> pd.DataFrame:
        """
        Get top customers by specified metric
        
        Args:
            n: Number of top customers to return
            metric: Metric to rank by (Revenue, Profit, Orders)
            
        Returns:
            DataFrame of top customers
        """
        try:
            metric_col = metric if metric in self.df.columns else 'Revenue'
            
            customer_stats = self.df.groupby(['Customer ID', 'Customer Name']).agg({
                'Revenue': 'sum',
                'Profit': 'sum',
                'Order ID': 'count'
            }).reset_index()
            
            customer_stats.columns = ['Customer ID', 'Customer Name', 'Total Revenue',
                                     'Total Profit', 'Total Orders']
            
            customer_stats = customer_stats.sort_values(by=f'Total {metric}', ascending=False).head(n)
            customer_stats = customer_stats.reset_index(drop=True)
            
            logger.info(f"Top {n} customers by {metric} retrieved")
            return customer_stats
            
        except Exception as e:
            logger.error(f"Failed to get top customers: {e}")
            raise
