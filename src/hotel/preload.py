from datetime import date

from hotel.enums import RoomType, ServiceCategory, ShiftType
from hotel.hotel_system import HotelSystem
from hotel.models import Guest, Room, Service, Staff, SuperAdmin


def preload_data(system: HotelSystem) -> None:
    """Load starter records required by the assignment."""
    # Do not overwrite records that were loaded from Excel or already created in memory.
    if system.rooms or system.users:
        return

    # Seed enough room variety for search, pricing, and booking demonstrations.
    rooms = [
        Room("RM-101", "101", RoomType.SINGLE, 1, 1, 120.0, amenities=["WiFi", "TV"]),
        Room("RM-102", "102", RoomType.DOUBLE, 1, 2, 180.0, amenities=["WiFi", "TV"]),
        Room("RM-201", "201", RoomType.SUITE, 2, 3, 320.0, amenities=["WiFi", "Mini Bar"]),
        Room("RM-301", "301", RoomType.PENTHOUSE, 3, 4, 620.0, amenities=["Spa", "Sea View"]),
        Room(
            "RM-105",
            "105",
            RoomType.ACCESSIBLE,
            1,
            2,
            170.0,
            amenities=["Wheelchair Access", "WiFi"],
        ),
    ]
    for room in rooms:
        system.add_room(room)

    # Demo guest accounts are used by the Streamlit guest login screen.
    guest_1 = Guest.create("GU-001", "John Parker", "john@example.com", "hash123", "0400000001")
    guest_1.nationality = "Australian"
    guest_1.id_verified = True

    guest_2 = Guest.create("GU-002", "Mia Clark", "mia@example.com", "hash234", "0400000002")
    guest_2.membership_tier = "Gold"
    guest_2.loyalty_points = 120

    staff = Staff.create(
        "ST-001", "Amelia Staff", "staff@example.com", "hash345", "0400000003", access_level=3
    )
    staff.department = "Front Office"
    staff.shift = ShiftType.EVENING
    staff.employed_since = date(2022, 7, 1)

    admin = SuperAdmin.create(
        "AD-001", "Noah Admin", "admin@example.com", "hash456", "0400000004"
    )
    admin.report_recipient = "management@hotel.com"

    users = [guest_1, guest_2, staff, admin]
    for user in users:
        system.add_user(user)

    # The service catalogue is copied onto bookings when guests select add-ons.
    service_catalog = [
        Service("SV-001", "Breakfast Buffet", ServiceCategory.BREAKFAST, 25.0),
        Service("SV-002", "Airport Transfer", ServiceCategory.TRANSPORT, 60.0),
        Service("SV-003", "Spa Session", ServiceCategory.SPA, 90.0),
    ]
    for service in service_catalog:
        system.add_service_catalog_item(service)
