from __future__ import annotations

from datetime import date
from pathlib import Path

from hotel.enums import ReportType, RoomStatus, RoomType, Season, ServiceCategory, UserRole
from hotel.hotel_system import HotelSystem
from hotel.models import Room, Service
from hotel.preload import preload_data
from hotel.storage.excel_storage import ExcelStorage

DATA_FILE = Path("hotel_data.xlsx")


def parse_date(text: str) -> date:
    """Parse ISO dates entered in the console menu."""
    return date.fromisoformat(text.strip())


def prompt(msg: str) -> str:
    """Read trimmed console input."""
    return input(msg).strip()


def show_room(room) -> None:
    """Print one room in a compact console-friendly format."""
    print(
        f"{room.room_id:<8} {room.room_number:<6} {room.room_type.value:<10} "
        f"cap={room.capacity:<2} rate=${room.base_nightly_rate:<7.2f} status={room.current_status.value}"
    )


def search_rooms_menu(system: HotelSystem) -> None:
    """Collect optional search filters and display matching rooms."""
    print("\nSearch Rooms")
    room_id = prompt("Room ID (or press Enter): ") or None
    room_type_text = prompt("Room type [single/double/suite/penthouse/accessible] (or Enter): ")
    min_capacity_text = prompt("Minimum capacity (or Enter): ")
    max_rate_text = prompt("Maximum nightly rate (or Enter): ")
    check_in_text = prompt("Check-in date YYYY-MM-DD (or Enter): ")
    check_out_text = prompt("Check-out date YYYY-MM-DD (or Enter): ")

    room_type = RoomType(room_type_text.lower()) if room_type_text else None
    min_capacity = int(min_capacity_text) if min_capacity_text else None
    max_rate = float(max_rate_text) if max_rate_text else None
    check_in = parse_date(check_in_text) if check_in_text else None
    check_out = parse_date(check_out_text) if check_out_text else None

    rooms = system.search_rooms(room_id, room_type, min_capacity, max_rate, check_in, check_out)
    if not rooms:
        print("No rooms matched the filter.")
        return
    for room in rooms:
        show_room(room)


def create_booking_menu(system: HotelSystem) -> None:
    """Collect booking details and optional service selections from the console."""
    print("\nCreate Booking")
    guest_id = prompt("Guest ID: ")
    room_id = prompt("Room ID: ")
    check_in = parse_date(prompt("Check-in date YYYY-MM-DD: "))
    check_out = parse_date(prompt("Check-out date YYYY-MM-DD: "))
    created_by = prompt("Created by user ID: ")

    add_services = prompt("Add optional services? [y/n]: ").lower() == "y"
    chosen_services: list[Service] = []
    if add_services and system.services:
        print("Available services:")
        for service in system.services.values():
            print(
                f"- {service.service_id}: {service.name} "
                f"(${service.unit_price:.2f}, category={service.category.value})"
            )
        # Service catalogue items are copied so each booking can store its own quantity/date.
        while True:
            service_id = prompt("Service ID (or Enter to finish): ")
            if not service_id:
                break
            catalog_item = system.services.get(service_id)
            if catalog_item is None:
                print("Invalid service ID.")
                continue
            quantity = int(prompt("Quantity: "))
            chosen_services.append(
                Service(
                    service_id=catalog_item.service_id,
                    name=catalog_item.name,
                    category=catalog_item.category,
                    unit_price=catalog_item.unit_price,
                    quantity=quantity,
                    applied_date=check_in,
                )
            )

    booking = system.create_booking(
        guest_id=guest_id,
        room_id=room_id,
        check_in=check_in,
        check_out=check_out,
        created_by=created_by,
        service_items=chosen_services,
    )
    print(
        f"Booking created: {booking.booking_id}, status={booking.status.value}, "
        f"total=${booking.total_charges:.2f}"
    )


def update_complete_booking_menu(system: HotelSystem) -> None:
    """Handle booking date updates, cancellations, and checkout completion."""
    print("\nUpdate or Complete Booking")
    booking_id = prompt("Booking ID: ")
    action = prompt("Action [update/cancel/complete]: ").lower()

    if action == "update":
        new_check_in = parse_date(prompt("New check-in YYYY-MM-DD: "))
        new_check_out = parse_date(prompt("New check-out YYYY-MM-DD: "))
        if system.update_booking_dates(booking_id, new_check_in, new_check_out):
            print("Booking dates updated.")
        else:
            print("Unable to update booking.")
        return

    if action == "cancel":
        reason = prompt("Cancel reason: ")
        if system.cancel_booking(booking_id, reason):
            print("Booking canceled.")
        else:
            print("Unable to cancel booking.")
        return

    if action == "complete":
        invoice = system.complete_booking(booking_id)
        if invoice is None:
            print("Booking not found.")
            return
        print("Booking completed. Invoice:")
        print(invoice)
        return

    print("Invalid action.")


