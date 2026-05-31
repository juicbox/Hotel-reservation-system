from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from hotel.enums import UserRole


@dataclass
class User(ABC):
    """Base account model shared by guests, staff, and administrators."""

    user_id: str
    full_name: str
    email: str
    password_hash: str
    phone: str
    role: UserRole
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def login(self, email: str, password_hash: str) -> bool:
        """Return True when credentials match an active user account."""
        return self.is_active and self.email == email and self.password_hash == password_hash

    def logout(self) -> None:
        return None

    def update_profile(self, full_name: str | None = None, phone: str | None = None) -> None:
        """Update only the profile fields supplied by the caller."""
        if full_name:
            self.full_name = full_name
        if phone:
            self.phone = phone

    def get_role(self) -> UserRole:
        return self.role

    def reset_password(self, new_hash: str) -> None:
        if not new_hash:
            raise ValueError("Password hash cannot be empty.")
        self.password_hash = new_hash

    @abstractmethod
    def has_permission(self, permission: str) -> bool:
        """Subclasses define which actions their role is allowed to perform."""
        raise NotImplementedError
