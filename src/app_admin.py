from __future__ import annotations

import streamlit as st

from ui.admin_pages import (
    render_all_bookings,
    render_booking_requests,
    render_reports,
    render_room_management,
    render_seasonal_pricing,
)
from ui.auth import admin_logout, render_admin_login
from ui.bootstrap import bootstrap, render_data_source_caption, save_data
from ui.style import apply_theme, hero


def main() -> None:
    """Standalone admin portal entry point."""
    st.set_page_config(page_title="Hotel Admin Portal", layout="wide")
    apply_theme()
    hero(
        "Hotel Admin Portal",
        "Review bookings, manage rooms, update seasonal pricing, and monitor hotel performance.",
        "Secure admin workspace",
    )

    if not render_admin_login():
        return

    system, storage = bootstrap()
    render_data_source_caption()

    st.sidebar.header("Admin dashboard")
    st.sidebar.success("Signed in as admin")
    if st.sidebar.button("Sign out", use_container_width=True):
        admin_logout()
        st.rerun()

    st.sidebar.divider()
    page = st.sidebar.radio(
        "Go to",
        options=[
            "Active Bookings",
            "Booking Requests",
            "Room Management",
            "Seasonal Pricing",
            "Reports",
        ],
    )

    if page == "Active Bookings":
        render_all_bookings(system)
    elif page == "Booking Requests":
        render_booking_requests(system)
    elif page == "Room Management":
        render_room_management(system)
    elif page == "Seasonal Pricing":
        render_seasonal_pricing(system)
    elif page == "Reports":
        render_reports(system)

    st.divider()
    if st.button("Save Data", use_container_width=True):
        save_data(storage, system)


if __name__ == "__main__":
    main()
