"""
Budget helper functions for period calculation and date math.
"""
from datetime import date
from calendar import monthrange


def get_month_period(year: int, month: int) -> tuple[date, date]:
    """
    Get first and last day of month.
    
    Args:
        year: Year (e.g., 2026)
        month: Month (1-12)
        
    Returns:
        Tuple of (start_date, end_date)
        
    Example:
        >>> get_month_period(2026, 1)
        (date(2026, 1, 1), date(2026, 1, 31))
    """
    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    return (start_date, end_date)


def get_current_month_period() -> tuple[date, date]:
    """
    Get current month period.
    
    Returns:
        Tuple of (start_date, end_date) for current month
        
    Example:
        If today is 2026-01-18:
        >>> get_current_month_period()
        (date(2026, 1, 1), date(2026, 1, 31))
    """
    today = date.today()
    return get_month_period(today.year, today.month)


def get_days_left_in_period(end_date: date, current_date: date | None = None) -> int:
    """
    Calculate days remaining in period (including current day).
    
    Args:
        end_date: Last day of period
        current_date: Reference date (defaults to today)
        
    Returns:
        Number of days left (including today), minimum 0
        
    Example:
        >>> get_days_left_in_period(date(2026, 1, 31), date(2026, 1, 16))
        16  # From Jan 16 to Jan 31, inclusive
    """
    if current_date is None:
        current_date = date.today()
    
    days = (end_date - current_date).days + 1  # +1 to include current day
    return max(0, days)  # Never negative
