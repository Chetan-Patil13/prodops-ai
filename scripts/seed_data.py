# scripts/seed_data.py

import random
from datetime import datetime, timedelta
import os

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()


USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

if not all([USER, PASSWORD, HOST, PORT, DBNAME]):
    raise RuntimeError("One or more DB environment variables are missing")

DATABASE_URL = (
    f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    "?sslmode=require"
)

engine = create_engine(DATABASE_URL)

# ------------------------
# Helpers
# ------------------------

def execute(sql, params=None):
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})


def fetch_one(sql, params=None):
    with engine.connect() as conn:
        return conn.execute(text(sql), params or {}).mappings().first()


# ------------------------
# Seed Roles
# ------------------------

def seed_roles():
    roles = [
        "ADMIN",
        "SUPERVISOR",
        "MAINTENANCE_HEAD",
        "PLANT_MANAGER",
    ]
    for role in roles:
        execute(
            "INSERT INTO roles (role_name) VALUES (:r) ON CONFLICT DO NOTHING",
            {"r": role},
        )


# ------------------------
# Seed Users
# ------------------------

def seed_users():
    users = [
        ("admin@prodops.ai", "Admin User"),
        ("supervisor1@prodops.ai", "Supervisor One"),
        ("supervisor2@prodops.ai", "Supervisor Two"),
        ("maintenance@prodops.ai", "Maintenance Head"),
        ("manager@prodops.ai", "Plant Manager"),
    ]

    for email, name in users:
        execute(
            """
            INSERT INTO users (user_email, full_name)
            VALUES (:email, :name)
            ON CONFLICT (user_email) DO NOTHING
            """,
            {"email": email, "name": name},
        )


def assign_roles():
    mapping = {
        "admin@prodops.ai": "ADMIN",
        "supervisor1@prodops.ai": "SUPERVISOR",
        "supervisor2@prodops.ai": "SUPERVISOR",
        "maintenance@prodops.ai": "MAINTENANCE_HEAD",
        "manager@prodops.ai": "PLANT_MANAGER",
    }

    for email, role in mapping.items():
        execute(
            """
            INSERT INTO user_roles (user_id, role_id)
            SELECT u.id, r.id
            FROM users u, roles r
            WHERE u.user_email = :email AND r.role_name = :role
            ON CONFLICT DO NOTHING
            """,
            {"email": email, "role": role},
        )


# ------------------------
# Seed Plant, Lines, Machines
# ------------------------

def seed_structure():
    execute(
        """
        INSERT INTO plants (plant_code, plant_name, location)
        VALUES ('PLANT-01', 'Main Manufacturing Plant', 'India')
        ON CONFLICT DO NOTHING
        """
    )

    execute(
        """
        INSERT INTO production_lines (line_code, line_name, plant_id)
        SELECT 'LINE-1', 'Casting Line 1', id FROM plants
        ON CONFLICT DO NOTHING
        """
    )

    execute(
        """
        INSERT INTO production_lines (line_code, line_name, plant_id)
        SELECT 'LINE-2', 'Casting Line 2', id FROM plants
        ON CONFLICT DO NOTHING
        """
    )

    lines = fetch_one("SELECT id FROM production_lines WHERE line_code='LINE-1'")
    if not lines:
        return

    for line_code in ["LINE-1", "LINE-2"]:
        for i in range(1, 4):
            execute(
                """
                INSERT INTO machines (machine_code, machine_name, line_id, machine_type)
                SELECT :mc, :mn, id, 'PRESS'
                FROM production_lines WHERE line_code=:lc
                ON CONFLICT DO NOTHING
                """,
                {
                    "mc": f"{line_code}-MC-{i}",
                    "mn": f"{line_code} Machine {i}",
                    "lc": line_code,
                },
            )


# ------------------------
# Seed Production Logs
# ------------------------

def seed_production_logs():
    today = datetime.utcnow().date()

    for day_offset in range(30):
        day = today - timedelta(days=day_offset)

        for shift in ["A", "B", "C"]:
            for line_code in ["LINE-1", "LINE-2"]:
                qty_good = random.randint(350, 420)
                qty_reject = random.randint(5, 20)

                execute(
                    """
                    INSERT INTO production_log
                    (line_id, event_time, shift_code, quantity_good, quantity_reject)
                    SELECT id, :time, :shift, :good, :reject
                    FROM production_lines WHERE line_code=:lc
                    """,
                    {
                        "time": day + timedelta(hours=random.randint(6, 22)),
                        "shift": shift,
                        "good": qty_good,
                        "reject": qty_reject,
                        "lc": line_code,
                    },
                )


# ------------------------
# Seed Downtime Logs
# ------------------------

def seed_downtime_logs():
    reasons = [
        ("HYD", "Hydraulic pressure low", "Breakdown"),
        ("ELEC", "Electrical fault", "Breakdown"),
        ("CHG", "Changeover", "Planned"),
        ("MAT", "Material shortage", "Unplanned"),
    ]

    today = datetime.utcnow().date()

    for day_offset in range(15):
        day = today - timedelta(days=day_offset)

        for line_code in ["LINE-1", "LINE-2"]:
            reason = random.choice(reasons)
            duration = random.randint(10, 45)

            start = datetime.combine(day, datetime.min.time()) + timedelta(hours=10)
            end = start + timedelta(minutes=duration)

            execute(
                """
                INSERT INTO downtime_log
                (line_id, start_time, end_time, reason_code, reason_text, category)
                SELECT id, :start, :end, :rc, :rt, :cat
                FROM production_lines WHERE line_code=:lc
                """,
                {
                    "start": start,
                    "end": end,
                    "rc": reason[0],
                    "rt": reason[1],
                    "cat": reason[2],
                    "lc": line_code,
                },
            )


# ------------------------
# Seed Tickets
# ------------------------

def seed_tickets():
    creator = fetch_one("SELECT id FROM users WHERE user_email='supervisor1@prodops.ai'")
    if not creator:
        return

    for i in range(5):
        execute(
            """
            INSERT INTO tickets
            (ticket_no, ticket_type, line_id, issue_summary, severity, status, created_by)
            SELECT
                :tno, 'Maintenance', id, 'Hydraulic issue detected',
                'High', 'OPEN', :uid
            FROM production_lines
            WHERE line_code='LINE-1'
            """,
            {
                "tno": f"MNT-{1000+i}",
                "uid": creator["id"],
            },
        )


# ------------------------
# MAIN
# ------------------------

def main():
    print("Seeding database...")
    seed_roles()
    seed_users()
    assign_roles()
    seed_structure()
    seed_production_logs()
    seed_downtime_logs()
    seed_tickets()
    print("Seeding complete.")


if __name__ == "__main__":
    main()
