from dataclasses import dataclass, field

from hotel.enums import RoomType, UserRole
from hotel.models.user import User


@dataclass
class Guest(User):
    """Customer account that can search rooms and manage their own bookings."""

    loyalty_points: int = 0
    membership_tier: str = "Standard"
    preferred_room_type: RoomType | None = None
    id_verified: bool = False
    nationality: str = ""
    bookings: list[str] = field(default_factory=list)

    def has_permission(self, permission: str) -> bool:
        """Guests are limited to self-service booking actions."""
        return permission in {
            "search_rooms",
            "create_booking",
            "cancel_booking",
            "view_own_bookings",
            "check_in",
            "check_out",
            "redeem_points",
        }

    def redeem_points(self, points: int) -> float:
        """Convert loyalty points into a dollar discount value."""
        if points <= 0 or points > self.loyalty_points:
            raise ValueError("Invalid points redemption request.")
        self.loyalty_points -= points
        return round(points * 0.1, 2)

    @classmethod
    def create(
        cls,
        user_id: str,
        full_name: str,
        email: str,
        password_hash: str,
        phone: str,
    ) -> "Guest":
        """Factory helper that ensures every new Guest has the guest role."""
        return cls(
            user_id=user_id,
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            phone=phone,
            role=UserRole.GUEST,
        )
