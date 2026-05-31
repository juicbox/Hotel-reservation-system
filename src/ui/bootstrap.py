from __future__ import annotations

from pathlib import Path

import streamlit as st

from hotel.hotel_system import HotelSystem
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


def save_data(storage: ExcelStorage, system: HotelSystem) -> None:
    """Persist current in-memory data to the shared Excel file."""
    storage.save(system)
    st.success(f"Data saved to {DATA_FILE}.")
