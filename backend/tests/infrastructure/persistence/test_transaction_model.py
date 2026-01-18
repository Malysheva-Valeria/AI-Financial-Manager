"""
Integration tests for TransactionModel ORM.
Tests database operations, validators, and relationships.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select
from pydantic import ValidationError

from app.infrastructure.persistence.transaction_model import (
    TransactionModel,
    TransactionTypeEnum,
    TransactionSourceEnum,
    BudgetCategoryEnum
)
from app.infrastructure.persistence.user_model import UserModel


class TestTransactionModel:
    """Test TransactionModel database operations and validation."""
    
    def test_create_transaction_in_database(self, session: Session):
        """Test creating a transaction and persisting to database."""
        # First create a user
        user = UserModel(
            email="test@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create transaction
        transaction = TransactionModel(
            user_id=user.id,
            amount=Decimal("-100.50"),
            currency="UAH",
            description="Groceries at ATB",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE
        )
        
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        
        assert transaction.id is not None
        assert transaction.user_id == user.id
        assert transaction.amount == Decimal("-100.50")
        assert transaction.category == BudgetCategoryEnum.NEEDS
        assert transaction.created_at is not None
    
    def test_zero_amount_raises_validation_error(self):
        """Test that amount cannot be zero."""
        with pytest.raises(ValidationError, match="Amount cannot be zero"):
            TransactionModel(
                user_id=1,
                amount=Decimal("0"),
                description="Test",
                category=BudgetCategoryEnum.NEEDS,
                transaction_type=TransactionTypeEnum.EXPENSE
            )
    
    def test_empty_description_raises_validation_error(self):
        """Test that description cannot be empty."""
        with pytest.raises(ValidationError, match="Description cannot be empty"):
            TransactionModel(
                user_id=1,
                amount=Decimal("-50.00"),
                description="",
                category=BudgetCategoryEnum.NEEDS,
                transaction_type=TransactionTypeEnum.EXPENSE
            )
    
    def test_whitespace_description_raises_validation_error(self):
        """Test that whitespace-only description is invalid."""
        with pytest.raises(ValidationError, match="Description cannot be empty"):
            TransactionModel(
                user_id=1,
                amount=Decimal("-50.00"),
                description="   ",
                category=BudgetCategoryEnum.NEEDS,
                transaction_type=TransactionTypeEnum.EXPENSE
            )
    
    def test_description_strips_whitespace(self):
        """Test that description whitespace is stripped."""
        transaction = TransactionModel(
            user_id=1,
            amount=Decimal("-50.00"),
            description="  Groceries  ",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE
        )
        
        assert transaction.description == "Groceries"
    
    def test_currency_normalized_to_uppercase(self):
        """Test that currency is normalized to uppercase."""
        transaction = TransactionModel(
            user_id=1,
            amount=Decimal("-50.00"),
            description="Test",
            currency="uah",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE
        )
        
        assert transaction.currency == "UAH"
    
    def test_default_currency_is_uah(self):
        """Test that default currency is UAH."""
        transaction = TransactionModel(
            user_id=1,
            amount=Decimal("-50.00"),
            description="Test",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE
        )
        
        assert transaction.currency == "UAH"
    
    def test_default_source_is_manual(self):
        """Test that default source is MANUAL."""
        transaction = TransactionModel(
            user_id=1,
            amount=Decimal("-50.00"),
            description="Test",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE
        )
        
        assert transaction.source == TransactionSourceEnum.MANUAL
    
    def test_default_is_ai_categorized_is_false(self):
        """Test that default is_ai_categorized is False."""
        transaction = TransactionModel(
            user_id=1,
            amount=Decimal("-50.00"),
            description="Test",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE
        )
        
        assert transaction.is_ai_categorized is False
    
    def test_foreign_key_relationship(self, session: Session):
        """Test relationship between User and Transaction."""
        # Create user
        user = UserModel(
            email="relation@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create transactions
        t1 = TransactionModel(
            user_id=user.id,
            amount=Decimal("-100.00"),
            description="Expense 1",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE
        )
        t2 = TransactionModel(
            user_id=user.id,
            amount=Decimal("1000.00"),
            description="Income",
            category=BudgetCategoryEnum.SAVINGS,
            transaction_type=TransactionTypeEnum.INCOME
        )
        
        session.add_all([t1, t2])
        session.commit()
        
        # Refresh user to load transactions
        session.refresh(user)
        
        assert len(user.transactions) == 2
    
    def test_cascade_delete(self, session: Session):
        """Test that deleting user deletes transactions."""
        # Create user with transaction
        user = UserModel(
            email="cascade@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        transaction = TransactionModel(
            user_id=user.id,
            amount=Decimal("-50.00"),
            description="Test",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE
        )
        session.add(transaction)
        session.commit()
        
        transaction_id = transaction.id
        
        # Delete user
        session.delete(user)
        session.commit()
        
        # Verify transaction is also deleted
        statement = select(TransactionModel).where(TransactionModel.id == transaction_id)
        result = session.exec(statement).first()
        
        assert result is None
    
    def test_soft_delete_pattern(self, session: Session):
        """Test soft delete with deleted_at field."""
        # Create user
        user = UserModel(
            email="softdelete@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create transaction
        transaction = TransactionModel(
            user_id=user.id,
            amount=Decimal("-50.00"),
            description="Test",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        
        assert transaction.deleted_at is None
        
        # Soft delete
        transaction.deleted_at = datetime.now(timezone.utc)
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        
        assert transaction.deleted_at is not None
    
    def test_monobank_transaction_id_unique(self, session: Session):
        """Test that mono_transaction_id must be unique."""
        user = UserModel(
            email="mono@example.com",
            password_hash="$2b$12$" + "x" * 50
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # First transaction with mono_transaction_id
        t1 = TransactionModel(
            user_id=user.id,
            amount=Decimal("-50.00"),
            description="Test 1",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE,
            mono_transaction_id="mono_123"
        )
        session.add(t1)
        session.commit()
        
        # Try to create another with same mono_transaction_id
        t2 = TransactionModel(
            user_id=user.id,
            amount=Decimal("-100.00"),
            description="Test 2",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE,
            mono_transaction_id="mono_123"
        )
        session.add(t2)
        
        with pytest.raises(Exception):  # IntegrityError
            session.commit()
    
    def test_transaction_repr(self):
        """Test __repr__ method."""
        transaction = TransactionModel(
            user_id=1,
            amount=Decimal("-100.50"),
            description="Groceries at ATB supermarket",
            category=BudgetCategoryEnum.NEEDS,
            transaction_type=TransactionTypeEnum.EXPENSE
        )
        
        repr_str = repr(transaction)
        
        assert "TransactionModel" in repr_str
        assert "-100.50" in repr_str
        assert "UAH" in repr_str
        assert "Groceries" in repr_str
