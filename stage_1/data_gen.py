"""Generated parking data: static content for vector DB and dynamic data for SQLite."""

# Static content: general info, location, booking process (for RAG / vector store)
STATIC_DOCS = [
    {
        "content": """Parking "Central Garage" is a covered multi-level parking facility in the city center.
Address: 123 Main Street. Entrance from Oak Avenue. GPS: 52.1234, 21.5678.
Nearest landmarks: City Hall (200 m), Central Station (500 m).""",
        "source": "location",
    },
    {
        "content": """General information: Central Garage offers 450 parking spaces on 3 levels (B1, B2, B3).
Facilities: CCTV, barrier at entry/exit, disabled spaces on each level, EV charging stations (10 points).
Security: 24/7 surveillance and patrol.""",
        "source": "general",
    },
    {
        "content": """Booking process: To reserve a space, provide your full name, surname, car registration number, and desired reservation period (start and end date/time).
Reservations are subject to administrator confirmation. You will receive a confirmation or refusal.
Payment is due on arrival; we accept card and cash.""",
        "source": "booking",
    },
    {
        "content": """Parking space types: Standard (regular vehicles), Wide (SUVs, minivans), Disabled (with valid permit), EV (electric vehicle charging).
Space numbering: Level B1 (1–150), B2 (151–300), B3 (301–450).""",
        "source": "parking_details",
    },
    {
        "content": """Cancellation policy: Free cancellation up to 2 hours before the reserved start time.
Late cancellations may incur a fee. No-shows are charged one hour at the standard rate.""",
        "source": "policies",
    },
]

# Dynamic data: filled into SQLite (availability, working hours, prices)
def get_dynamic_fixture():
    """Working hours, prices, and initial availability (generated)."""
    return {
        "working_hours": [
            {"day": "Monday", "open": "06:00", "close": "23:00"},
            {"day": "Tuesday", "open": "06:00", "close": "23:00"},
            {"day": "Wednesday", "open": "06:00", "close": "23:00"},
            {"day": "Thursday", "open": "06:00", "close": "23:00"},
            {"day": "Friday", "open": "06:00", "close": "00:00"},
            {"day": "Saturday", "open": "08:00", "close": "00:00"},
            {"day": "Sunday", "open": "08:00", "close": "22:00"},
        ],
        "prices": [
            {"type": "standard", "first_hour": 5.00, "next_hours": 2.50, "day_max": 25.00},
            {"type": "wide", "first_hour": 7.00, "next_hours": 3.50, "day_max": 35.00},
            {"type": "ev", "first_hour": 6.00, "next_hours": 3.00, "day_max": 30.00},
        ],
        "availability": [
            # Sample: space_id, date, hour_slot, available (1=free, 0=taken)
            # We'll generate a small grid for "today" and "tomorrow"
        ],
    }
