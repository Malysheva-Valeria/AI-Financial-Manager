"""
Tracking Mode Value Object.
Defines how user tracks their finances: AUTO_MONO (Monobank integration) or MANUAL.
"""
from enum import Enum


class TrackingMode(str, Enum):
    """
    Tracking mode for financial transactions.
    
    Attributes:
        AUTO_MONO: Automatic tracking via Monobank API
        MANUAL: Manual entry of all transactions
    """
    AUTO_MONO = "AUTO_MONO"
    MANUAL = "MANUAL"
    
    def is_auto(self) -> bool:
        """Check if tracking mode is automatic."""
        return self == TrackingMode.AUTO_MONO
    
    def requires_bank_token(self) -> bool:
        """Check if mode requires Monobank token."""
        return self == TrackingMode.AUTO_MONO
