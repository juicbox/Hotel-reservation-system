from __future__ import annotations

from pathlib import Path

import streamlit as st

from hotel.enums import RoomStatus
from hotel.hotel_system import HotelSystem
from hotel.models import Guest
from hotel.preload import preload_data
from hotel.storage.excel_storage import ExcelStorage

DATA_FILE = Path("hotel_data.xlsx")


def bootstrap() -> tuple[HotelSystem, ExcelStorage]:
    """Create or reuse the Streamlit session's HotelSystem and storage helper."""
    if "hotel_system" not in st.session_state:
        system = HotelSystem.reset_instance()
        storage = ExcelStorage(DATA_FILE)
        loaded = storage.load(system)
        if not loaded:
            preload_data(system)
        # Store the system in session state so reruns keep the same in-memory data.
        st.session_state["hotel_system"] = system
        st.session_state["excel_storage"] = storage
        st.session_state["loaded_from_excel"] = loaded
    return st.session_state["hotel_system"], st.session_state["excel_storage"]


def render_data_source_caption() -> None:
    """Show whether data came from Excel or from the default preload records."""
    if st.session_state.get("loaded_from_excel"):
        st.caption("Loaded existing data from hotel_data.xlsx")
    else:
        st.caption("Loaded default preload data")


def _merge_persisted_guest_records(storage: ExcelStorage, system: HotelSystem) -> None:
    """Keep guest-created users/bookings if another Streamlit session saved them first."""
    if not DATA_FILE.exists():
        return

    persisted = HotelSystem()
    if not storage.load(persisted):
        return

    for user_id, user in persisted.users.items():
        if user_id not in system.users:
            system.users[user_id] = user

    for booking_id, booking in persisted.bookings.items():
        if booking_id not in system.bookings:
            system.bookings[booking_id] = booking
            guest = system.users.get(booking.guest_id)
            if isinstance(guest, Guest) and booking_id not in guest.bookings:
                guest.bookings.append(booking_id)

            room = system.rooms.get(booking.room_id)
            if room and booking.is_active and room.current_status not in {
                RoomStatus.MAINTENANCE,
                RoomStatus.CLEANING,
            }:
                room.current_status = RoomStatus.RESERVED


def save_data(storage: ExcelStorage, system: HotelSystem) -> None:
    """Persist current in-memory data to the shared Excel file."""
    try:
        _merge_persisted_guest_records(storage, system)
        storage.save(system)
    except PermissionError:
        st.error(
            f"Could not save to {DATA_FILE}. Close the Excel file if it is open, "
            "then click Save Data again."
        )
        return
    st.success(f"Data saved to {DATA_FILE}.")
