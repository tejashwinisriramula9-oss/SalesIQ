"""
SalesIQ Config Module
"""

from .settings import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    BASE_DIR,
    DATA_DIR,
    REPORTS_DIR,
    ASSETS_DIR,
    DATABASE_URL,
    THEME,
    REQUIRED_COLUMNS,
    SIDEBAR_MENU,
    FEATURES,
    get_version,
    get_app_name,
    is_production,
    get_data_file_path
)

__all__ = [
    'APP_NAME',
    'APP_VERSION',
    'APP_DESCRIPTION',
    'BASE_DIR',
    'DATA_DIR',
    'REPORTS_DIR',
    'ASSETS_DIR',
    'DATABASE_URL',
    'THEME',
    'REQUIRED_COLUMNS',
    'SIDEBAR_MENU',
    'FEATURES',
    'get_version',
    'get_app_name',
    'is_production',
    'get_data_file_path'
]
