from dataclasses import dataclass
from datetime import date

from hotel.enums import ServiceCategory


@dataclass
class Service:
    """Optional add-on service that can be attached to a booking."""

    service_id: str
    name: str
    category: ServiceCategory
    unit_price: float
    quantity: int = 1
    applied_date: date | None = None

    def get_total_cost(self) -> float:
        """Calculate the total service charge for the selected quantity."""
        return round(self.unit_price * self.quantity, 2)

    def apply_discount(self, percentage: float) -> None:
        """Apply a percentage discount to the service unit price."""
        if percentage < 0 or percentage > 100:
            raise ValueError("Discount must be between 0 and 100.")
        multiplier = (100 - percentage) / 100
        self.unit_price = round(self.unit_price * multiplier, 2)

    def get_category(self) -> ServiceCategory:
        return self.category

    def get_description(self) -> str:
        return f"{self.name} ({self.category.value}) x{self.quantity}"

    def is_available(self, usage_date: date) -> bool:
        """Placeholder availability check for future date-based service rules."""
        _ = usage_date
        return True
