from __future__ import annotations

import streamlit as st

from ui.admin_pages import (
    render_all_bookings,
    render_booking_requests,
    render_reports,
    render_room_management,
    render_seasonal_pricing,
)
from ui.auth import (
    admin_logout,
    get_current_guest_id,
    guest_logout,
    is_admin_authenticated,
    is_guest_authenticated,
    render_admin_login_form,
    render_guest_login,
)
from ui.bootstrap import bootstrap, render_data_source_caption, save_data
from ui.guest_pages import (
    render_create_booking,
    render_manage_booking,
    render_my_bookings,
    render_search,
)
from ui.style import apply_theme, hero


def render_header() -> None:
    """Render the public hero and the top-right admin login entry point."""
    _, right = st.columns([5.5, 2])
    with right:
        with st.container(border=True):
            if is_admin_authenticated():
                st.caption("Admin session active")
                if st.button("Admin Sign Out", width="stretch"):
                    admin_logout()
                    st.rerun()
            else:
                st.caption("Staff access")
                if st.button("Admin Login", width="stretch", type="primary"):
                    st.session_state["show_admin_login"] = not st.session_state.get(
                        "show_admin_login", False
                    )
                    st.rerun()

    if is_admin_authenticated():
        hero(
            "Admin Dashboard",
            "Manage bookings, room operations, pricing, and reporting from one secure workspace.",
            "Signed in as admin",
        )
    else:
        hero(
            "Hotel Reservation Portal",
            "Browse rooms freely, then sign in only when you are ready to book or manage your stay.",
            "Guest booking",
        )


def render_admin_portal(system, storage) -> None:
    """Render admin-only navigation and pages after admin login."""
    st.sidebar.header("Admin dashboard")
    st.sidebar.caption("Operations and reporting")
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
    if st.button("Save Data", width="stretch"):
        save_data(storage, system)


def _require_login(system, storage) -> bool:
    """Show the login/register form and return False if the guest is not signed in."""
    if is_guest_authenticated():
        return True
    st.info("Please sign in or create an account to continue.")
    render_guest_login(system, storage)
    return False


def render_guest_portal(system, storage) -> None:
    """Render public guest navigation; protected pages ask for login when needed."""
    # Sidebar — guest identity or prompt to sign in
    st.sidebar.header("Guest portal")
    if is_guest_authenticated():
        guest = system.users.get(get_current_guest_id())
        st.sidebar.success(f"Signed in as {guest.full_name}" if guest else "Signed in")
        if st.sidebar.button("Sign out", width="stretch"):
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
        # Always accessible — no login needed
        render_search(system)
    elif page == "Book a Room":
        if _require_login(system, storage):
            render_create_booking(system, get_current_guest_id(), storage)
    elif page == "My Bookings":
        if _require_login(system, storage):
            render_my_bookings(system, get_current_guest_id())
    elif page == "Cancel a Booking":
        if _require_login(system, storage):
            render_manage_booking(system, get_current_guest_id(), storage)


def main() -> None:
    """Combined Streamlit app for guest browsing and admin operations."""
    st.set_page_config(page_title="Hotel Reservation System", layout="wide")
    apply_theme()

    system, storage = bootstrap()

    render_header()

    if is_admin_authenticated():
        render_data_source_caption()
        st.divider()
        render_admin_portal(system, storage)
        return

    render_admin_login_form()
    st.divider()
    render_data_source_caption()
    render_guest_portal(system, storage)


if __name__ == "__main__":
    main()
