from enum import Enum


class RoomType(Enum):
    SINGLE = "single"
    DOUBLE = "double"
    SUITE = "suite"
    PENTHOUSE = "penthouse"
    ACCESSIBLE = "accessible"


class RoomStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"
    CLEANING = "cleaning"


class UserRole(Enum):
    GUEST = "guest"
    STAFF = "staff"
    SUPER_ADMIN = "super_admin"


class ShiftType(Enum):
    MORNING = "morning"
    EVENING = "evening"
    NIGHT = "night"


class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELED = "canceled"


class ServiceCategory(Enum):
    BREAKFAST = "breakfast"
    TRANSPORT = "transport"
    SPA = "spa"
    LAUNDRY = "laundry"
    OTHER = "other"


class Season(Enum):
    LOW = "low"
    NORMAL = "normal"
    PEAK = "peak"


class ReportType(Enum):
    OCCUPANCY = "occupancy"
    REVENUE = "revenue"
    MAINTENANCE = "maintenance"
    FULL = "full"
