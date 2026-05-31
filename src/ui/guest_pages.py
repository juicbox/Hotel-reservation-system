from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from hotel.enums import BookingStatus, RoomStatus, RoomType
from hotel.hotel_system import HotelSystem
from hotel.models import Service
from ui.style import page_header


def room_type_label(room_type: RoomType) -> str:
    return room_type.value.capitalize()


def _bookable_rooms(system: HotelSystem) -> list:
    """Return rooms that are not under maintenance or cleaning."""
    return [
        room for room in system.rooms.values()
        if room.current_status not in {RoomStatus.MAINTENANCE, RoomStatus.CLEANING}
    ]


def render_search(system: HotelSystem) -> None:
    """Render public room search; guests do not need an account to browse."""
    page_header(
        "Search rooms",
        "Compare available room types, rates, amenities, and dates before signing in.",
    )
    col1, col2 = st.columns(2)
    with col1:
        room_type_raw = st.selectbox(
            "Room Type",
            options=[""] + [item.value for item in RoomType],
            format_func=lambda value: value.capitalize() if value else "Any",
        )
        min_capacity = st.number_input("Minimum guests", min_value=0, value=0, step=1)
    with col2:
        max_rate = st.number_input("Maximum nightly rate ($)", min_value=0.0, value=0.0, step=10.0)
        use_date_filter = st.checkbox("Filter by date range")
        if use_date_filter:
            check_in = st.date_input("Check-in date", value=date.today())
            check_out = st.date_input("Check-out date", value=date.today() + timedelta(days=1))
        else:
            check_in = None
            check_out = None

    if st.button("Search", use_container_width=True, type="primary"):
        room_type = RoomType(room_type_raw) if room_type_raw else None
        all_matches = system.search_rooms(
            room_id=None,
            room_type=room_type,
            min_capacity=min_capacity or None,
            max_rate=max_rate or None,
            check_in=check_in,
            check_out=check_out,
        )
        # only show rooms guests can actually book
        rooms = [
            r for r in all_matches
            if r.current_status not in {RoomStatus.MAINTENANCE, RoomStatus.CLEANING}
        ]
        if not rooms:
            st.info("No rooms available for the selected filters.")
            return
        st.success(f"Found {len(rooms)} room(s).")
        st.dataframe(
            [
                {
                    "Room": room.room_number,
                    "Type": room_type_label(room.room_type),
                    "Guests": room.capacity,
                    "Nightly rate": f"${room.get_effective_rate(date.today()):.2f}",
                    "Amenities": ", ".join(room.amenities) if room.amenities else "—",
                    "Availability": "Available" if room.current_status == RoomStatus.AVAILABLE else "Currently booked",
                }
                for room in rooms
            ],
            hide_index=True,
            use_container_width=True,
        )


def render_create_booking(system: HotelSystem, guest_id: str) -> None:
    """Render booking form for the currently signed-in guest."""
    page_header(
        "Book a room",
        "Choose a room, travel dates, and optional services. Requests stay pending until staff approval.",
    )

    bookable = _bookable_rooms(system)
    if not bookable:
        st.warning("No rooms are currently available for booking.")
        return

    room_options = {
        f"{r.room_number} — {room_type_label(r.room_type)}, {r.capacity} guests, "
        f"${r.get_effective_rate(date.today()):.2f}/night": r.room_id
        for r in sorted(bookable, key=lambda r: r.room_number)
    }

    service_options = {
        f"{s.name} — ${s.unit_price:.2f}": s.service_id
        for s in system.services.values()
    }

    col1, col2 = st.columns(2)
    with col1:
        room_label = st.selectbox("Select room", options=list(room_options.keys()))
        check_in = st.date_input("Check-in date", value=date.today())
    with col2:
        check_out = st.date_input("Check-out date", value=date.today() + timedelta(days=1))
        selected_service_labels = st.multiselect("Add-on services (optional)", options=list(service_options.keys()))

    quantities = {}
    for label in selected_service_labels:
        quantities[label] = st.number_input(
            f"Quantity: {label}", min_value=1, max_value=20, value=1, step=1
        )

    if st.button("Request booking", use_container_width=True, type="primary"):
        room_id = room_options[room_label]
        service_items = []
        for label in selected_service_labels:
            service_id = service_options[label]
            source = system.services[service_id]
            service_items.append(
                Service(
                    service_id=source.service_id,
                    name=source.name,
                    category=source.category,
                    unit_price=source.unit_price,
                    quantity=quantities[label],
                    applied_date=check_in,
                )
            )

        try:
            booking = system.create_booking(
                guest_id=guest_id,
                room_id=room_id,
                check_in=check_in,
                check_out=check_out,
                created_by=guest_id,
                service_items=service_items,
            )
            st.success(
                f"Booking request submitted! Reference: **{booking.booking_id}** | "
                f"Total: **${booking.total_charges:.2f}** | "
                f"Status: pending staff approval"
            )
        except ValueError as exc:
            st.error(str(exc))


def render_my_bookings(system: HotelSystem, guest_id: str) -> None:
    """Render only the signed-in guest's active and past bookings."""
    page_header("My bookings", "Review current reservations and previous stays.")
    history = system.get_user_history(guest_id)
    active = [b for b in history if b.is_active]
    past = [b for b in history if not b.is_active]

    st.markdown("**Active bookings**")
    if active:
        st.dataframe(
            [
                {
                    "Reference": b.booking_id,
                    "Room": system.rooms[b.room_id].room_number if b.room_id in system.rooms else b.room_id,
                    "Check-in": b.check_in_date.isoformat(),
                    "Check-out": b.check_out_date.isoformat(),
                    "Status": b.status.value.replace("_", " ").capitalize(),
                    "Total": f"${b.total_charges:.2f}",
                }
                for b in active
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("You have no active bookings.")

    st.markdown("**Past bookings**")
    if past:
        st.dataframe(
            [
                {
                    "Reference": b.booking_id,
                    "Room": system.rooms[b.room_id].room_number if b.room_id in system.rooms else b.room_id,
                    "Check-in": b.check_in_date.isoformat(),
                    "Check-out": b.check_out_date.isoformat(),
                    "Status": b.status.value.replace("_", " ").capitalize(),
                    "Total": f"${b.total_charges:.2f}",
                }
                for b in past
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No past bookings.")


def render_manage_booking(system: HotelSystem, guest_id: str) -> None:
    """Allow guests to cancel eligible bookings from their own account."""
    page_header(
        "Cancel a booking",
        "Cancel pending or confirmed bookings that have not started yet.",
    )
    history = system.get_user_history(guest_id)
    # guests can only cancel bookings that are pending or confirmed (not yet checked in)
    cancellable = [
        b for b in history
        if b.status in {BookingStatus.PENDING, BookingStatus.CONFIRMED}
    ]
    if not cancellable:
        st.info("You have no bookings that can be cancelled.")
        return

    booking_options = {
        f"{b.booking_id} — Room {system.rooms[b.room_id].room_number if b.room_id in system.rooms else b.room_id}, "
        f"{b.check_in_date} to {b.check_out_date}": b.booking_id
        for b in cancellable
    }

    selected_label = st.selectbox("Select booking to cancel", options=list(booking_options.keys()))
    reason = st.text_area("Reason for cancellation")

    if st.button("Cancel booking", use_container_width=True, type="primary"):
        if not reason.strip():
            st.error("Please provide a reason for cancellation.")
        else:
            booking_id = booking_options[selected_label]
            if system.cancel_booking(booking_id, reason.strip()):
                st.success("Your booking has been cancelled.")
            else:
                st.error("Unable to cancel this booking. Please contact reception.")
