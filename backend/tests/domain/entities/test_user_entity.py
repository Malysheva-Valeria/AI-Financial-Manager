"""
Unit tests for User domain entity.
Tests pure business logic without database dependencies.
"""
import pytest
from datetime import datetime, timezone

from app.domain.entities.user import User
from app.domain.value_objects.tracking_mode import TrackingMode


class TestUserEntity:
    """Test User domain entity business logic."""
    
    def test_user_creation(self):
        """Test basic user creation."""
        user = User(
            id=1,
            email="test@example.com",
            tracking_mode=TrackingMode.MANUAL,
            is_premium=False
        )
        
        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.tracking_mode == TrackingMode.MANUAL
        assert user.is_premium is False
    
    def test_premium_user_can_use_ai_advisor(self):
        """Test business rule: Premium users can access AI advisor."""
        user = User(
            id=1,
            email="premium@example.com",
            tracking_mode=TrackingMode.MANUAL,
            is_premium=True
        )
        
        assert user.can_use_ai_advisor() is True
    
    def test_free_user_cannot_use_ai_advisor(self):
        """Test business rule: Free users cannot access AI advisor."""
        user = User(
            id=1,
            email="free@example.com",
            tracking_mode=TrackingMode.MANUAL,
            is_premium=False
        )
        
        assert user.can_use_ai_advisor() is False
    
    def test_user_with_token_can_use_auto_tracking(self):
        """Test business rule: Auto tracking requires token."""
        user = User(
            id=1,
            email="test@example.com",
            tracking_mode=TrackingMode.AUTO_MONO,
            is_premium=False,
            mono_token="encrypted_token_here",
            mono_account_id="account123"
        )
        
        assert user.can_use_auto_tracking() is True
    
    def test_user_without_token_cannot_use_auto_tracking(self):
        """Test business rule: Auto tracking fails without token."""
        user = User(
            id=1,
            email="test@example.com",
            tracking_mode=TrackingMode.AUTO_MONO,
            is_premium=False,
            mono_token=None
        )
        
        assert user.can_use_auto_tracking() is False
    
    def test_switch_to_manual_mode_clears_monobank_data(self):
        """Test that switching to manual mode removes Monobank credentials."""
        user = User(
            id=1,
            email="test@example.com",
            tracking_mode=TrackingMode.AUTO_MONO,
            is_premium=False,
            mono_token="encrypted_token",
            mono_account_id="account123",
            webhook_hash="webhook_abc"
        )
        
        user.switch_to_manual_mode()
        
        assert user.tracking_mode == TrackingMode.MANUAL
        assert user.mono_token is None
        assert user.mono_account_id is None
        assert user.webhook_hash is None
    
    def test_switch_to_auto_mode_sets_credentials(self):
        """Test switching to auto mode with credentials."""
        user = User(
            id=1,
            email="test@example.com",
            tracking_mode=TrackingMode.MANUAL,
            is_premium=False
        )
        
        user.switch_to_auto_mode(
            mono_token="new_token",
            mono_account_id="new_account"
        )
        
        assert user.tracking_mode == TrackingMode.AUTO_MONO
        assert user.mono_token == "new_token"
        assert user.mono_account_id == "new_account"
    
    def test_switch_to_auto_mode_without_token_raises_error(self):
        """Test that auto mode requires token."""
        user = User(
            id=1,
            email="test@example.com",
            tracking_mode=TrackingMode.MANUAL,
            is_premium=False
        )
        
        with pytest.raises(ValueError, match="Monobank token and account ID are required"):
            user.switch_to_auto_mode(mono_token="", mono_account_id="account")
    
    def test_enable_premium(self):
        """Test enabling premium subscription."""
        user = User(
            id=1,
            email="test@example.com",
            tracking_mode=TrackingMode.MANUAL,
            is_premium=False
        )
        
        user.enable_premium()
        
        assert user.is_premium is True
    
    def test_disable_premium(self):
        """Test disabling premium subscription."""
        user = User(
            id=1,
            email="test@example.com",
            tracking_mode=TrackingMode.MANUAL,
            is_premium=True
        )
        
        user.disable_premium()
        
        assert user.is_premium is False
    
    def test_user_string_representation(self):
        """Test __str__ method."""
        user = User(
            id=42,
            email="test@example.com",
            tracking_mode=TrackingMode.MANUAL,
            is_premium=True
        )
        
        result = str(user)
        
        assert "42" in result
        assert "test@example.com" in result
        assert "True" in result
