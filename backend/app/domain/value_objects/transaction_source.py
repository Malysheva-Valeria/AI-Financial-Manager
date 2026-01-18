"""
Transaction Source Value Object.
Defines how transaction was created.
"""
from enum import Enum


class TransactionSource(str, Enum):
    """
    Source of transaction creation.
    
    Attributes:
        MANUAL: User manually added transaction
        MONOBANK: Automatically synced from Monobank API
    """
    MANUAL = "MANUAL"
    MONOBANK = "MONOBANK"
    
    def is_manual(self) -> bool:
        """Check if transaction was manually added."""
        return self == TransactionSource.MANUAL
    
    def is_from_bank(self) -> bool:
        """Check if transaction came from Monobank."""
        return self == TransactionSource.MONOBANK
