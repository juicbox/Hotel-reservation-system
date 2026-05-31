from __future__ import annotations

from datetime import date
from uuid import uuid4

from hotel.enums import BookingStatus, ReportType, RoomStatus, RoomType, Season, UserRole
from hotel.models import Booking, Guest, Report, Room, Service, Staff, SuperAdmin, User


class HotelSystem:
    """Singleton system manager that owns rooms, users, bookings and services."""

    _instance: "HotelSystem | None" = None

    def __init__(self) -> None:
        self.rooms: dict[str, Room] = {}
        self.users: dict[str, User] = {}
        self.bookings: dict[str, Booking] = {}
        self.services: dict[str, Service] = {}
        self.current_season: Season = Season.NORMAL

    @classmethod
    def get_instance(cls) -> "HotelSystem":
        """Return the shared singleton instance used by the console app."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> "HotelSystem":
        """Create a fresh singleton instance, useful for Streamlit session startup."""
        cls._instance = cls()
        return cls._instance

    def add_room(self, room: Room) -> None:
        self.rooms[room.room_id] = room

    def remove_room(self, room_id: str) -> bool:
        """Remove a room only when it has no active bookings."""
        if room_id not in self.rooms:
            return False
        has_active = any(
            booking.room_id == room_id and booking.is_active for booking in self.bookings.values()
        )
        if has_active:
            return False
        del self.rooms[room_id]
        return True

    def add_user(self, user: User) -> None:
        self.users[user.user_id] = user

    def add_service_catalog_item(self, service: Service) -> None:
        self.services[service.service_id] = service

    def authenticate(self, email: str, password_hash: str) -> User | None:
        """Find an active user whose credentials match the login request."""
        for user in self.users.values():
            if user.login(email, password_hash):
                return user
        return None

    def search_rooms(
        self,
        room_id: str | None = None,
        room_type: RoomType | None = None,
        min_capacity: int | None = None,
        max_rate: float | None = None,
        check_in: date | None = None,
        check_out: date | None = None,
    ) -> list[Room]:
        """Search rooms using optional guest-facing filters."""
        results = []
        for room in self.rooms.values():
            if room_id and room.room_id != room_id:
                continue
            if room_type and room.room_type != room_type:
                continue
            if min_capacity and room.capacity < min_capacity:
                continue
            if max_rate and room.get_effective_rate(date.today()) > max_rate:
                continue
            if check_in and check_out and not room.is_available(
                check_in, check_out, self.bookings.values()
            ):
                continue
            results.append(room)
        return results

    def create_booking(
        self,
        guest_id: str,
        room_id: str,
        check_in: date,
        check_out: date,
        created_by: str,
        service_items: list[Service] | None = None,
    ) -> Booking:
        """Create a pending booking request for a valid guest and available room."""
        if guest_id not in self.users or self.users[guest_id].role != UserRole.GUEST:
            raise ValueError("Guest ID is invalid.")
        if room_id not in self.rooms:
            raise ValueError("Room ID is invalid.")
        room = self.rooms[room_id]
        if not room.is_available(check_in, check_out, self.bookings.values()):
            raise ValueError("Room is not available for the selected dates.")

        booking = Booking(
            booking_id=f"B-{uuid4().hex[:8].upper()}",
            guest_id=guest_id,
            room_id=room_id,
            check_in_date=check_in,
            check_out_date=check_out,
            created_by=created_by,
            status=BookingStatus.PENDING,
        )

        for service in service_items or []:
            booking.add_service(service)
        booking.compute_charges(room.base_nightly_rate, room.seasonal_multiplier)

        # Keep both the central booking collection and the guest history in sync.
        self.bookings[booking.booking_id] = booking
        guest = self.users[guest_id]
        if isinstance(guest, Guest):
            guest.bookings.append(booking.booking_id)
        room.current_status = RoomStatus.RESERVED
        return booking

    def update_booking_dates(self, booking_id: str, check_in: date, check_out: date) -> bool:
        """Update booking dates if the new range is valid and not double-booked."""
        booking = self.bookings.get(booking_id)
        if booking is None:
            return False
        if not booking.modify(check_in, check_out):
            return False
        if not booking.validate_overlap(list(self.bookings.values())):
            return False
        room = self.rooms[booking.room_id]
        booking.compute_charges(room.base_nightly_rate, room.seasonal_multiplier)
        return True

    def cancel_booking(self, booking_id: str, reason: str) -> bool:
        """Cancel an active booking and make the room available if possible."""
        booking = self.bookings.get(booking_id)
        if booking is None or not booking.is_active:
            return False
        booking.cancel(reason)
        self._refresh_room_status(booking.room_id)
        return True

    def complete_booking(self, booking_id: str) -> dict | None:
        """Mark a booking as checked out and return its invoice."""
        booking = self.bookings.get(booking_id)
        if booking is None:
            return None
        booking.status = BookingStatus.CHECKED_OUT
        invoice = booking.generate_invoice()
        guest = self.users.get(booking.guest_id)
        if isinstance(guest, Guest):
            guest.loyalty_points += int(booking.total_charges // 20)
        self._refresh_room_status(booking.room_id)
        return invoice

    def process_booking_request(self, booking_id: str, approve: bool) -> bool:
        """Approve or deny a pending booking from the admin portal."""
        booking = self.bookings.get(booking_id)
        if booking is None or booking.status != BookingStatus.PENDING:
            return False
        booking.status = BookingStatus.CONFIRMED if approve else BookingStatus.CANCELED
        if not approve:
            self._refresh_room_status(booking.room_id)
        return True

    def add_service_to_booking(self, booking_id: str, service: Service) -> bool:
        booking = self.bookings.get(booking_id)
        if booking is None:
            return False
        booking.add_service(service)
        room = self.rooms[booking.room_id]
        booking.compute_charges(room.base_nightly_rate, room.seasonal_multiplier)
        return True

    def list_active_bookings(self) -> list[Booking]:
        return [booking for booking in self.bookings.values() if booking.is_active]

    def get_user_history(self, guest_id: str) -> list[Booking]:
        return [booking for booking in self.bookings.values() if booking.guest_id == guest_id]

    def apply_seasonal_pricing(self, season: Season) -> None:
        """Apply the selected seasonal multiplier to every room."""
        self.current_season = season
        multipliers = {Season.LOW: 0.85, Season.NORMAL: 1.0, Season.PEAK: 1.35}
        multiplier = multipliers[season]
        for room in self.rooms.values():
            room.seasonal_multiplier = multiplier

    def generate_report(self, report_type: ReportType, generated_by: str) -> Report:
        """Build a current operational report for the admin UI."""
        total_rooms = len(self.rooms)
        active_bookings = self.list_active_bookings()
        occupied_rooms = len({booking.room_id for booking in active_bookings})
        occupancy = (occupied_rooms / total_rooms * 100) if total_rooms else 0.0
        revenue = sum(booking.total_charges for booking in self.bookings.values())

        data = {
            "occupancy_rate": round(occupancy, 2),
            "revenue_summary": {"total_revenue": round(revenue, 2)},
            "active_bookings": len(active_bookings),
            "season": self.current_season.value,
        }
        return Report(
            report_id=f"R-{uuid4().hex[:8].upper()}",
            report_type=report_type,
            generated_by=generated_by,
            period="Current Snapshot",
            data=data,
        )

    def _refresh_room_status(self, room_id: str) -> None:
        """Recalculate room status after booking approval, cancellation, or checkout."""
        room = self.rooms.get(room_id)
        if room is None:
            return
        has_active = any(
            booking.room_id == room_id and booking.is_active for booking in self.bookings.values()
        )
        if room.current_status not in {RoomStatus.MAINTENANCE, RoomStatus.CLEANING}:
            room.current_status = RoomStatus.RESERVED if has_active else RoomStatus.AVAILABLE


def build_user_from_role(
    role: UserRole,
    user_id: str,
    full_name: str,
    email: str,
    password_hash: str,
    phone: str,
    access_level: int = 1,
) -> User:
    """Rebuild the correct User subclass when loading users from Excel."""
    if role == UserRole.GUEST:
        return Guest.create(user_id, full_name, email, password_hash, phone)
    if role == UserRole.STAFF:
        return Staff.create(user_id, full_name, email, password_hash, phone, access_level)
    if role == UserRole.SUPER_ADMIN:
        return SuperAdmin.create(user_id, full_name, email, password_hash, phone)
    raise ValueError(f"Unsupported role: {role}")