def view_bookings_menu(system: HotelSystem) -> None:
    """Show active bookings and optionally one guest's booking history."""
    print("\nActive Bookings")
    active = system.list_active_bookings()
    if not active:
        print("No active bookings.")
    for booking in active:
        print(
            f"{booking.booking_id} guest={booking.guest_id} room={booking.room_id} "
            f"{booking.check_in_date} -> {booking.check_out_date} status={booking.status.value}"
        )

    guest_id = prompt("\nEnter Guest ID to view booking history (or Enter to skip): ")
    if not guest_id:
        return
    history = system.get_user_history(guest_id)
    if not history:
        print("No history found for this guest.")
        return
    for booking in history:
        print(
            f"{booking.booking_id} status={booking.status.value} "
            f"charges=${booking.total_charges:.2f}"
        )


def staff_admin_menu(system: HotelSystem) -> None:
    """Console menu for staff/admin-only operations."""
    print("\nStaff/Admin Action")
    operator_id = prompt("Your user ID: ")
    user = system.users.get(operator_id)
    if user is None or user.role == UserRole.GUEST:
        print("Only staff/admin users can perform this action.")
        return

    print("1) Add room")
    print("2) Remove room")
    print("3) Approve booking")
    print("4) Deny booking")
    print("5) Generate report")
    print("6) Mark room maintenance")
    print("7) Apply seasonal pricing")
    choice = prompt("Select action: ")

    if choice == "1":
        room = create_room_from_input()
        system.add_room(room)
        print("Room added.")
    elif choice == "2":
        room_id = prompt("Room ID to remove: ")
        print("Room removed." if system.remove_room(room_id) else "Unable to remove room.")
    elif choice == "3":
        booking_id = prompt("Booking ID to approve: ")
        print("Booking approved." if system.process_booking_request(booking_id, True) else "Failed.")
    elif choice == "4":
        booking_id = prompt("Booking ID to deny: ")
        print("Booking denied." if system.process_booking_request(booking_id, False) else "Failed.")
    elif choice == "5":
        report = system.generate_report(ReportType.FULL, operator_id)
        print(
            f"Report generated: occupancy={report.data['occupancy_rate']}%, "
            f"revenue=${report.data['revenue_summary']['total_revenue']:.2f}"
        )
    elif choice == "6":
        room_id = prompt("Room ID: ")
        room = system.rooms.get(room_id)
        if room is None:
            print("Invalid room ID.")
        elif room.current_status == RoomStatus.MAINTENANCE:
            room.set_maintenance(False)
            print("Room marked available.")
        else:
            room.set_maintenance(True)
            print("Room marked under maintenance.")
    elif choice == "7":
        season_text = prompt("Season [low/normal/peak]: ").lower()
        try:
            system.apply_seasonal_pricing(Season(season_text))
            print(f"Seasonal pricing updated to '{season_text}'.")
        except ValueError:
            print("Invalid season.")
    else:
        print("Invalid action.")


def create_room_from_input():
    """Build a Room object from console input fields."""
    room_id = prompt("Room ID: ")
    room_number = prompt("Room Number: ")
    room_type = RoomType(prompt("Room type [single/double/suite/penthouse/accessible]: ").lower())
    floor = int(prompt("Floor: "))
    capacity = int(prompt("Capacity: "))
    rate = float(prompt("Base nightly rate: "))
    return Room(
        room_id=room_id,
        room_number=room_number,
        room_type=room_type,
        floor=floor,
        capacity=capacity,
        base_nightly_rate=rate,
        amenities=[],
    )


def bootstrap_system() -> tuple[HotelSystem, ExcelStorage]:
    """Load saved Excel data when present, otherwise seed default data."""
    system = HotelSystem.get_instance()
    storage = ExcelStorage(DATA_FILE)
    loaded = storage.load(system)
    if loaded:
        print(f"Loaded existing data from {DATA_FILE}.")
    else:
        preload_data(system)
        print("Loaded default preload data.")
    return system, storage


def run_console() -> None:
    """Run the interactive console menu until the user saves and exits."""
    system, storage = bootstrap_system()
    print("\nHotel Room Reservation System")

    while True:
        print("\nMain Menu")
        print("1) Search rooms")
        print("2) Create booking")
        print("3) Update/Complete booking")
        print("4) View active bookings and guest history")
        print("5) Staff/Admin action")
        print("6) Save and Exit")

        choice = prompt("Choose option [1-6]: ")
        try:
            if choice == "1":
                search_rooms_menu(system)
            elif choice == "2":
                create_booking_menu(system)
            elif choice == "3":
                update_complete_booking_menu(system)
            elif choice == "4":
                view_bookings_menu(system)
            elif choice == "5":
                staff_admin_menu(system)
            elif choice == "6":
                storage.save(system)
                print(f"Data saved to {DATA_FILE}. Goodbye.")
                break
            else:
                print("Please choose a number from 1 to 6.")
        except ValueError as exc:
            print(f"Input error: {exc}")
        except Exception as exc:  # keep CLI resilient during demo
            print(f"Unexpected error: {exc}")


if __name__ == "__main__":
    run_console()
