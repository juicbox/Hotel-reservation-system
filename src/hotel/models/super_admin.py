from dataclasses import dataclass, field

from hotel.enums import UserRole
from hotel.models.staff import Staff


@dataclass
class SuperAdmin(Staff):
    """Administrator account with unrestricted access to system functions."""

    system_permissions: set[str] = field(default_factory=lambda: {"all"})
    audit_log_access: bool = True
    override_enabled: bool = True
    managed_staff: list[str] = field(default_factory=list)
    report_recipient: str = ""

    def has_permission(self, permission: str) -> bool:
        """Super admins can perform any supported permission."""
        _ = permission
        return True

    @classmethod
    def create(
        cls,
        user_id: str,
        full_name: str,
        email: str,
        password_hash: str,
        phone: str,
    ) -> "SuperAdmin":
        """Factory helper that creates an administrator with top access level."""
        return cls(
            user_id=user_id,
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            phone=phone,
            role=UserRole.SUPER_ADMIN,
            staff_id=user_id,
            access_level=4,
        )
