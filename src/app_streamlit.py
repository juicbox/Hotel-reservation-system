from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import streamlit as st

from hotel.enums import ReportType, RoomStatus, RoomType, Season
from hotel.hotel_system import HotelSystem
from hotel.models import Service
from hotel.preload import preload_data
from hotel.storage.excel_storage import ExcelStorage

DATA_FILE = Path("hotel_data.xlsx")


def bootstrap() -> tuple[HotelSystem, ExcelStorage]:
    if "hotel_system" not in st.session_state:
        system = HotelSystem.reset_instance()
        storage = ExcelStorage(DATA_FILE)
        loaded = storage.load(system)
        if not loaded:
            preload_data(system)
        st.session_state["hotel_system"] = system
        st.session_state["excel_storage"] = storage
        st.session_state["loaded_from_excel"] = loaded
    return st.session_state["hotel_system"], st.session_state["excel_storage"]


def room_type_label(room_type: RoomType) -> str:
    return room_type.value.capitalize()


def render_search(system: HotelSystem) -> None:
    st.subheader("Search Rooms")
    col1, col2 = st.columns(2)
    with col1:
        room_id = st.text_input("Room ID (optional)")
        room_type_raw = st.selectbox(
            "Room Type (optional)",
            options=[""] + [item.value for item in RoomType],
            format_func=lambda value: value.capitalize() if value else "Any",
        )
        min_capacity = st.number_input("Minimum capacity", min_value=0, value=0, step=1)
    with col2:
        max_rate = st.number_input("Maximum nightly rate", min_value=0.0, value=0.0, step=10.0)
        use_date_filter = st.checkbox("Filter by date range")
        if use_date_filter:
            check_in = st.date_input("Check-in date", value=date.today())
            check_out = st.date_input("Check-out date", value=date.today() + timedelta(days=1))
        else:
            check_in = None
            check_out = None

    if st.button("Run search", use_container_width=True):
        room_type = RoomType(room_type_raw) if room_type_raw else None
        rooms = system.search_rooms(
            room_id=room_id.strip() or None,
            room_type=room_type,
            min_capacity=min_capacity or None,
            max_rate=max_rate or None,
            check_in=check_in,
            check_out=check_out,
        )
        if not rooms:
            st.info("No rooms found for the selected filters.")
            return
        st.success(f"Found {len(rooms)} room(s).")
        st.table(
            [
                {
                    "Room ID": room.room_id,
                    "Number": room.room_number,
                    "Type": room_type_label(room.room_type),
                    "Capacity": room.capacity,
                    "Rate": room.base_nightly_rate,
                    "Status": room.current_status.value,
                }
                for room in rooms
            ]
        )


def render_create_booking(system: HotelSystem) -> None:
    st.subheader("Create Booking")
    guest_ids = sorted(
        [user_id for user_id, user in system.users.items() if user.role.value == "guest"]
    )
    room_ids = sorted(system.rooms.keys())
    service_ids = sorted(system.services.keys())

    col1, col2 = st.columns(2)
    with col1:
        guest_id = st.selectbox("Guest ID", options=guest_ids)
        room_id = st.selectbox("Room ID", options=room_ids)
        created_by = st.text_input("Created by (staff/admin ID)", value="ST-001")
    with col2:
        check_in = st.date_input("Check-in date", value=date.today())
        check_out = st.date_input("Check-out date", value=date.today() + timedelta(days=1))
        selected_services = st.multiselect("Optional services", options=service_ids)

    quantities = {}
    for service_id in selected_services:
        quantities[service_id] = st.number_input(
            f"Quantity for {service_id}", min_value=1, max_value=20, value=1, step=1
        )

    if st.button("Create booking", use_container_width=True):
        service_items = []
        for service_id in selected_services:
            source = system.services[service_id]
            service_items.append(
                Service(
                    service_id=source.service_id,
                    name=source.name,
                    category=source.category,
                    unit_price=source.unit_price,
                    quantity=quantities[service_id],
                    applied_date=check_in,
                )
            )

        try:
            booking = system.create_booking(
                guest_id=guest_id,
                room_id=room_id,
                check_in=check_in,
                check_out=check_out,
                created_by=created_by,
                service_items=service_items,
            )
            st.success(
                f"Booking created: {booking.booking_id} | Status: {booking.status.value} | "
                f"Total: ${booking.total_charges:.2f}"
            )
        except ValueError as exc:
            st.error(str(exc))


