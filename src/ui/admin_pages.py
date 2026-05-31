from __future__ import annotations

import streamlit as st

from hotel.enums import ReportType, RoomStatus, RoomType, Season
from hotel.hotel_system import HotelSystem
from hotel.models import Room
from ui.style import page_header


def render_all_bookings(system: HotelSystem) -> None:
    """Show all active bookings in a readable admin table."""
    page_header("Active bookings", "Monitor all bookings that are currently pending, confirmed, or checked in.")
    active = system.list_active_bookings()
    if active:
        st.dataframe(
            [
                {
                    "Reference": booking.booking_id,
                    "Guest": system.users[booking.guest_id].full_name
                    if booking.guest_id in system.users
                    else booking.guest_id,
                    "Room": system.rooms[booking.room_id].room_number
                    if booking.room_id in system.rooms
                    else booking.room_id,
                    "Check-in": booking.check_in_date.isoformat(),
                    "Check-out": booking.check_out_date.isoformat(),
                    "Status": booking.status.value.replace("_", " ").capitalize(),
                    "Total ($)": f"{booking.total_charges:,.2f}",
                }
                for booking in active
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No active bookings found.")


def render_booking_requests(system: HotelSystem) -> None:
    """Show pending booking requests and approval controls."""
    page_header(
        "Booking requests",
        "Approve valid guest booking requests or deny requests that cannot be fulfilled.",
    )
    pending = [
        booking
        for booking in system.list_active_bookings()
        if booking.status.value == "pending"
    ]
    if pending:
        st.dataframe(
            [
                {
                    "Reference": booking.booking_id,
                    "Guest": system.users[booking.guest_id].full_name
                    if booking.guest_id in system.users
                    else booking.guest_id,
                    "Room": system.rooms[booking.room_id].room_number
                    if booking.room_id in system.rooms
                    else booking.room_id,
                    "Check-in": booking.check_in_date.isoformat(),
                    "Check-out": booking.check_out_date.isoformat(),
                    "Total ($)": f"{booking.total_charges:,.2f}",
                }
                for booking in pending
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No pending bookings.")

    booking_id = st.text_input("Booking ID")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Approve", use_container_width=True, type="primary"):
            if system.process_booking_request(booking_id.strip(), True):
                st.success("Booking approved.")
            else:
                st.error("Approval failed. Check booking ID and status.")
    with col2:
        if st.button("Deny", use_container_width=True):
            if system.process_booking_request(booking_id.strip(), False):
                st.success("Booking denied.")
            else:
                st.error("Denial failed. Check booking ID and status.")


def render_room_management(system: HotelSystem) -> None:
    """Render room inventory controls for admin users."""
    page_header(
        "Room management",
        "Review inventory, add new rooms, remove unused rooms, and toggle maintenance status.",
    )

    st.markdown("**Current rooms**")
    if system.rooms:
        st.dataframe(
            [
                {
                    "Room ID": room.room_id,
                    "Number": room.room_number,
                    "Type": room.room_type.value.capitalize(),
                    "Capacity": room.capacity,
                    "Rate ($)": f"{room.base_nightly_rate:,.2f}",
                    "Status": room.current_status.value.capitalize(),
                }
                for room in system.rooms.values()
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No rooms in the system.")

    st.markdown("**Toggle maintenance**")
    room_id = st.selectbox("Room ID", options=sorted(system.rooms.keys()))
    if st.button("Toggle maintenance status", use_container_width=True):
        room = system.rooms[room_id]
        room.set_maintenance(room.current_status != RoomStatus.MAINTENANCE)
        st.success(f"Room {room_id} status is now: {room.current_status.value}")

    st.markdown("**Add room**")
    with st.form("add_room_form"):
        new_room_id = st.text_input("Room ID")
        room_number = st.text_input("Room number")
        room_type = st.selectbox("Room type", options=[item.value for item in RoomType])
        floor = st.number_input("Floor", min_value=0, step=1)
        capacity = st.number_input("Capacity", min_value=1, step=1)
        rate = st.number_input("Base nightly rate", min_value=0.0, step=10.0)
        submitted = st.form_submit_button("Add room", use_container_width=True)

    if submitted:
        if new_room_id in system.rooms:
            st.error("A room with that ID already exists.")
        else:
            system.add_room(
                Room(
                    room_id=new_room_id.strip(),
                    room_number=room_number.strip(),
                    room_type=RoomType(room_type),
                    floor=int(floor),
                    capacity=int(capacity),
                    base_nightly_rate=float(rate),
                    amenities=[],
                )
            )
            st.success(f"Room {new_room_id} added.")

    st.markdown("**Remove room**")
    remove_id = st.selectbox("Room to remove", options=sorted(system.rooms.keys()), key="remove_room")
    if st.button("Remove room", use_container_width=True):
        if system.remove_room(remove_id):
            st.success(f"Room {remove_id} removed.")
        else:
            st.error("Unable to remove room. It may have active bookings.")


def render_seasonal_pricing(system: HotelSystem) -> None:
    """Allow admin users to apply a global seasonal rate multiplier."""
    page_header(
        "Seasonal pricing",
        "Apply a pricing multiplier across all rooms for low, normal, or peak seasons.",
    )
    season_raw = st.selectbox("Season", options=[item.value for item in Season])
    if st.button("Apply seasonal pricing", use_container_width=True, type="primary"):
        system.apply_seasonal_pricing(Season(season_raw))
        st.success(f"Seasonal pricing applied: {season_raw}")


def render_reports(system: HotelSystem) -> None:
    """Generate a human-readable operational report for admins."""
    page_header(
        "Reports",
        "Generate a readable snapshot of occupancy, revenue, room status, and recent activity.",
    )

    if not st.button("Generate report", use_container_width=True, type="primary"):
        return

    report = system.generate_report(ReportType.FULL, "AD-001")
    d = report.data

    st.caption(f"Generated at {report.generated_at.strftime('%Y-%m-%d %H:%M')}  ·  Season: **{d['season'].capitalize()}**")

    # ── Key metrics ────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Occupancy rate", f"{d['occupancy_rate']}%")
    col2.metric("Total revenue", f"${d['revenue_summary']['total_revenue']:,.2f}")
    col3.metric("Active bookings", d["active_bookings"])
    col4.metric("Total rooms", len(system.rooms))

    st.divider()

    # ── Room status breakdown ──────────────────────────────────────────────────
    st.markdown("#### Room status")
    status_counts: dict[str, int] = {}
    for room in system.rooms.values():
        label = room.current_status.value.capitalize()
        status_counts[label] = status_counts.get(label, 0) + 1

    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.dataframe(
            [{"Status": k, "Rooms": v} for k, v in sorted(status_counts.items())],
            hide_index=True,
            use_container_width=True,
        )
    with col_b:
        st.bar_chart(status_counts)

    st.divider()

    # ── Booking status breakdown ───────────────────────────────────────────────
    st.markdown("#### Booking status")
    booking_counts: dict[str, int] = {}
    for booking in system.bookings.values():
        label = booking.status.value.replace("_", " ").capitalize()
        booking_counts[label] = booking_counts.get(label, 0) + 1

    if booking_counts:
        col_c, col_d = st.columns([1, 2])
        with col_c:
            st.dataframe(
                [{"Status": k, "Bookings": v} for k, v in sorted(booking_counts.items())],
                hide_index=True,
                use_container_width=True,
            )
        with col_d:
            st.bar_chart(booking_counts)
    else:
        st.info("No bookings recorded yet.")

    st.divider()

    # ── Revenue per room type ──────────────────────────────────────────────────
    st.markdown("#### Revenue by room type")
    type_revenue: dict[str, float] = {}
    for booking in system.bookings.values():
        room = system.rooms.get(booking.room_id)
        if room is None:
            continue
        label = room.room_type.value.capitalize()
        type_revenue[label] = round(type_revenue.get(label, 0.0) + booking.total_charges, 2)

    if type_revenue:
        col_e, col_f = st.columns([1, 2])
        with col_e:
            st.dataframe(
                [{"Room type": k, "Revenue ($)": f"{v:,.2f}"} for k, v in sorted(type_revenue.items())],
                hide_index=True,
                use_container_width=True,
            )
        with col_f:
            st.bar_chart(type_revenue)
    else:
        st.info("No revenue data yet.")

    st.divider()

    # ── Recent bookings ────────────────────────────────────────────────────────
    st.markdown("#### Recent bookings")
    recent = sorted(system.bookings.values(), key=lambda b: b.modified_at, reverse=True)[:10]
    if recent:
        st.dataframe(
            [
                {
                    "Reference": b.booking_id,
                    "Guest": system.users[b.guest_id].full_name if b.guest_id in system.users else b.guest_id,
                    "Room": system.rooms[b.room_id].room_number if b.room_id in system.rooms else b.room_id,
                    "Check-in": b.check_in_date.isoformat(),
                    "Check-out": b.check_out_date.isoformat(),
                    "Status": b.status.value.replace("_", " ").capitalize(),
                    "Total ($)": f"{b.total_charges:,.2f}",
                }
                for b in recent
            ],
            hide_index=True,
            use_container_width=True,
        )
