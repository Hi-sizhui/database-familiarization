from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dbfamiliarity import Familiarizer, SQLiteProfiler

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/public/chinook/chinook_fixture.sqlite"
OUT = ROOT / "results/familiarization_oracle.csv"


@dataclass(frozen=True)
class Task:
    name: str
    required_columns: tuple[tuple[str, str], ...] = ()
    required_joins: tuple[tuple[str, str, str, str], ...] = ()


TASKS = [
    Task("track_title_samples", (("Track","Name"),)),
    Task("artist_names", (("Artist","Name"),)),
    Task("genre_names", (("Genre","Name"),)),
    Task("customer_countries", (("Customer","Country"),)),
    Task("invoice_totals", (("Invoice","Total"),)),
    Task("track_prices", (("Track","UnitPrice"),)),
    Task("track_duration", (("Track","Milliseconds"),)),
    Task("employee_titles", (("Employee","Title"),)),
    Task("media_types", (("MediaType","Name"),)),
    Task("playlist_names", (("Playlist","Name"),)),
    Task("artist_album", (("Artist","Name"),("Album","Title")), (("Album","ArtistId","Artist","ArtistId"),)),
    Task("album_tracks", (("Album","Title"),("Track","Name")), (("Track","AlbumId","Album","AlbumId"),)),
    Task("track_genre", (("Track","Name"),("Genre","Name")), (("Track","GenreId","Genre","GenreId"),)),
    Task("track_media", (("Track","Name"),("MediaType","Name")), (("Track","MediaTypeId","MediaType","MediaTypeId"),)),
    Task("customer_invoice", (("Customer","Country"),("Invoice","Total")), (("Invoice","CustomerId","Customer","CustomerId"),)),
    Task("invoice_lines", (("Invoice","Total"),("InvoiceLine","Quantity")), (("InvoiceLine","InvoiceId","Invoice","InvoiceId"),)),
    Task("line_track", (("InvoiceLine","Quantity"),("Track","Name")), (("InvoiceLine","TrackId","Track","TrackId"),)),
    Task("playlist_track", (("Playlist","Name"),("Track","Name")), (("PlaylistTrack","PlaylistId","Playlist","PlaylistId"),("PlaylistTrack","TrackId","Track","TrackId"))),
    Task("album_track_genre", (("Album","Title"),("Track","Name"),("Genre","Name")), (("Track","AlbumId","Album","AlbumId"),("Track","GenreId","Genre","GenreId"))),
    Task("customer_spend", (("Customer","Country"),("Invoice","Total")), (("Invoice","CustomerId","Customer","CustomerId"),)),
    Task("rock_playlist", (("Playlist","Name"),("Track","Name")), (("PlaylistTrack","PlaylistId","Playlist","PlaylistId"),("PlaylistTrack","TrackId","Track","TrackId"),("Track","GenreId","Genre","GenreId"))),
    Task("sales_by_artist", (("Artist","Name"),("InvoiceLine","Quantity")), (("InvoiceLine","TrackId","Track","TrackId"),("Track","AlbumId","Album","AlbumId"),("Album","ArtistId","Artist","ArtistId"))),
    Task("invoice_date_totals", (("Invoice","InvoiceDate"),("Invoice","Total"))),
    Task("track_composer", (("Track","Composer"),)),
]


def covered(mem, task: Task) -> bool:
    return all(mem.has_column_fact(t, c) for t, c in task.required_columns) and all(
        mem.has_join(*j) for j in task.required_joins
    )


def main():
    profiler = SQLiteProfiler(DB)
    budgets = [0, 4, 8, 12, 16, 24, 32, 40, 48]
    rows = []
    for policy in ("random", "round_robin", "adaptive"):
        for budget in budgets:
            scores = []
            last_mem = None
            for seed in range(10):
                last_mem = Familiarizer(profiler, policy=policy, seed=seed).run(budget).freeze()
                scores.append(sum(covered(last_mem, t) for t in TASKS) / len(TASKS))
            rows.append({
                "policy": policy,
                "budget": budget,
                "mean_task_coverage": round(statistics.mean(scores), 4),
                "std": round(statistics.stdev(scores), 4),
                "tasks": len(TASKS),
                "memory_columns": len(last_mem.empirical),
                "memory_joins": len(last_mem.relations),
            })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(OUT)
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