def render_view_bookings(system: HotelSystem) -> None:
    st.subheader("View Active Bookings and Guest History")

    active = system.list_active_bookings()
    if active:
        st.table(
            [
                {
                    "Booking ID": booking.booking_id,
                    "Guest ID": booking.guest_id,
                    "Room ID": booking.room_id,
                    "Check-in": booking.check_in_date.isoformat(),
                    "Check-out": booking.check_out_date.isoformat(),
                    "Status": booking.status.value,
                    "Charges": booking.total_charges,
                }
                for booking in active
            ]
        )
    else:
        st.info("No active bookings found.")

    guest_id = st.text_input("Guest ID for history")
    if st.button("Load guest history"):
        history = system.get_user_history(guest_id.strip())
        if not history:
            st.warning("No history found for that guest ID.")
            return
        st.table(
            [
                {
                    "Booking ID": booking.booking_id,
                    "Status": booking.status.value,
                    "Check-in": booking.check_in_date.isoformat(),
                    "Check-out": booking.check_out_date.isoformat(),
                    "Charges": booking.total_charges,
                }
                for booking in history
            ]
        )


def render_admin(system: HotelSystem) -> None:
    st.subheader("Staff/Admin Actions")
    action = st.selectbox(
        "Select action",
        options=[
            "Approve booking",
            "Deny booking",
            "Toggle room maintenance",
            "Apply seasonal pricing",
            "Generate report",
        ],
    )

    if action in {"Approve booking", "Deny booking"}:
        booking_id = st.text_input("Booking ID")
        if st.button("Run action", use_container_width=True):
            ok = system.process_booking_request(booking_id.strip(), action == "Approve booking")
            if ok:
                st.success("Action completed successfully.")
            else:
                st.error("Action failed. Check booking ID and status.")
    elif action == "Toggle room maintenance":
        room_id = st.selectbox("Room ID", options=sorted(system.rooms.keys()))
        if st.button("Run action", use_container_width=True):
            room = system.rooms[room_id]
            room.set_maintenance(room.current_status != RoomStatus.MAINTENANCE)
            st.success(f"Room {room_id} status is now: {room.current_status.value}")
    elif action == "Apply seasonal pricing":
        season_raw = st.selectbox("Season", options=[item.value for item in Season])
        if st.button("Run action", use_container_width=True):
            system.apply_seasonal_pricing(Season(season_raw))
            st.success(f"Seasonal pricing applied: {season_raw}")
    elif action == "Generate report":
        generated_by = st.text_input("Generated by (admin ID)", value="AD-001")
        if st.button("Run action", use_container_width=True):
            report = system.generate_report(ReportType.FULL, generated_by)
            st.json(report.data)


def save_data(storage: ExcelStorage, system: HotelSystem) -> None:
    storage.save(system)
    st.success(f"Data saved to {DATA_FILE}.")


def main() -> None:
    st.set_page_config(page_title="Hotel Reservation System", layout="wide")
    st.title("Hotel Room Reservation System")

    system, storage = bootstrap()
    if st.session_state.get("loaded_from_excel"):
        st.caption("Loaded existing data from hotel_data.xlsx")
    else:
        st.caption("Loaded default preload data")

    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Go to",
        options=[
            "Search Rooms",
            "Create Booking",
            "View Bookings",
            "Staff/Admin",
        ],
    )

    if page == "Search Rooms":
        render_search(system)
    elif page == "Create Booking":
        render_create_booking(system)
    elif page == "View Bookings":
        render_view_bookings(system)
    elif page == "Staff/Admin":
        render_admin(system)

    st.divider()
    if st.button("Save Data", use_container_width=True):
        save_data(storage, system)


if __name__ == "__main__":
    main()
