from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("tourism_demo.db")


def main() -> None:
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE city (
            city_id INTEGER PRIMARY KEY,
            city_name TEXT NOT NULL,
            province TEXT NOT NULL
        );

        CREATE TABLE tourism_monthly (
            city_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            inbound_visitors INTEGER NOT NULL,
            total_visitors INTEGER NOT NULL,
            tourism_revenue REAL NOT NULL,
            FOREIGN KEY (city_id) REFERENCES city(city_id)
        );

        CREATE TABLE indicator_definition (
            indicator_code TEXT PRIMARY KEY,
            indicator_name TEXT NOT NULL,
            unit TEXT NOT NULL,
            definition_text TEXT NOT NULL,
            valid_from TEXT NOT NULL
        );
        """
    )
    conn.executemany(
        "INSERT INTO city(city_id, city_name, province) VALUES (?, ?, ?)",
        [(1, "Hangzhou", "Zhejiang"), (2, "Ningbo", "Zhejiang"),
         (3, "Jinhua", "Zhejiang"), (4, "Wenzhou", "Zhejiang")],
    )
    rows = []
    for year in (2024, 2025):
        for month in (1, 2, 3, 4):
            base = 10000 if year == 2024 else 12000
            for city_id, multiplier in [(1, 1.25), (2, 1.05), (3, 0.9), (4, 0.98)]:
                inbound = int(base * multiplier * (1 + 0.03 * month))
                total = int(inbound * 3.6)
                revenue = round(total * 0.0025, 2)
                rows.append((city_id, year, month, inbound, total, revenue))
    conn.executemany(
        "INSERT INTO tourism_monthly(city_id, year, month, inbound_visitors, total_visitors, tourism_revenue) VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.executemany(
        "INSERT INTO indicator_definition(indicator_code, indicator_name, unit, definition_text, valid_from) VALUES (?, ?, ?, ?, ?)",
        [
            ("INBOUND_VISITORS", "Inbound visitors", "person-visits",
             "Visitors entering the destination under the current inbound tourism statistical definition.", "2024-01-01"),
            ("TOTAL_VISITORS", "Total visitors", "person-visits",
             "All recorded visitor arrivals covered by the tourism statistics system.", "2024-01-01"),
        ],
    )
    conn.commit()
    conn.close()
    print(f"Created {DB}")


if __name__ == "__main__":
    main()
