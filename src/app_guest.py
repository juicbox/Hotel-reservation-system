from __future__ import annotations

import streamlit as st

from ui.auth import (
    get_current_guest_id,
    guest_logout,
    is_guest_authenticated,
    render_guest_login,
)
from ui.bootstrap import bootstrap, render_data_source_caption
from ui.guest_pages import (
    render_create_booking,
    render_manage_booking,
    render_my_bookings,
    render_search,
)
from ui.style import apply_theme, hero


def _require_login(system) -> bool:
    """Prompt guests to sign in before they access personal booking pages."""
    if is_guest_authenticated():
        return True
    st.info("Please sign in or create an account to continue.")
    render_guest_login(system)
    return False


def main() -> None:
    """Standalone guest portal entry point."""
    st.set_page_config(page_title="Hotel Guest Portal", layout="wide")
    apply_theme()
    hero(
        "Hotel Guest Portal",
        "Explore available rooms first, then sign in when you are ready to book or manage your stay.",
        "Guest booking",
    )

    system, _storage = bootstrap()
    render_data_source_caption()

    st.sidebar.header("Guest portal")
    if is_guest_authenticated():
        guest = system.users.get(get_current_guest_id())
        st.sidebar.success(f"Signed in as {guest.full_name}" if guest else "Signed in")
        if st.sidebar.button("Sign out", use_container_width=True):
            guest_logout()
            st.rerun()
    else:
        st.sidebar.caption("Not signed in")

    st.sidebar.divider()
    page = st.sidebar.radio(
        "Go to",
        options=[
            "Search Rooms",
            "Book a Room",
            "My Bookings",
            "Cancel a Booking",
        ],
    )

    if page == "Search Rooms":
        render_search(system)
    elif page == "Book a Room":
        if _require_login(system):
            render_create_booking(system, get_current_guest_id())
    elif page == "My Bookings":
        if _require_login(system):
            render_my_bookings(system, get_current_guest_id())
    elif page == "Cancel a Booking":
        if _require_login(system):
            render_manage_booking(system, get_current_guest_id())


if __name__ == "__main__":
    main()
