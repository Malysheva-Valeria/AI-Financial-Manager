"""
Unit tests for Transaction domain entity.
Tests pure business logic without database dependencies.
"""
import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.domain.entities.transaction import Transaction
from app.domain.value_objects.transaction_type import TransactionType
from app.domain.value_objects.transaction_source import TransactionSource
from app.domain.value_objects.budget_category import BudgetCategory


class TestTransactionEntity:
    """Test Transaction domain entity business logic."""
    
    def test_transaction_creation(self):
        """Test basic transaction creation."""
        transaction = Transaction(
            id=1,
            user_id=1,
            amount=Decimal("-50.00"),
            currency="UAH",
            description="Groceries",
            category=BudgetCategory.NEEDS,
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL
        )
        
        assert transaction.id == 1
        assert transaction.amount == Decimal("-50.00")
        assert transaction.category == BudgetCategory.NEEDS
    
    def test_expense_is_expense(self):
        """Test that expense transaction is identified correctly."""
        transaction = Transaction(
            id=1,
            user_id=1,
            amount=Decimal("-100.00"),
            currency="UAH",
            description="Test",
            category=BudgetCategory.NEEDS,
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL
        )
        
        assert transaction.is_expense() is True
        assert transaction.is_income() is False
    
    def test_income_is_income(self):
        """Test that income transaction is identified correctly."""
        transaction = Transaction(
            id=1,
            user_id=1,
            amount=Decimal("1000.00"),
            currency="UAH",
            description="Salary",
            category=BudgetCategory.SAVINGS,
            transaction_type=TransactionType.INCOME,
            source=TransactionSource.MANUAL
        )
        
        assert transaction.is_income() is True
        assert transaction.is_expense() is False
    
    def test_manual_transaction_is_manual(self):
        """Test manual transaction identification."""
        transaction = Transaction(
            id=1,
            user_id=1,
            amount=Decimal("-50.00"),
            currency="UAH",
            description="Cash",
            category=BudgetCategory.NEEDS,
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL
        )
        
        assert transaction.is_manual() is True
        assert transaction.is_from_bank() is False
    
    def test_monobank_transaction_is_from_bank(self):
        """Test Monobank transaction identification."""
        transaction = Transaction(
            id=1,
            user_id=1,
            amount=Decimal("-50.00"),
            currency="UAH",
            description="Card payment",
            category=BudgetCategory.WANTS,
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MONOBANK,
            mono_transaction_id="mono_123"
        )
        
        assert transaction.is_from_bank() is True
        assert transaction.is_manual() is False
    
    def test_soft_delete(self):
        """Test soft delete functionality."""
        transaction = Transaction(
            id=1,
            user_id=1,
            amount=Decimal("-50.00"),
            currency="UAH",
            description="Test",
            category=BudgetCategory.NEEDS,
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL
        )
        
        assert transaction.is_deleted() is False
        assert transaction.deleted_at is None
        
        transaction.soft_delete()
        
        assert transaction.is_deleted() is True
        assert transaction.deleted_at is not None
    
    def test_restore_deleted_transaction(self):
        """Test restoring soft-deleted transaction."""
        transaction = Transaction(
            id=1,
            user_id=1,
            amount=Decimal("-50.00"),
            currency="UAH",
            description="Test",
            category=BudgetCategory.NEEDS,
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL
        )
        
        transaction.soft_delete()
        assert transaction.is_deleted() is True
        
        transaction.restore()
        assert transaction.is_deleted() is False
        assert transaction.deleted_at is None
    
    def test_get_absolute_amount(self):
        """Test getting absolute value of amount."""
        expense = Transaction(
            id=1,
            user_id=1,
            amount=Decimal("-150.50"),
            currency="UAH",
            description="Expense",
            category=BudgetCategory.NEEDS,
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL
        )
        
        assert expense.get_absolute_amount() == Decimal("150.50")
        
        income = Transaction(
            id=2,
            user_id=1,
            amount=Decimal("1000.00"),
            currency="UAH",
            description="Income",
            category=BudgetCategory.SAVINGS,
            transaction_type=TransactionType.INCOME,
            source=TransactionSource.MANUAL
        )
        
        assert income.get_absolute_amount() == Decimal("1000.00")
    
    def test_ai_categorization(self):
        """Test AI categorization."""
        transaction = Transaction(
            id=1,
            user_id=1,
            amount=Decimal("-50.00"),
            currency="UAH",
            description="ATB Market",
            category=BudgetCategory.WANTS,  # Initially wrong
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL,
            is_ai_categorized=False
        )
        
        assert transaction.is_ai_categorized is False
        
        transaction.categorize_with_ai(BudgetCategory.NEEDS)
        
        assert transaction.category == BudgetCategory.NEEDS
        assert transaction.is_ai_categorized is True
    
    def test_manual_recategorization(self):
        """Test manual category change."""
        transaction = Transaction(
            id=1,
            user_id=1,
            amount=Decimal("-50.00"),
            currency="UAH",
            description="Restaurant",
            category=BudgetCategory.NEEDS,
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL,
            is_ai_categorized=True  # Was AI categorized
        )
        
        transaction.manually_recategorize(BudgetCategory.WANTS)
        
        assert transaction.category == BudgetCategory.WANTS
        assert transaction.is_ai_categorized is False
    
    def test_string_representation(self):
        """Test __str__ method."""
        expense = Transaction(
            id=1,
            user_id=1,
            amount=Decimal("-100.00"),
            currency="UAH",
            description="Groceries",
            category=BudgetCategory.NEEDS,
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL
        )
        
        result = str(expense)
        assert "-100" in result
        assert "UAH" in result
        assert "Groceries" in result
        
        income = Transaction(
            id=2,
            user_id=1,
            amount=Decimal("1000.00"),
            currency="UAH",
            description="Salary",
            category=BudgetCategory.SAVINGS,
            transaction_type=TransactionType.INCOME,
            source=TransactionSource.MANUAL
        )
        
        result = str(income)
        assert "+1000" in result or "1000" in result
