from dataclasses import dataclass, field
from datetime import date
from typing import Iterable

from hotel.enums import RoomStatus, RoomType


@dataclass
class Room:
    room_id: str
    room_number: str
    room_type: RoomType
    floor: int
    capacity: int
    base_nightly_rate: float
    current_status: RoomStatus = RoomStatus.AVAILABLE
    seasonal_multiplier: float = 1.0
    amenities: list[str] = field(default_factory=list)

    def get_effective_rate(self, booking_date: date) -> float:
        """Return effective nightly rate for a given day."""
        _ = booking_date  # rate can evolve per date in the future
        return round(self.base_nightly_rate * self.seasonal_multiplier, 2)

    def is_available(self, check_in: date, check_out: date, room_bookings: Iterable) -> bool:
        """Check if this room is free for the requested period."""
        if self.current_status in {RoomStatus.MAINTENANCE, RoomStatus.CLEANING}:
            return False

        for booking in room_bookings:
            if booking.room_id != self.room_id:
                continue
            if booking.is_active and booking.overlaps(check_in, check_out):
                return False
        return True

    def set_maintenance(self, flag: bool) -> None:
        self.current_status = RoomStatus.MAINTENANCE if flag else RoomStatus.AVAILABLE

    def update_rate(self, new_rate: float, admin_id: str) -> None:
        if new_rate <= 0:
            raise ValueError("Nightly rate must be greater than zero.")
        _ = admin_id  # kept for audit extension
        self.base_nightly_rate = round(new_rate, 2)
