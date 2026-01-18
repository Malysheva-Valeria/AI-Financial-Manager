"""
User Domain Entity.
Pure business logic, framework-independent.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.domain.value_objects.tracking_mode import TrackingMode


@dataclass
class User:
    """
    User domain entity representing core business logic.
    
    This is separate from UserModel (ORM) following Dependency Inversion Principle.
    Contains only business rules, no database or framework dependencies.
    """
    id: Optional[int]
    email: str
    tracking_mode: TrackingMode
    is_premium: bool
    cash_reminder_enabled: bool = False
    mono_token: Optional[str] = None
    mono_account_id: Optional[str] = None
    webhook_hash: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def can_use_ai_advisor(self) -> bool:
        """
        Business rule: AI Advisor requires premium subscription.
        
        Returns:
            True if user has premium access, False otherwise
        """
        return self.is_premium
    
    def can_use_auto_tracking(self) -> bool:
        """
        Business rule: Auto tracking requires Monobank token.
        
        Returns:
            True if user has valid Monobank token configured
        """
        return (
            self.tracking_mode == TrackingMode.AUTO_MONO 
            and self.mono_token is not None
        )
    
    def switch_to_manual_mode(self) -> None:
        """
        Business logic: Switching to manual mode clears Monobank data.
        
        This ensures user privacy when they choose manual tracking.
        """
        self.tracking_mode = TrackingMode.MANUAL
        self.mono_token = None
        self.mono_account_id = None
        self.webhook_hash = None
        self.updated_at = datetime.now(timezone.utc)
    
    def switch_to_auto_mode(self, mono_token: str, mono_account_id: str) -> None:
        """
        Business logic: Switching to auto mode requires Monobank credentials.
        
        Args:
            mono_token: Encrypted Monobank API token
            mono_account_id: Monobank account ID (white jar)
        
        Raises:
            ValueError: If token or account ID is empty
        """
        if not mono_token or not mono_account_id:
            raise ValueError("Monobank token and account ID are required for AUTO mode")
        
        self.tracking_mode = TrackingMode.AUTO_MONO
        self.mono_token = mono_token
        self.mono_account_id = mono_account_id
        self.updated_at = datetime.now(timezone.utc)
    
    def enable_premium(self) -> None:
        """Activate premium subscription."""
        self.is_premium = True
        self.updated_at = datetime.now(timezone.utc)
    
    def disable_premium(self) -> None:
        """Deactivate premium subscription."""
        self.is_premium = False
        self.updated_at = datetime.now(timezone.utc)
    
    def __str__(self) -> str:
        """String representation."""
        return f"User(id={self.id}, email={self.email}, premium={self.is_premium})"
