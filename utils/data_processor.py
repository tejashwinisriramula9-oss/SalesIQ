"""
SalesIQ Data Processor
Enterprise-grade data import, cleaning, and transformation utilities
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Enterprise data processing pipeline
    Handles data import, validation, cleaning, and transformation
    """
    
    REQUIRED_COLUMNS = [
        'Order ID', 'Order Date', 'Customer ID', 'Customer Name',
        'Product', 'Category', 'Region', 'Quantity', 'Unit Price',
        'Revenue', 'Cost', 'Profit'
    ]
    
    def __init__(self):
        """Initialize data processor"""
        self.raw_data = None
        self.processed_data = None
        self.validation_errors = []
    
    def import_data(self, file_path: str = None, file_obj = None) -> pd.DataFrame:
        """
        Import data from various file formats
        
        Args:
            file_path: Path to data file
            file_obj: File object (for Streamlit uploads)
            
        Returns:
            Imported DataFrame
        """
        try:
            if file_obj is not None:
                # Handle Streamlit file upload
                file_extension = file_obj.name.split('.')[-1].lower()
                
                if file_extension == 'csv':
                    self.raw_data = pd.read_csv(file_obj)
                elif file_extension in ['xlsx', 'xls']:
                    self.raw_data = pd.read_excel(file_obj)
                else:
                    raise ValueError(f"Unsupported file format: {file_extension}")
                    
            elif file_path:
                # Handle file path
                file_extension = file_path.split('.')[-1].lower()
                
                if file_extension == 'csv':
                    self.raw_data = pd.read_csv(file_path)
                elif file_extension in ['xlsx', 'xls']:
                    self.raw_data = pd.read_excel(file_path)
                else:
                    raise ValueError(f"Unsupported file format: {file_extension}")
            else:
                raise ValueError("Either file_path or file_obj must be provided")
            
            logger.info(f"Data imported successfully: {len(self.raw_data)} rows")
            return self.raw_data
            
        except Exception as e:
            logger.error(f"Data import failed: {e}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate data structure and content
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append("DataFrame is empty")
            return False, errors
        
        # Check required columns
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Check for null values in critical columns
        critical_cols = ['Order ID', 'Order Date', 'Quantity', 'Unit Price', 'Revenue']
        for col in critical_cols:
            if col in df.columns and df[col].isnull().any():
                errors.append(f"Null values found in critical column: {col}")
        
        # Check data types
        if 'Quantity' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['Quantity']):
                errors.append("Quantity column must be numeric")
        
        if 'Revenue' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['Revenue']):
                errors.append("Revenue column must be numeric")
        
        self.validation_errors = errors
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("Data validation passed")
        else:
            logger.warning(f"Data validation failed: {errors}")
        
        return is_valid, errors
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess data
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        try:
            df_clean = df.copy()
            
            # Remove duplicates
            initial_rows = len(df_clean)
            df_clean = df_clean.drop_duplicates()
            duplicates_removed = initial_rows - len(df_clean)
            if duplicates_removed > 0:
                logger.info(f"Removed {duplicates_removed} duplicate rows")
            
            # Handle missing values
            for col in df_clean.columns:
                if df_clean[col].isnull().any():
                    if pd.api.types.is_numeric_dtype(df_clean[col]):
                        df_clean[col].fillna(0, inplace=True)
                    else:
                        df_clean[col].fillna('Unknown', inplace=True)
            
            # Standardize column names
            df_clean.columns = df_clean.columns.str.strip()
            
            # Convert date column
            if 'Order Date' in df_clean.columns:
                df_clean['Order Date'] = pd.to_datetime(df_clean['Order Date'], errors='coerce')
            
            # Ensure numeric columns are proper types
            numeric_cols = ['Quantity', 'Unit Price', 'Revenue', 'Cost', 'Profit']
            for col in numeric_cols:
                if col in df_clean.columns:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
            
            # Remove rows with invalid dates
            if 'Order Date' in df_clean.columns:
                df_clean = df_clean[df_clean['Order Date'].notna()]
            
            # Calculate derived metrics if missing
            if 'Revenue' in df_clean.columns and 'Cost' in df_clean.columns:
                if 'Profit' not in df_clean.columns or df_clean['Profit'].isnull().all():
                    df_clean['Profit'] = df_clean['Revenue'] - df_clean['Cost']
            
            if 'Quantity' in df_clean.columns and 'Unit Price' in df_clean.columns:
                if 'Revenue' not in df_clean.columns or df_clean['Revenue'].isnull().all():
                    df_clean['Revenue'] = df_clean['Quantity'] * df_clean['Unit Price']
            
            logger.info(f"Data cleaning completed: {len(df_clean)} rows")
            self.processed_data = df_clean
            return df_clean
            
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            raise
    
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data for analysis
        
        Args:
            df: DataFrame to transform
            
        Returns:
            Transformed DataFrame with additional features
        """
        try:
            df_transform = df.copy()
            
            # Add time-based features
            if 'Order Date' in df_transform.columns:
                df_transform['Year'] = df_transform['Order Date'].dt.year
                df_transform['Month'] = df_transform['Order Date'].dt.month
                df_transform['Quarter'] = df_transform['Order Date'].dt.quarter
                df_transform['DayOfWeek'] = df_transform['Order Date'].dt.dayofweek
                df_transform['MonthName'] = df_transform['Order Date'].dt.strftime('%B')
            
            # Add profit margin
            if 'Revenue' in df_transform.columns and 'Cost' in df_transform.columns:
                df_transform['ProfitMargin'] = (df_transform['Profit'] / df_transform['Revenue'] * 100).round(2)
                df_transform['ProfitMargin'] = df_transform['ProfitMargin'].fillna(0)
            
            # Add profit/loss indicator
            if 'Profit' in df_transform.columns:
                df_transform['ProfitStatus'] = df_transform['Profit'].apply(
                    lambda x: 'Profit' if x > 0 else 'Loss' if x < 0 else 'Break-even'
                )
            
            # Standardize text columns
            text_cols = ['Category', 'Region', 'Product']
            for col in text_cols:
                if col in df_transform.columns:
                    df_transform[col] = df_transform[col].str.strip().str.title()
            
            logger.info("Data transformation completed")
            return df_transform
            
        except Exception as e:
            logger.error(f"Data transformation failed: {e}")
            raise
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate data summary statistics
        
        Args:
            df: DataFrame to summarize
            
        Returns:
            Dictionary of summary statistics
        """
        try:
            summary = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'date_range': {},
                'numeric_summary': {},
                'categorical_summary': {}
            }
            
            # Date range
            if 'Order Date' in df.columns:
                summary['date_range'] = {
                    'start': df['Order Date'].min().strftime('%Y-%m-%d'),
                    'end': df['Order Date'].max().strftime('%Y-%m-%d'),
                    'days': (df['Order Date'].max() - df['Order Date'].min()).days
                }
            
            # Numeric summary
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in ['Revenue', 'Profit', 'Quantity']:
                if col in numeric_cols:
                    summary['numeric_summary'][col] = {
                        'total': df[col].sum(),
                        'mean': df[col].mean(),
                        'median': df[col].median(),
                        'min': df[col].min(),
                        'max': df[col].max(),
                        'std': df[col].std()
                    }
            
            # Categorical summary
            categorical_cols = ['Category', 'Region', 'Product']
            for col in categorical_cols:
                if col in df.columns:
                    summary['categorical_summary'][col] = {
                        'unique_count': df[col].nunique(),
                        'top_values': df[col].value_counts().head(5).to_dict()
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate data summary: {e}")
            raise
    
    def export_to_csv(self, df: pd.DataFrame, filename: str) -> str:
        """
        Export DataFrame to CSV
        
        Args:
            df: DataFrame to export
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        try:
            output_path = f"data/{filename}"
            df.to_csv(output_path, index=False)
            logger.info(f"Data exported to CSV: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            raise
    
    def export_to_excel(self, df: pd.DataFrame, filename: str) -> str:
        """
        Export DataFrame to Excel
        
        Args:
            df: DataFrame to export
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        try:
            output_path = f"data/{filename}"
            df.to_excel(output_path, index=False, engine='openpyxl')
            logger.info(f"Data exported to Excel: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            raise


def process_uploaded_file(file_obj) -> pd.DataFrame:
    """
    Convenience function to process uploaded file
    
    Args:
        file_obj: Uploaded file object
        
    Returns:
        Processed DataFrame
    """
    processor = DataProcessor()
    
    # Import
    df = processor.import_data(file_obj=file_obj)
    
    # Validate
    is_valid, errors = processor.validate_data(df)
    if not is_valid:
        logger.warning(f"Data validation issues: {errors}")
    
    # Clean
    df_clean = processor.clean_data(df)
    
    # Transform
    df_transform = processor.transform_data(df_clean)
    
    return df_transform
