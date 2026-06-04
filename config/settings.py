"""
SalesIQ Configuration Module
Centralized configuration for the application
"""

import os
from pathlib import Path
from datetime import datetime

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

APP_NAME = "SalesIQ"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-Powered Sales Intelligence & Business Analytics Platform"
APP_TAGLINE = "Transforming Sales Data into Intelligent Business Decisions"

# ============================================================================
# PATHS & DIRECTORIES
# ============================================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
ASSETS_DIR = BASE_DIR / "assets"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, REPORTS_DIR, ASSETS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# SQLite database (can be changed to PostgreSQL for production)
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    f'sqlite:///{BASE_DIR}/salesiq.db'
)

# Connection pool settings
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_RECYCLE = 3600

# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================

STREAMLIT_CONFIG = {
    'page_title': 'SalesIQ - Business Intelligence',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# ============================================================================
# THEME & UI SETTINGS
# ============================================================================

THEME = {
    'primary_color': '#1F77B4',
    'secondary_color': '#FF7F0E',
    'success_color': '#2CA02C',
    'danger_color': '#D62728',
    'warning_color': '#FF9800',
    'info_color': '#2196F3',
    'background': '#FFFFFF',
    'surface': '#F8F9FA',
    'text_primary': '#1A1A1A',
    'text_secondary': '#6B7280',
    'border_color': '#E5E7EB'
}

# ============================================================================
# DATA SETTINGS
# ============================================================================

# Sample data file name
SAMPLE_DATA_FILE = 'sample_sales.csv'

# Required columns for sales data
REQUIRED_COLUMNS = [
    'Order ID',
    'Order Date',
    'Customer ID',
    'Customer Name',
    'Product',
    'Category',
    'Region',
    'Quantity',
    'Unit Price',
    'Revenue',
    'Cost',
    'Profit'
]

# Date format for parsing
DATE_FORMAT = '%Y-%m-%d'

# ============================================================================
# ANALYTICS & FORECASTING SETTINGS
# ============================================================================

# Forecasting parameters
FORECAST_PERIODS = 30  # Days to forecast
TEST_SIZE = 0.2  # Train-test split ratio
RANDOM_STATE = 42  # For reproducibility

# Forecasting models
FORECASTING_MODELS = {
    'linear_regression': 'Linear Regression',
    'random_forest': 'Random Forest',
    'arima': 'ARIMA'
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} | {asctime} | {name} | {message}',
            'style': '{'
        },
        'simple': {
            'format': '{levelname} | {message}',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filename': str(LOGS_DIR / 'salesiq.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}

# ============================================================================
# PAGINATION & DISPLAY SETTINGS
# ============================================================================

DEFAULT_ROWS_PER_PAGE = 50
MAX_ROWS_DISPLAY = 1000
CHART_HEIGHT = 400
CHART_WIDTH = 'container'

# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURES = {
    'dark_mode': False,  # Enable dark mode toggle
    'real_time_updates': False,  # Real-time data refresh
    'advanced_analytics': True,  # Enable advanced analytics
    'ml_forecasting': True,  # Enable ML forecasting
    'report_generation': True,  # Enable PDF/Excel reports
    'data_upload': True,  # Enable CSV upload feature
}

# ============================================================================
# MENU CONFIGURATION
# ============================================================================

SIDEBAR_MENU = [
    {
        'icon': '📊',
        'label': 'Executive Dashboard',
        'key': 'Dashboard'
    },
    {
        'icon': '📈',
        'label': 'Sales Analytics',
        'key': 'Sales'
    },
    {
        'icon': '👥',
        'label': 'Customer Intelligence',
        'key': 'Customers'
    },
    {
        'icon': '💰',
        'label': 'Profitability Analysis',
        'key': 'Profitability'
    },
    {
        'icon': '🔮',
        'label': 'AI Forecasting',
        'key': 'Forecasting'
    },
    {
        'icon': '💡',
        'label': 'AI Insights',
        'key': 'Insights'
    },
    {
        'icon': '📄',
        'label': 'Reports & Export',
        'key': 'Reports'
    },
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_version():
    """Get application version"""
    return APP_VERSION

def get_app_name():
    """Get application name"""
    return APP_NAME

def is_production():
    """Check if running in production"""
    return os.getenv('ENVIRONMENT', 'development') == 'production'

def get_data_file_path(filename):
    """Get full path to data file"""
    return DATA_DIR / filename
