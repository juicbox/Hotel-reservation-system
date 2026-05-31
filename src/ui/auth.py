from __future__ import annotations

import streamlit as st

from hotel.enums import UserRole
from hotel.hotel_system import HotelSystem
from hotel.models.guest import Guest
from ui.style import page_header

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


# ── Admin auth ────────────────────────────────────────────────────────────────

def is_admin_authenticated() -> bool:
    return bool(st.session_state.get("admin_authenticated"))


def render_admin_login_form() -> None:
    """Compact inline admin login form, toggled by the header button."""
    if is_admin_authenticated() or not st.session_state.get("show_admin_login"):
        return

    with st.container(border=True):
        st.markdown("**Admin sign-in**")
        st.caption("Enter admin credentials to open the management dashboard.")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            username = st.text_input(
                "Username", key="admin_login_username",
                label_visibility="collapsed", placeholder="Username",
            )
        with col2:
            password = st.text_input(
                "Password", type="password", key="admin_login_password",
                label_visibility="collapsed", placeholder="Password",
            )
        with col3:
            submit = st.button("Sign in", width="stretch", key="admin_login_submit")

        if submit:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state["admin_authenticated"] = True
                st.session_state.pop("show_admin_login", None)
                st.rerun()
            else:
                st.error("Invalid username or password.")


def render_admin_login() -> bool:
    """Standalone admin login screen used by the dedicated admin app."""
    if is_admin_authenticated():
        return True

    st.session_state["show_admin_login"] = True
    page_header("Admin sign-in", "Use your administrator credentials to continue.")
    render_admin_login_form()
    return False


def admin_logout() -> None:
    st.session_state.pop("admin_authenticated", None)
    st.session_state.pop("show_admin_login", None)


# ── Guest auth ────────────────────────────────────────────────────────────────

def is_guest_authenticated() -> bool:
    # Streamlit keeps per-browser-session state here; a signed-in guest is
    # represented by their user ID, not by exposing a selectable guest list.
    return bool(st.session_state.get("guest_id"))


def get_current_guest_id() -> str | None:
    # All guest-only pages use this ID so users can only access their own data.
    return st.session_state.get("guest_id")


def _next_guest_id(system: HotelSystem) -> str:
    """Generate the next sequential guest ID (e.g. GU-003)."""
    # Guest IDs are generated from existing in-memory users. They are persisted
    # later when the system is saved to hotel_data.xlsx.
    existing = [
        uid for uid in system.users
        if uid.startswith("GU-") and uid[3:].isdigit()
    ]
    next_num = max((int(uid[3:]) for uid in existing), default=0) + 1
    return f"GU-{next_num:03d}"


def _autosave_guest_change(storage, system: HotelSystem) -> None:
    """Save guest-created records immediately when storage is available."""
    if storage is None:
        return
    try:
        storage.save(system)
    except PermissionError:
        st.warning(
            "Account created for this session, but it could not be saved because "
            "hotel_data.xlsx is open. Close the Excel file and use Save Data."
        )


def render_guest_login(system: HotelSystem, storage=None) -> None:
    """Login / register page shown when no guest is signed in."""
    page_header(
        "Guest account",
        "Sign in to book rooms, view your reservations, or create a new account.",
    )
    tab_login, tab_register = st.tabs(["Sign in", "Create account"])

    # ── Sign in tab ──────────────────────────────────────────────────────────
    with tab_login:
        st.caption("Sign in with your registered email address and password.")
        with st.form("guest_login_form"):
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in", width="stretch")

        if submitted:
            # Authenticate against HotelSystem users. The preload data stores
            # demo password hashes as plain strings, so the entered value must
            # match the stored password_hash field.
            user = system.authenticate(email.strip(), password.strip())
            if user is None or user.role != UserRole.GUEST:
                st.error("Invalid email or password.")
            elif not user.is_active:
                st.error("Your account is inactive. Please contact reception.")
            else:
                st.session_state["guest_id"] = user.user_id
                st.rerun()

        st.divider()
        st.caption(
            "Demo accounts: `john@example.com` / `hash123` "
            "· `mia@example.com` / `hash234`"
        )

    # ── Register tab ─────────────────────────────────────────────────────────
    with tab_register:
        st.caption("Create a new guest account to start making reservations.")
        with st.form("guest_register_form"):
            full_name = st.text_input("Full name")
            email_reg = st.text_input("Email address", key="reg_email")
            phone = st.text_input("Phone number")
            password_reg = st.text_input("Password", type="password", key="reg_pw")
            password_confirm = st.text_input("Confirm password", type="password", key="reg_pw2")
            register = st.form_submit_button("Create account", width="stretch")

        if register:
            # Validation
            errors = []
            if not full_name.strip():
                errors.append("Full name is required.")
            if not email_reg.strip() or "@" not in email_reg:
                errors.append("A valid email address is required.")
            if not phone.strip():
                errors.append("Phone number is required.")
            if not password_reg:
                errors.append("Password is required.")
            elif password_reg != password_confirm:
                errors.append("Passwords do not match.")
            elif len(password_reg) < 4:
                errors.append("Password must be at least 4 characters.")

            email_taken = any(
                u.email == email_reg.strip() for u in system.users.values()
            )
            if email_taken:
                errors.append("An account with that email already exists.")

            if errors:
                for msg in errors:
                    st.error(msg)
            else:
                # Create the new guest in memory and sign them in immediately.
                # The account becomes permanent after the admin clicks Save Data.
                new_id = _next_guest_id(system)
                new_guest = Guest.create(
                    user_id=new_id,
                    full_name=full_name.strip(),
                    email=email_reg.strip(),
                    password_hash=password_reg,
                    phone=phone.strip(),
                )
                system.add_user(new_guest)
                _autosave_guest_change(storage, system)
                st.session_state["guest_id"] = new_id
                st.rerun()


def guest_logout() -> None:
    st.session_state.pop("guest_id", None)
