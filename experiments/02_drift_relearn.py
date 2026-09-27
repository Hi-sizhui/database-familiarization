from pathlib import Path
import shutil
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dbfamiliarity import Familiarizer, SQLiteProfiler
from dbfamiliarity.core import detect_drift, targeted_relearn

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/public/chinook/chinook_fixture.sqlite"
DRIFTED = ROOT / "results/chinook_drifted.sqlite"
MEMORY = ROOT / "results/adaptive_memory_frozen.json"


def main():
    DRIFTED.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BASE, DRIFTED)
    conn = sqlite3.connect(DRIFTED)
    conn.execute("UPDATE Genre SET Name='Classic Rock' WHERE GenreId=1")
    conn.commit()
    conn.close()

    mem = Familiarizer(SQLiteProfiler(BASE), policy="adaptive", seed=7).run(24).freeze()
    mem.to_json(MEMORY)

    frozen = type(mem).from_json(MEMORY)
    drift = detect_drift(frozen, SQLiteProfiler(DRIFTED))
    action_count_before = len(frozen.actions)
    frozen, refreshed = targeted_relearn(frozen, SQLiteProfiler(DRIFTED), drift)
    action_count_after = len(frozen.actions)

    print("frozen_memory:", MEMORY)
    print("structural_changed:", drift["structural_changed"])
    print("empirical_changed:", drift["empirical_changed"])
    print("targeted_refresh_probes:", refreshed)
    print("onboarding_log_unchanged:", action_count_before == action_count_after)
    print("new_Genre.Name_sample:", frozen.empirical["Genre.Name"].sample_values)


if __name__ == "__main__":
    main()
