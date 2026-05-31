from enum import Enum


class RoomType(Enum):
    """Supported room categories used for search and pricing."""

    SINGLE = "single"
    DOUBLE = "double"
    SUITE = "suite"
    PENTHOUSE = "penthouse"
    ACCESSIBLE = "accessible"


class RoomStatus(Enum):
    """Operational room states used by booking and maintenance workflows."""

    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"
    CLEANING = "cleaning"


class UserRole(Enum):
    """System roles used for access control."""

    GUEST = "guest"
    STAFF = "staff"
    SUPER_ADMIN = "super_admin"


class ShiftType(Enum):
    """Staff shift categories."""

    MORNING = "morning"
    EVENING = "evening"
    NIGHT = "night"


class BookingStatus(Enum):
    """Lifecycle states for a booking request/reservation."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELED = "canceled"


class ServiceCategory(Enum):
    """Categories for optional booking add-on services."""

    BREAKFAST = "breakfast"
    TRANSPORT = "transport"
    SPA = "spa"
    LAUNDRY = "laundry"
    OTHER = "other"


class Season(Enum):
    """Pricing seasons used to apply room rate multipliers."""

    LOW = "low"
    NORMAL = "normal"
    PEAK = "peak"


class ReportType(Enum):
    """Types of reports the admin system can generate."""

    OCCUPANCY = "occupancy"
    REVENUE = "revenue"
    MAINTENANCE = "maintenance"
    FULL = "full"
