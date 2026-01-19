"""
Unit tests for Category value object.
"""
import pytest
from app.domain.value_objects.category import Category, BudgetType


class TestCategoryBasics:
    """Test basic Category enum functionality."""
    
    def test_category_enum_exists(self):
        """All categories should be defined."""
        assert Category.GROCERIES
        assert Category.HOUSING
        assert Category.RESTAURANTS
        assert Category.SAVINGS_ACCOUNT
    
    def test_category_values_are_strings(self):
        """Category values should be uppercase strings."""
        assert Category.GROCERIES.value == "GROCERIES"
        assert Category.HOUSING.value == "HOUSING"
        assert isinstance(Category.GROCERIES.value, str)


class TestBudgetTypeMapping:
    """Test budget type classification."""
    
    def test_needs_categories_return_needs_budget_type(self):
        """NEEDS categories should return BudgetType.NEEDS."""
        assert Category.GROCERIES.get_budget_type() == BudgetType.NEEDS
        assert Category.HOUSING.get_budget_type() == BudgetType.NEEDS
        assert Category.UTILITIES.get_budget_type() == BudgetType.NEEDS
        assert Category.TRANSPORT.get_budget_type() == BudgetType.NEEDS
        assert Category.INSURANCE.get_budget_type() == BudgetType.NEEDS
        assert Category.HEALTHCARE.get_budget_type() == BudgetType.NEEDS
    
    def test_wants_categories_return_wants_budget_type(self):
        """WANTS categories should return BudgetType.WANTS."""
        assert Category.RESTAURANTS.get_budget_type() == BudgetType.WANTS
        assert Category.ENTERTAINMENT.get_budget_type() == BudgetType.WANTS
        assert Category.SHOPPING.get_budget_type() == BudgetType.WANTS
        assert Category.HOBBIES.get_budget_type() == BudgetType.WANTS
        assert Category.TRAVEL.get_budget_type() == BudgetType.WANTS
        assert Category.BEAUTY.get_budget_type() == BudgetType.WANTS
    
    def test_savings_categories_return_savings_budget_type(self):
        """SAVINGS categories should return BudgetType.SAVINGS."""
        assert Category.SAVINGS_ACCOUNT.get_budget_type() == BudgetType.SAVINGS
        assert Category.INVESTMENTS.get_budget_type() == BudgetType.SAVINGS
        assert Category.DEBT_REPAYMENT.get_budget_type() == BudgetType.SAVINGS
    
    def test_income_category_returns_none(self):
        """INCOME category doesn't belong to any budget type."""
        assert Category.INCOME.get_budget_type() is None
    
    def test_other_category_defaults_to_wants(self):
        """OTHER category defaults to WANTS."""
        assert Category.OTHER.get_budget_type() == BudgetType.WANTS


class TestCategoryFiltering:
    """Test filtering categories by budget type."""
    
    def test_get_needs_categories(self):
        """Should return all NEEDS categories."""
        needs = Category.get_needs_categories()
        
        assert len(needs) == 6
        assert Category.GROCERIES in needs
        assert Category.HOUSING in needs
        assert Category.UTILITIES in needs
        assert Category.TRANSPORT in needs
        assert Category.INSURANCE in needs
        assert Category.HEALTHCARE in needs
        
        # Should NOT contain WANTS or SAVINGS
        assert Category.RESTAURANTS not in needs
        assert Category.SAVINGS_ACCOUNT not in needs
    
    def test_get_wants_categories(self):
        """Should return all WANTS categories."""
        wants = Category.get_wants_categories()
        
        assert len(wants) == 7  # Including OTHER
        assert Category.RESTAURANTS in wants
        assert Category.ENTERTAINMENT in wants
        assert Category.SHOPPING in wants
        assert Category.HOBBIES in wants
        assert Category.TRAVEL in wants
        assert Category.BEAUTY in wants
        assert Category.OTHER in wants
        
        # Should NOT contain NEEDS or SAVINGS
        assert Category.GROCERIES not in wants
        assert Category.SAVINGS_ACCOUNT not in wants
    
    def test_get_savings_categories(self):
        """Should return all SAVINGS categories."""
        savings = Category.get_savings_categories()
        
        assert len(savings) == 3
        assert Category.SAVINGS_ACCOUNT in savings
        assert Category.INVESTMENTS in savings
        assert Category.DEBT_REPAYMENT in savings
        
        # Should NOT contain NEEDS or WANTS
        assert Category.GROCERIES not in savings
        assert Category.RESTAURANTS not in savings
    
    def test_get_all_by_budget_type(self):
        """Generic method should work for any budget type."""
        needs = Category.get_all_by_budget_type(BudgetType.NEEDS)
        wants = Category.get_all_by_budget_type(BudgetType.WANTS)
        savings = Category.get_all_by_budget_type(BudgetType.SAVINGS)
        
        assert len(needs) == 6
        assert len(wants) == 7
        assert len(savings) == 3


class TestCategoryMetadata:
    """Test Ukrainian names and icons."""
    
    def test_ukrainian_display_names(self):
        """All categories should have Ukrainian names."""
        assert Category.GROCERIES.display_name_ua == "Продукти"
        assert Category.HOUSING.display_name_ua == "Житло"
        assert Category.RESTAURANTS.display_name_ua == "Ресторани"
        assert Category.SAVINGS_ACCOUNT.display_name_ua == "Заощадження"
    
    def test_icon_names(self):
        """All categories should have SF Symbol icons."""
        assert Category.GROCERIES.icon == "cart.fill"
        assert Category.HOUSING.icon == "house.fill"
        assert Category.RESTAURANTS.icon == "fork.knife"
        assert Category.TRAVEL.icon == "airplane"
    
    def test_all_categories_have_metadata(self):
        """Every category must have display name and icon."""
        for category in Category:
            assert category.display_name_ua is not None
            assert category.icon is not None
            assert isinstance(category.display_name_ua, str)
            assert isinstance(category.icon, str)


class TestCategoryBusinessLogic:
    """Test business logic scenarios."""
    
    def test_50_30_20_rule_distribution(self):
        """Categories should support 50/30/20 rule."""
        needs = Category.get_needs_categories()
        wants = Category.get_wants_categories()
        savings = Category.get_savings_categories()
        
        # Should have categories in all three buckets
        assert len(needs) > 0, "Should have NEEDS categories"
        assert len(wants) > 0, "Should have WANTS categories"
        assert len(savings) > 0, "Should have SAVINGS categories"
        
        # Verify no overlap
        all_budget_categories = needs + wants + savings
        unique_categories = set(all_budget_categories)
        assert len(all_budget_categories) == len(unique_categories), "No category should belong to multiple budget types"
    
    def test_transaction_can_determine_budget_impact(self):
        """Transaction with category can determine which budget bucket to impact."""
        # Simulate transaction logic
        transaction_category = Category.GROCERIES
        budget_type = transaction_category.get_budget_type()
        
        assert budget_type == BudgetType.NEEDS
        # This would affect the NEEDS (50%) budget bucket
    
    def test_income_category_special_handling(self):
        """Income transactions shouldn't affect budget buckets."""
        income_category = Category.INCOME
        budget_type = income_category.get_budget_type()
        
        assert budget_type is None
        # Income increases total budget, not consumed from any bucket
