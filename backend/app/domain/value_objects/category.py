"""
Category Value Object - Specific transaction categories with budget type mapping.

Each category automatically maps to NEEDS/WANTS/SAVINGS for 50/30/20 rule.
"""
from enum import Enum
from typing import List, Optional


class BudgetType(str, Enum):
    """Budget types for 50/30/20 rule."""
    NEEDS = "NEEDS"      # 50% - essentials
    WANTS = "WANTS"      # 30% - lifestyle
    SAVINGS = "SAVINGS"  # 20% - future


class Category(str, Enum):
    """
    Transaction categories with automatic budget type classification.
    
    Each category belongs to one budget type (NEEDS/WANTS/SAVINGS)
    for automatic 50/30/20 budget tracking.
    """
    
    # ==================== NEEDS (50%) ====================
    HOUSING = "HOUSING"
    UTILITIES = "UTILITIES"
    GROCERIES = "GROCERIES"
    TRANSPORT = "TRANSPORT"
    INSURANCE = "INSURANCE"
    HEALTHCARE = "HEALTHCARE"
    
    # ==================== WANTS (30%) ====================
    ENTERTAINMENT = "ENTERTAINMENT"
    RESTAURANTS = "RESTAURANTS"
    SHOPPING = "SHOPPING"
    HOBBIES = "HOBBIES"
    TRAVEL = "TRAVEL"
    BEAUTY = "BEAUTY"
    
    # ==================== SAVINGS (20%) ====================
    SAVINGS_ACCOUNT = "SAVINGS_ACCOUNT"
    INVESTMENTS = "INVESTMENTS"
    DEBT_REPAYMENT = "DEBT_REPAYMENT"
    
    # ==================== SPECIAL ====================
    INCOME = "INCOME"
    OTHER = "OTHER"
    
    def get_budget_type(self) -> Optional[BudgetType]:
        """
        Get the budget type (NEEDS/WANTS/SAVINGS) for this category.
        
        Returns:
            BudgetType: The budget type this category belongs to
            None: For INCOME category (doesn't belong to any budget)
        """
        # Use string value as key
        metadata = _CATEGORY_METADATA.get(self.value)
        return metadata["budget_type"] if metadata else None
    
    @property
    def display_name_ua(self) -> str:
        """Get Ukrainian display name."""
        metadata = _CATEGORY_METADATA.get(self.value)
        return metadata["display_name_ua"] if metadata else self.value
    
    @property
    def icon(self) -> str:
        """Get SF Symbol icon name."""
        metadata = _CATEGORY_METADATA.get(self.value)
        return metadata["icon"] if metadata else "questionmark.circle"
    
    @classmethod
    def get_all_by_budget_type(cls, budget_type: BudgetType) -> List["Category"]:
        """Get all categories that belong to a specific budget type."""
        return [
            category for category in cls
            if category.get_budget_type() == budget_type
        ]
    
    @classmethod
    def get_needs_categories(cls) -> List["Category"]:
        """Get all NEEDS categories (50% budget)."""
        return cls.get_all_by_budget_type(BudgetType.NEEDS)
    
    @classmethod
    def get_wants_categories(cls) -> List["Category"]:
        """Get all WANTS categories (30% budget)."""
        return cls.get_all_by_budget_type(BudgetType.WANTS)
    
    @classmethod
    def get_savings_categories(cls) -> List["Category"]:
        """Get all SAVINGS categories (20% budget)."""
        return cls.get_all_by_budget_type(BudgetType.SAVINGS)


# Metadata defined AFTER enum to avoid circular reference
_CATEGORY_METADATA = {
    # NEEDS (50%)
    "HOUSING": {
        "budget_type": BudgetType.NEEDS,
        "display_name_ua": "Житло",
        "icon": "house.fill"
    },
    "UTILITIES": {
        "budget_type": BudgetType.NEEDS,
        "display_name_ua": "Комунальні",
        "icon": "bolt.fill"
    },
    "GROCERIES": {
        "budget_type": BudgetType.NEEDS,
        "display_name_ua": "Продукти",
        "icon": "cart.fill"
    },
    "TRANSPORT": {
        "budget_type": BudgetType.NEEDS,
        "display_name_ua": "Транспорт",
        "icon": "car.fill"
    },
    "INSURANCE": {
        "budget_type": BudgetType.NEEDS,
        "display_name_ua": "Страхування",
        "icon": "shield.fill"
    },
    "HEALTHCARE": {
        "budget_type": BudgetType.NEEDS,
        "display_name_ua": "Здоров'я",
        "icon": "cross.case.fill"
    },
    
    # WANTS (30%)
    "ENTERTAINMENT": {
        "budget_type": BudgetType.WANTS,
        "display_name_ua": "Розваги",
        "icon": "tv.fill"
    },
    "RESTAURANTS": {
        "budget_type": BudgetType.WANTS,
        "display_name_ua": "Ресторани",
        "icon": "fork.knife"
    },
    "SHOPPING": {
        "budget_type": BudgetType.WANTS,
        "display_name_ua": "Шопінг",
        "icon": "bag.fill"
    },
    "HOBBIES": {
        "budget_type": BudgetType.WANTS,
        "display_name_ua": "Хобі",
        "icon": "sportscourt.fill"
    },
    "TRAVEL": {
        "budget_type": BudgetType.WANTS,
        "display_name_ua": "Подорожі",
        "icon": "airplane"
    },
    "BEAUTY": {
        "budget_type": BudgetType.WANTS,
        "display_name_ua": "Краса",
        "icon": "sparkles"
    },
    
    # SAVINGS (20%)
    "SAVINGS_ACCOUNT": {
        "budget_type": BudgetType.SAVINGS,
        "display_name_ua": "Заощадження",
        "icon": "banknote.fill"
    },
    "INVESTMENTS": {
        "budget_type": BudgetType.SAVINGS,
        "display_name_ua": "Інвестиції",
        "icon": "chart.line.uptrend.xyaxis"
    },
    "DEBT_REPAYMENT": {
        "budget_type": BudgetType.SAVINGS,
        "display_name_ua": "Погашення боргів",
        "icon": "creditcard.fill"
    },
    
    # SPECIAL
    "INCOME": {
        "budget_type": None,
        "display_name_ua": "Дохід",
        "icon": "arrow.down.circle.fill"
    },
    "OTHER": {
        "budget_type": BudgetType.WANTS,
        "display_name_ua": "Інше",
        "icon": "questionmark.circle.fill"
    },
}
