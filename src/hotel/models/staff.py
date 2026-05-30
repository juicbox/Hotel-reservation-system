from dataclasses import dataclass, field
from datetime import date

from hotel.enums import ShiftType, UserRole
from hotel.models.user import User


@dataclass
class Staff(User):
    staff_id: str = ""
    department: str = ""
    shift: ShiftType = ShiftType.MORNING
    employed_since: date | None = None
    managed_rooms: list[str] = field(default_factory=list)
    access_level: int = 1

    def has_permission(self, permission: str) -> bool:
        common_permissions = {
            "search_rooms",
            "view_guest_bookings",
            "process_check_in",
            "process_check_out",
            "add_service_to_booking",
            "update_booking_notes",
            "approve_booking",
            "deny_booking",
        }
        maintenance_permissions = {"mark_room_cleaned", "flag_maintenance"}
        if permission in common_permissions:
            return True
        if permission in maintenance_permissions:
            return self.access_level >= 2
        return False

    @classmethod
    def create(
        cls,
        user_id: str,
        full_name: str,
        email: str,
        password_hash: str,
        phone: str,
        access_level: int = 1,
    ) -> "Staff":
        return cls(
            user_id=user_id,
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            phone=phone,
            role=UserRole.STAFF,
            staff_id=user_id,
            access_level=access_level,
        )
