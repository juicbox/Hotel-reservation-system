# Hotel Room Reservation System (Part B)

This project is a Python implementation of the Part A UML design for a hotel room reservation system.

## What is implemented

- Task 1: OO classes based on UML (Room, User hierarchy, Booking, Service, HotelSystem, Report)
- Task 2: Interactive console menu
- Task 3: Startup preload data (rooms, users, services)
- Task 4: Excel persistence (save and load)

## Project structure

- `src/main.py`: Console entry point and menu flow
- `src/hotel/enums.py`: Enums used by model classes
- `src/hotel/models/`: Domain classes from UML
- `src/hotel/hotel_system.py`: Singleton manager/system class
- `src/hotel/preload.py`: Initial data preload records
- `src/hotel/storage/excel_storage.py`: Excel save/load helper

## Setup

1. Install Python 3.10+.
2. Install dependency:
   - `pip install -r requirements.txt`

## Run

From the project root:

- `python src/main.py`

## Run frontend (Streamlit)

From the project root:

- `streamlit run src/app_streamlit.py`

This launches a single browser UI that serves both guest and admin experiences:

- **Guest portal** is the default view (no login required).
- **Admin login** button in the top-right corner reveals a compact sign-in form.
  - Credentials: username `admin`, password `admin`
  - Once signed in, the sidebar and pages switch to the admin portal.
  - A **Sign out** button returns to the guest view.

The standalone portals are also available:
- `streamlit run src/app_guest.py`
- `streamlit run src/app_admin.py`

## Data persistence

- File used: `hotel_data.xlsx` (created in project root)
- On startup:
  - If `hotel_data.xlsx` exists, data is loaded from it.
  - Otherwise, default preload data is used.
- On exit (menu option 6), current state is saved to Excel.

## Data source and preload rationale

- No external dataset was used for this assessment.
- To satisfy Task 3, the system uses a synthetic starter dataset defined in `src/hotel/preload.py`.
- The preload includes rooms, users, and service catalog records so the menu can be demonstrated immediately.
- To satisfy Task 4, runtime data is persisted to `hotel_data.xlsx` using `openpyxl` and loaded again on next startup.

## Quick testing guide (manual)

1. Start program and use menu option `1` to search rooms.
2. Use option `2` to create a booking with seeded guest and room IDs.
3. Use option `3` to update/cancel/complete that booking.
4. Use option `4` to check active bookings and guest history.
5. Use option `5` with `ST-001` or `AD-001` for staff/admin actions.
6. Exit with option `6`, restart program, and confirm data reload from Excel.

## Preloaded sample IDs

- Rooms: `RM-101`, `RM-102`, `RM-201`, `RM-301`, `RM-105`
- Guest users: `GU-001`, `GU-002`
- Staff user: `ST-001`
- Super admin: `AD-001`
- Services: `SV-001`, `SV-002`, `SV-003`
