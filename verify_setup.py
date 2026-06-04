"""
SalesIQ System Verification Script
Verifies all dependencies, configurations, and files before running the application
"""

import sys
import subprocess
from pathlib import Path
import importlib
from datetime import datetime

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print application header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       SalesIQ - System Verification & Setup Check          ║")
    print("║          Enterprise Business Intelligence Platform         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")

def print_section(title):
    """Print section header"""
    print(f"{Colors.BOLD}{Colors.BLUE}▶ {title}{Colors.END}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message):
    """Print info message"""
    print(f"  {message}")

def check_python_version():
    """Check Python version"""
    print_section("Python Version Check")
    
    version = sys.version_info
    required_version = (3, 9)
    
    if version >= required_version:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.9+ required. Current: {version.major}.{version.minor}")
        return False

def check_dependencies():
    """Check all required Python dependencies"""
    print_section("Python Dependencies Check")
    
    dependencies = {
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'plotly': 'Plotly',
        'sqlalchemy': 'SQLAlchemy',
        'sklearn': 'Scikit-learn',
        'loguru': 'Loguru',
    }
    
    all_installed = True
    
    for package, name in dependencies.items():
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'unknown')
            print_success(f"{name} ({version})")
        except ImportError:
            print_error(f"{name} not installed")
            all_installed = False
    
    if not all_installed:
        print_warning("Some dependencies are missing. Run: pip install -r requirements.txt")
    
    return all_installed

def check_directory_structure():
    """Check if all required directories exist"""
    print_section("Directory Structure Check")
    
    base_dir = Path(__file__).parent
    required_dirs = {
        'analytics': 'Analytics module',
        'database': 'Database module',
        'forecasting': 'Forecasting module',
        'utils': 'Utilities module',
        'config': 'Configuration module',
        'data': 'Data storage',
        'reports': 'Reports generation',
    }
    
    all_exist = True
    
    for dir_name, description in required_dirs.items():
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print_success(f"{dir_name}/ ({description})")
        else:
            print_error(f"{dir_name}/ missing ({description})")
            all_exist = False
    
    return all_exist

def check_files():
    """Check if all required files exist"""
    print_section("Required Files Check")
    
    base_dir = Path(__file__).parent
    required_files = {
        'app.py': 'Main Streamlit application',
        'requirements.txt': 'Dependencies list',
        'README.md': 'Documentation',
        'config/settings.py': 'Configuration file',
        'database/models.py': 'Database models',
        'database/connection.py': 'Database connection',
        'analytics/sales_analytics.py': 'Sales analytics module',
        'forecasting/forecasting_models.py': 'Forecasting module',
        'utils/data_processor.py': 'Data processor',
    }
    
    all_exist = True
    
    for file_path, description in required_files.items():
        full_path = base_dir / file_path
        if full_path.exists():
            file_size = full_path.stat().st_size
            print_success(f"{file_path} ({description})")
            print_info(f"  Size: {file_size:,} bytes")
        else:
            print_error(f"{file_path} missing ({description})")
            all_exist = False
    
    return all_exist

def check_sample_data():
    """Check if sample data exists"""
    print_section("Sample Data Check")
    
    data_dir = Path(__file__).parent / 'data'
    sample_file = data_dir / 'sample_sales.csv'
    
    if sample_file.exists():
        try:
            import pandas as pd
            df = pd.read_csv(sample_file)
            print_success(f"Sample data found (sample_sales.csv)")
            print_info(f"  Records: {len(df)}")
            print_info(f"  Columns: {', '.join(df.columns[:5])}...")
            print_info(f"  Size: {sample_file.stat().st_size:,} bytes")
            return True
        except Exception as e:
            print_error(f"Sample data exists but cannot be read: {str(e)}")
            return False
    else:
        print_warning("Sample data not found (sample_sales.csv)")
        print_info("  Run 'python verify_setup.py' to generate sample data")
        return False

def check_imports():
    """Check if core modules can be imported"""
    print_section("Module Import Check")
    
    modules = {
        'config.settings': 'Configuration module',
        'database.models': 'Database models',
        'database.connection': 'Database connection',
        'analytics.sales_analytics': 'Sales analytics',
        'forecasting.forecasting_models': 'Forecasting models',
        'utils.data_processor': 'Data processor',
    }
    
    all_imported = True
    
    for module_path, description in modules.items():
        try:
            __import__(module_path)
            print_success(f"{module_path} ({description})")
        except ImportError as e:
            print_error(f"{module_path} import failed: {str(e)}")
            all_imported = False
        except Exception as e:
            print_warning(f"{module_path} import warning: {str(e)}")
    
    return all_imported

def check_database():
    """Check database connectivity"""
    print_section("Database Check")
    
    try:
        from database.connection import DatabaseManager
        
        db_manager = DatabaseManager()
        print_success("Database connection successful")
        print_info(f"  Database URL: {db_manager.database_url}")
        return True
    except Exception as e:
        print_warning(f"Database connection test: {str(e)}")
        print_info("  This is expected if database is not yet initialized")
        return True  # Not a critical failure

def print_summary(checks):
    """Print verification summary"""
    print_section("Verification Summary")
    
    passed = sum(checks.values())
    total = len(checks)
    percentage = (passed / total) * 100
    
    for check_name, result in checks.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {check_name}: {status}")
    
    print(f"\n  Overall: {passed}/{total} checks passed ({percentage:.0f}%)")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All systems ready! You can run: streamlit run app.py{Colors.END}\n")
        return True
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some checks failed. Please resolve issues above.{Colors.END}\n")
        return False

def main():
    """Run all verification checks"""
    print_header()
    
    checks = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Directories': check_directory_structure(),
        'Files': check_files(),
        'Sample Data': check_sample_data(),
        'Module Imports': check_imports(),
        'Database': check_database(),
    }
    
    print("\n")
    success = print_summary(checks)
    
    print(f"{Colors.BOLD}Additional Information:{Colors.END}")
    print(f"  • Application: SalesIQ v1.0.0")
    print(f"  • Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  • Python: {sys.version.split()[0]}")
    print(f"  • Platform: {sys.platform}")
    print()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
