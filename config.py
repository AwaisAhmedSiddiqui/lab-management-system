"""
Configuration Module - Lab Management & Analytics System
System-wide configuration settings
"""

# Application Settings
APP_NAME = "Lab Management & Analytics System"
APP_VERSION = "1.0.0"
APP_ICON = "🔬"

# Database Settings
DATABASE_NAME = "lab_management.db"

# Session Settings
SESSION_TIMEOUT_MINUTES = 60

# Performa Names with Display Names and Table Names
PERFORMAS = {
    'Data Retrieval Reports': 'data_retrieval_reports',
    'Lab Activity': 'lab_activity',
    'Special Checking in Lab': 'special_checking_in_lab',
    'Daily Checking Report': 'daily_checking_report',
    'Monthly Site Checking Report': 'monthly_site_checking_report',
    'AMI MDI TCPs': 'ami_mdi_tcps',
    'Audit Record': 'audit_record',
    'Court Cases': 'court_cases',
    'Log Book Record': 'log_book_record',
    'TA/DA Record': 'ta_da_record'
}

# Navigation Menu Items
MENU_ITEMS = {
    'main': [
        {'name': 'Dashboard', 'icon': '🏠'},
    ],
    'performas': [
        {'name': 'Data Retrieval Reports', 'icon': '📊'},
        {'name': 'Lab Activity', 'icon': '🔬'},
        {'name': 'Special Checking in Lab', 'icon': '🔍'},
        {'name': 'Daily Checking Report', 'icon': '📋'},
        {'name': 'Monthly Site Checking Report', 'icon': '📅'},
        {'name': 'AMI MDI TCPs', 'icon': '⚡'},
        {'name': 'Audit Record', 'icon': '📝'},
        {'name': 'Court Cases', 'icon': '⚖️'},
        {'name': 'Log Book Record', 'icon': '📖'},
        {'name': 'TA/DA Record', 'icon': '💰'},
    ],
    'admin': [
        {'name': 'Activity Logs', 'icon': '📜'},
        {'name': 'Theme Settings', 'icon': '🎨'},
        {'name': 'User Management', 'icon': '👥'},
        {'name': 'Database Backup', 'icon': '💾'},
    ]
}

# Default Theme Colors
DEFAULT_THEME = {
    'background_color': '#0E1117',
    'sidebar_color': '#262730',
    'text_color': '#FAFAFA',
    'card_color': '#1E1E1E',
    'primary_color': '#FF4B4B'
}

# Light Theme Preset
LIGHT_THEME = {
    'background_color': '#FFFFFF',
    'sidebar_color': '#F0F2F6',
    'text_color': '#262730',
    'card_color': '#FFFFFF',
    'primary_color': '#FF4B4B'
}

# Dark Blue Theme Preset
DARK_BLUE_THEME = {
    'background_color': '#0A1929',
    'sidebar_color': '#001E3C',
    'text_color': '#B2BAC2',
    'card_color': '#0A1929',
    'primary_color': '#5090D3'
}

# Green Theme Preset
GREEN_THEME = {
    'background_color': '#1A1D21',
    'sidebar_color': '#252A30',
    'text_color': '#E9ECEF',
    'card_color': '#2D3238',
    'primary_color': '#28A745'
}

# Theme Presets for Selection
THEME_PRESETS = {
    'Default Dark': DEFAULT_THEME,
    'Light': LIGHT_THEME,
    'Dark Blue': DARK_BLUE_THEME,
    'Green': GREEN_THEME
}

# Data Entry Columns Configuration
DATA_COLUMNS = [
    {'name': 's_no', 'display': 'S.No', 'type': 'auto', 'required': False},
    {'name': 'sub_division', 'display': 'Sub-Division', 'type': 'select', 'required': True},
    {'name': 'reference_no', 'display': 'Reference No', 'type': 'text', 'required': True, 'validation': '14_digit'},
    {'name': 'name', 'display': 'Name', 'type': 'text', 'required': True},
    {'name': 'tariff', 'display': 'Tariff', 'type': 'select', 'required': False},
    {'name': 'load', 'display': 'Load', 'type': 'text', 'required': False},
    {'name': 'meter_no', 'display': 'Meter No', 'type': 'text', 'required': False},
    {'name': 'make', 'display': 'Make', 'type': 'text', 'required': False},
    {'name': 'mco_no', 'display': 'MCO No', 'type': 'text', 'required': False},
    {'name': 'mco_date', 'display': 'MCO Date', 'type': 'date', 'required': False},
    {'name': 'bill_reading', 'display': 'Bill Reading', 'type': 'number', 'required': False},
    {'name': 'meter_reading', 'display': 'Meter Reading', 'type': 'number', 'required': False},
    {'name': 'difference', 'display': 'Difference', 'type': 'auto_calc', 'required': False},
    {'name': 'status', 'display': 'Status', 'type': 'select', 'required': False},
    {'name': 'remarks', 'display': 'Remarks', 'type': 'textarea', 'required': False},
    {'name': 'entry_date', 'display': 'Entry Date', 'type': 'timestamp', 'required': False, 'hidden': True},
]

# Activity Log Configuration
ACTIVITY_COLUMNS = [
    {'name': 'log_id', 'display': 'Log ID', 'type': 'auto'},
    {'name': 'username', 'display': 'Username', 'type': 'text'},
    {'name': 'role', 'display': 'Role', 'type': 'text'},
    {'name': 'session_id', 'display': 'Session ID', 'type': 'text'},
    {'name': 'performa_name', 'display': 'Performa Name', 'type': 'text'},
    {'name': 'action_type', 'display': 'Action Type', 'type': 'select'},
    {'name': 'reference_no', 'display': 'Reference No', 'type': 'text'},
    {'name': 'timestamp', 'display': 'Timestamp', 'type': 'datetime'},
]

# Role Permissions
PERMISSIONS = {
    'admin': {
        'can_add': True,
        'can_edit': True,
        'can_delete': True,
        'can_unlock': True,
        'can_view_logs': True,
        'can_change_theme': True,
        'can_manage_users': True,
        'can_backup': True,
    },
    'staff': {
        'can_add': True,
        'can_edit': True,  # Only unlocked records
        'can_delete': False,
        'can_unlock': False,
        'can_view_logs': False,
        'can_change_theme': False,
        'can_manage_users': False,
        'can_backup': False,
    }
}

# Status Options
STATUS_OPTIONS = ['Active', 'Pending', 'Completed', 'Cancelled', 'Under Review']

# Tariff Options
TARIFF_OPTIONS = ['A-1', 'A-2', 'A-3', 'B-1', 'B-2', 'B-3', 'C-1', 'C-2', 'C-3', 
                  'Industrial', 'Commercial', 'Domestic', 'Agriculture']

# Sub-Division Options
SUB_DIVISION_OPTIONS = [f'Sub-Division {i}' for i in range(1, 11)]

# Export Settings
EXPORT_FORMATS = ['Excel', 'PDF', 'CSV']

# Pagination Settings
RECORDS_PER_PAGE = 25

# Activity Log Limits
RECENT_ACTIVITIES_LIMIT = 10
MAX_ACTIVITY_EXPORT = 10000
