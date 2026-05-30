from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from hotel.enums import BookingStatus
from hotel.models.service import Service


@dataclass
class Booking:
    booking_id: str
    guest_id: str
    room_id: str
    check_in_date: date
    check_out_date: date
    status: BookingStatus = BookingStatus.PENDING
    services: list[Service] = field(default_factory=list)
    total_charges: float = 0.0
    deposit_paid: float = 0.0
    notes: str = ""
    created_by: str = ""
    modified_at: datetime = field(default_factory=datetime.now)

    @property
    def is_active(self) -> bool:
        return self.status in {
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED,
            BookingStatus.CHECKED_IN,
        }

    def overlaps(self, check_in: date, check_out: date) -> bool:
        return check_in < self.check_out_date and check_out > self.check_in_date

    def validate_overlap(self, existing_bookings: list["Booking"]) -> bool:
        for booking in existing_bookings:
            if booking.booking_id == self.booking_id:
                continue
            if booking.room_id != self.room_id or not booking.is_active:
                continue
            if self.overlaps(booking.check_in_date, booking.check_out_date):
                return False
        return True

    def compute_charges(self, nightly_rate: float, seasonal_multiplier: float = 1.0) -> float:
        nights = (self.check_out_date - self.check_in_date).days
        if nights <= 0:
            raise ValueError("Check-out must be after check-in.")
        room_cost = nights * nightly_rate * seasonal_multiplier
        service_cost = sum(service.get_total_cost() for service in self.services)
        self.total_charges = round(room_cost + service_cost, 2)
        self.modified_at = datetime.now()
        return self.total_charges

    def add_service(self, service: Service) -> None:
        self.services.append(service)
        self.modified_at = datetime.now()

    def modify(self, check_in: date, check_out: date, notes: str = "") -> bool:
        if check_out <= check_in:
            return False
        self.check_in_date = check_in
        self.check_out_date = check_out
        if notes:
            self.notes = notes
        self.modified_at = datetime.now()
        return True

    def cancel(self, reason: str) -> None:
        self.status = BookingStatus.CANCELED
        self.notes = reason
        self.modified_at = datetime.now()

    def generate_invoice(self) -> dict:
        return {
            "booking_id": self.booking_id,
            "guest_id": self.guest_id,
            "room_id": self.room_id,
            "total_charges": self.total_charges,
            "deposit_paid": self.deposit_paid,
            "balance_due": round(self.total_charges - self.deposit_paid, 2),
            "services": [service.get_description() for service in self.services],
        }
