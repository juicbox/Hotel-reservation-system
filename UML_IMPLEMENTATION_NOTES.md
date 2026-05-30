# UML Implementation Notes

This document explains how the Part A UML model was translated into code.

## 1) Class mapping from UML to Python

- `Room` -> `src/hotel/models/room.py`
  - Includes room identity, type, status, rate, and availability checks.
- `User` (abstract) -> `src/hotel/models/user.py`
  - Common profile and authentication fields.
  - Abstract method `has_permission()` enforced in subclasses.
- `Guest` -> `src/hotel/models/guest.py`
  - Inherits `User`; supports guest-level permissions and loyalty points.
- `Staff` -> `src/hotel/models/staff.py`
  - Inherits `User`; includes access level and staff actions.
- `SuperAdmin` -> `src/hotel/models/super_admin.py`
  - Inherits `Staff`; unrestricted permissions and admin-level fields.
- `Booking` -> `src/hotel/models/booking.py`
  - Transaction model, overlap validation, service attachment, charge calculation.
- `Service` -> `src/hotel/models/service.py`
  - Optional add-on entity with pricing and category.
- `HotelSystem` (singleton manager) -> `src/hotel/hotel_system.py`
  - Central manager for rooms, users, bookings, reports, and business operations.
- `Report` -> `src/hotel/models/report.py`
  - Encapsulates occupancy/revenue output data.

## 2) Relationships implemented

- Inheritance:
  - `User <- Guest`
  - `User <- Staff <- SuperAdmin`
- Association:
  - `Booking` links `Guest` and `Room` by IDs.
- Composition:
  - `Booking` owns `Service` instances in `booking.services`.
- Aggregation:
  - `HotelSystem` stores independent collections of rooms, users, bookings, and services.

## 3) Enums from UML

Implemented in `src/hotel/enums.py`:

- `RoomType`
- `RoomStatus`
- `UserRole`
- `ShiftType`
- `BookingStatus`
- `ServiceCategory`
- `Season`
- `ReportType`

## 4) Functional translation to assignment tasks

- Task 1 (OO classes): Implemented with typed Python dataclasses + abstract base class.
- Task 2 (interactive console menu): Implemented in `src/main.py`.
- Task 3 (data preload): Implemented in `src/hotel/preload.py`.
- Task 4 (Excel persistence): Implemented in `src/hotel/storage/excel_storage.py`.

## 5) Design decisions kept from UML rationale

- `HotelSystem` implemented as singleton (`get_instance()`).
- Overlap validation is booking-focused (`Booking.validate_overlap()`).
- Role-based behavior uses polymorphism through `has_permission()`.
- `password_hash` retained as hash field (no plain password storage).

## 6) Notes for assessor

- Code uses clean module boundaries to match UML responsibilities.
- Comments are intentionally concise and placed where logic may be non-obvious.
- Menu flow is resilient to invalid inputs and continues running after input errors.

## 7) UML attributes/methods to Python implementation

This section provides direct traceability from UML design elements to implemented code.

- `Room` (`src/hotel/models/room.py`)
  - UML attributes -> `room_id`, `room_number`, `room_type`, `floor`, `capacity`, `base_nightly_rate`, `current_status`, `seasonal_multiplier`, `amenities`
  - UML methods -> `get_effective_rate()`, `is_available()`, `set_maintenance()`, `update_rate()`

- `User` (`src/hotel/models/user.py`)
  - UML attributes -> `user_id`, `full_name`, `email`, `password_hash`, `phone`, `role`, `created_at`, `is_active`
  - UML methods -> `login()`, `logout()`, `update_profile()`, `get_role()`, `reset_password()`, abstract `has_permission()`

- `Guest` (`src/hotel/models/guest.py`)
  - UML attributes -> `loyalty_points`, `membership_tier`, `preferred_room_type`, `id_verified`, `nationality`, `bookings`
  - UML methods -> role-specific `has_permission()`, `redeem_points()`
  - Booking/search behavior is executed through `HotelSystem` service methods used by the console and frontend flows.

- `Staff` (`src/hotel/models/staff.py`)
  - UML attributes -> `staff_id`, `department`, `shift`, `employed_since`, `managed_rooms`, `access_level`
  - UML methods -> role-specific `has_permission()` with access-level gating
  - Operational staff actions are implemented through `HotelSystem` methods (booking approval/denial, maintenance-related actions).

- `SuperAdmin` (`src/hotel/models/super_admin.py`)
  - UML attributes -> `system_permissions`, `audit_log_access`, `override_enabled`, `managed_staff`, `report_recipient`
  - UML methods -> unrestricted `has_permission()` and admin actions routed via `HotelSystem` (report generation, pricing and control operations).

- `Booking` (`src/hotel/models/booking.py`)
  - UML attributes -> `booking_id`, `guest_id`, `room_id`, `check_in_date`, `check_out_date`, `status`, `services`, `total_charges`, `deposit_paid`, `notes`, `created_by`, `modified_at`
  - UML methods -> `compute_charges()`, `validate_overlap()`, `add_service()`, `modify()`, `cancel()`, `generate_invoice()`
  - Additional helper for date-range logic -> `overlaps()`

- `Service` (`src/hotel/models/service.py`)
  - UML attributes -> `service_id`, `name`, `category`, `unit_price`, `quantity`, `applied_date`
  - UML methods -> `get_total_cost()`, `apply_discount()`, `get_category()`, `get_description()`, `is_available()`

- `HotelSystem` (`src/hotel/hotel_system.py`)
  - UML attributes -> `rooms`, `users`, `bookings`, `services`, `current_season`
  - UML methods -> `search_rooms()`, `create_booking()`, `generate_report()`, `get_instance()`, `apply_seasonal_pricing()`, `authenticate()`
  - Extended manager operations required by menu/task flow -> update/cancel/complete booking, booking approval/denial, user history retrieval, room lifecycle refresh.

- `Report` (`src/hotel/models/report.py`)
  - UML attributes -> `report_id`, `report_type`, `generated_at`, `generated_by`, `period`, `data`
  - UML methods -> `generate()`, `export()`, `get_occupancy_rate()`, `get_revenue_summary()`
